import os
from typing import List
from uuid import UUID

import httpx
import models
from database import get_db
from dotenv import load_dotenv
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, ConfigDict
from security import get_current_user
from sqlalchemy.orm import Session

load_dotenv()

# ==========================================
# CONFIGURAÇÃO DOS ENDPOINTS DO SUPABASE
# ==========================================
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")  # <--- ADICIONADO A ANON KEY

router = APIRouter(prefix="/api/v1/membros", tags=["Equipe e Membros"])


# ==========================================
# SCHEMAS LOCAIS (Pydantic)
# ==========================================
class ProfileCreate(BaseModel):
    name: str
    email: str
    role: str


class ProfileResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    name: str
    email: str
    role: str


# ==========================================
# DEPENDÊNCIA DE SEGURANÇA (RBAC)
# ==========================================
def verificar_admin(
    db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)
):
    """Verifica se o usuário logado tem permissão de 'admin'."""
    user_id = current_user.get("user_id")

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Não foi possível identificar o ID do usuário no token.",
        )

    usuario = db.query(models.Profile).filter(models.Profile.id == user_id).first()

    if not usuario or usuario.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado. Apenas administradores podem gerenciar a equipe.",
        )
    return current_user


# ==========================================
# ROTAS
# ==========================================
@router.get("", response_model=List[ProfileResponse])
def listar_membros(
    db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)
):
    tenant_id = current_user.get("tenant_id")
    membros = db.query(models.Profile).filter(models.Profile.tenant_id == tenant_id).all()
    return membros


@router.post("", response_model=ProfileResponse, status_code=status.HTTP_201_CREATED)
def adicionar_membro(
    membro_in: ProfileCreate,
    db: Session = Depends(get_db),
    admin_user: dict = Depends(verificar_admin),
):
    tenant_id = admin_user.get("tenant_id")

    # 1. Verifica no banco se o e-mail já existe
    existe = db.query(models.Profile).filter(models.Profile.email == membro_in.email).first()
    if existe:
        raise HTTPException(
            status_code=400, detail="Este e-mail já está cadastrado no sistema."
        )

    # 2. Prepara as variáveis para a API do Supabase
    url_invite = f"{SUPABASE_URL.rstrip('/')}/auth/v1/invite"
    headers = {
        "apikey": SUPABASE_SERVICE_KEY,
        "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
        "Content-Type": "application/json"
    }
    
    frontend_url = os.getenv("FRONTEND_URL", "http://localhost:5173")

    payload_invite = {
    "email": membro_in.email,
    "data": {
        "name": membro_in.name,
        "tenant_id": str(tenant_id)
    },
    "redirect_to": f"{frontend_url}/redefinir-senha"
    }
    

    try:
        with httpx.Client() as client:
            # Chama o endpoint de Convite Oficial
            response = client.post(url_invite, json=payload_invite, headers=headers)

            if response.status_code not in [200, 201]:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Erro no Supabase Auth: {response.text}"
                )

            dados_supabase = response.json()
            novo_user_id = dados_supabase.get("id")

        if not novo_user_id:
            raise HTTPException(status_code=500, detail="Supabase não retornou o ID do novo usuário.")

        # 3. Busca o perfil que a sua Trigger do banco criou automaticamente
        db.expire_all()
        perfil_criado = db.query(models.Profile).filter(models.Profile.id == novo_user_id).first()

        if perfil_criado:
            perfil_criado.name = membro_in.name  # type: ignore
            perfil_criado.role = membro_in.role  # type: ignore
            perfil_criado.tenant_id = tenant_id  # type: ignore
            db.commit()
            db.refresh(perfil_criado)
            return perfil_criado
        else:
            # FALLBACK: Caso a trigger não exista, cria o perfil manualmente
            try:
                novo_perfil = models.Profile(
                    id=novo_user_id,
                    name=membro_in.name,  # type: ignore
                    email=membro_in.email,
                    role=membro_in.role,  # type: ignore
                    tenant_id=tenant_id   # type: ignore
                )
                db.add(novo_perfil)
                db.commit()
                db.refresh(novo_perfil)
                return novo_perfil
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Convite enviado, mas falha ao criar Profile local: {str(e)}")

    except httpx.RequestError as e:
        raise HTTPException(status_code=500, detail=f"Falha de rede ao conectar com o Supabase: {str(e)}")


@router.delete("/{membro_id}", status_code=status.HTTP_204_NO_CONTENT)
def remover_membro(
    membro_id: UUID,
    db: Session = Depends(get_db),
    admin_user: dict = Depends(verificar_admin),
):
    tenant_id = admin_user.get("tenant_id")

    membro = (
        db.query(models.Profile)
        .filter(models.Profile.id == membro_id, models.Profile.tenant_id == tenant_id)
        .first()
    )
    if not membro:
        raise HTTPException(status_code=404, detail="Membro não encontrado.")

    if str(membro.id) == admin_user.get("user_id"):
        raise HTTPException(
            status_code=400, detail="Você não pode excluir sua própria conta."
        )

    db.delete(membro)
    db.commit()
    return None