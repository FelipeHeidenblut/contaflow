import os
from typing import List
from uuid import UUID

import httpx
import models
from database import get_db
from dotenv import load_dotenv
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, ConfigDict, EmailStr, Field
from typing import Literal
from security import get_active_user, get_current_user
from sqlalchemy.orm import Session

load_dotenv()

# ==========================================
# CONFIGURAÇÃO DOS ENDPOINTS DO SUPABASE
# ==========================================
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")

router = APIRouter(prefix="/api/v1/membros", tags=["Equipe e Membros"])

# Limites de membros por plano
LIMITES_MEMBROS = {"free": 1, "basico": 5, "profissional": 10, "business": float("inf")}
NOMES_PLANOS = {
    "free": "Gratuito",
    "basico": "Essencial",
    "profissional": "Profissional",
    "business": "Empresarial",
}


# ==========================================
# SCHEMAS LOCAIS (Pydantic)
# ==========================================
class ProfileCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=150)
    email: EmailStr
    role: Literal["admin", "colaborador"]
    password: str = Field(..., min_length=8, max_length=72)


class ProfileResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    name: str
    email: str
    role: str


# ==========================================
# DEPENDÊNCIA DE SEGURANÇA (RBAC)
# ==========================================
def verificar_admin(current_user: dict = Depends(get_active_user)):
    """
    Verifica se o usuário logado tem permissão de 'admin'.
    Otimização: A role já vem no current_user (buscada no security.py), não precisamos de DB aqui.
    """
    if current_user.get("role") != "admin":
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
    membros = (
        db.query(models.Profile).filter(models.Profile.tenant_id == tenant_id).all()
    )
    return membros


@router.post("", response_model=ProfileResponse, status_code=status.HTTP_201_CREATED)
def adicionar_membro(
    membro_in: ProfileCreate,
    db: Session = Depends(get_db),
    admin_user: dict = Depends(verificar_admin),
):
    tenant_id = admin_user.get("tenant_id")
    
    tenant = db.query(models.Tenant).filter(models.Tenant.id == tenant_id).first()
    limite = LIMITES_MEMBROS.get(tenant.plano, 1)
    
    total_membros = db.query(models.Profile).filter(
        models.Profile.tenant_id == tenant_id
    ).count()
    
    if total_membros >= limite:
        raise HTTPException(
            status_code=403, 
            detail=f"Seu plano {NOMES_PLANOS.get(tenant.plano, tenant.plano)} permite apenas {limite} usuário(s). Faça upgrade para adicionar mais membros!"
        )

    # 1. Verifica no banco se o e-mail já existe
    existe = (
        db.query(models.Profile).filter(models.Profile.email == membro_in.email).first()
    )
    if existe:
        raise HTTPException(
            status_code=400, detail="Este e-mail já está cadastrado no sistema."
        )

    # 2. Cria o usuário direto no Supabase Auth
    url_create = f"{SUPABASE_URL.rstrip('/')}/auth/v1/admin/users"
    headers = {
        "apikey": SUPABASE_SERVICE_KEY,
        "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
        "Content-Type": "application/json",
    }
    payload_create = {
        "email": membro_in.email,
        "password": membro_in.password,
        "email_confirm": True,
        "user_metadata": {"name": membro_in.name, "tenant_id": str(tenant_id)},
    }

    try:
        with httpx.Client(timeout=10.0) as client:
            response = client.post(url_create, json=payload_create, headers=headers)

            if response.status_code not in [200, 201]:
                raise HTTPException(
                    status_code=502,
                    detail="Não foi possível criar o usuário no provedor de autenticação.",
                )

            dados_supabase = response.json()
            novo_user_id = dados_supabase.get("id")

        if not novo_user_id:
            raise HTTPException(
                status_code=500, detail="Supabase não retornou o ID do novo usuário."
            )

        # 3. Busca o perfil que a sua Trigger do banco criou automaticamente
        db.expire_all()
        perfil_criado = (
            db.query(models.Profile).filter(models.Profile.id == novo_user_id).first()
        )

        if perfil_criado:
            perfil_criado.name = membro_in.name  # type: ignore
            perfil_criado.role = membro_in.role  # type: ignore
            perfil_criado.tenant_id = tenant_id  # type: ignore
            db.commit()
            db.refresh(perfil_criado)
            return perfil_criado
        else:
            # FALLBACK
            try:
                novo_perfil = models.Profile(
                    id=novo_user_id,
                    name=membro_in.name,  # type: ignore
                    email=membro_in.email,
                    role=membro_in.role,  # type: ignore
                    tenant_id=tenant_id,  # type: ignore
                )
                db.add(novo_perfil)
                db.commit()
                db.refresh(novo_perfil)
                return novo_perfil
            except Exception as e:
                raise HTTPException(
                    status_code=500,
                    detail="Usuário criado no provedor, mas o perfil local não pôde ser concluído.",
                )

    except httpx.RequestError as e:
        raise HTTPException(
            status_code=500,
            detail="Falha de comunicação com o provedor de autenticação.",
        )


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

    # ==========================================
    # CORREÇÃO: Apagar o usuário do Supabase Auth também!
    # ==========================================
    user_id_str = str(membro.id)
    url_delete = f"{SUPABASE_URL.rstrip('/')}/auth/v1/admin/users/{user_id_str}"
    headers = {
        "apikey": SUPABASE_SERVICE_KEY,
        "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
    }

    try:
        with httpx.Client(timeout=10.0) as client:
            # Faz a requisição DELETE para o Supabase
            response = client.delete(url_delete, headers=headers)
            
            # Se o Supabase devolver 200, 204 ou 404 (já apagado), podemos prosseguir.
            # Se devolver outro erro, precisamos abortar para não ficar órfão.
            if response.status_code not in [200, 204, 404]:
                raise HTTPException(
                    status_code=500,
                    detail="Não foi possível remover o usuário do provedor de autenticação."
                )
    except httpx.RequestError as e:
        raise HTTPException(
            status_code=500,
            detail="Falha de comunicação com o provedor de autenticação."
        )

    # Agora sim, apaga o perfil do banco de dados local
    db.delete(membro)
    db.commit()
    return None
