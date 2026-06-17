import os
from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from dotenv import load_dotenv
import httpx # <-- Usaremos o HTTPX para isolar a chamada de segurança

# Banco de Dados e Segurança locais
from database import get_db
from security import get_current_user
import models
from pydantic import BaseModel, ConfigDict

load_dotenv()

# ==========================================
# CONFIGURAÇÃO DOS ENDPOINTS DO SUPABASE
# ==========================================
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

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
def verificar_admin(db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    """Verifica se o usuário logado tem permissão de 'admin'."""
    user_id = current_user.get("user_id") # <--- CORRIGIDO AQUI
    
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Não foi possível identificar o ID do usuário no token."
        )

    usuario = db.query(models.Profile).filter(models.Profile.id == user_id).first()
    
    if not usuario or usuario.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Acesso negado. Apenas administradores podem gerenciar a equipe."
        )
    return current_user

# ==========================================
# ROTAS
# ==========================================
@router.get("", response_model=List[ProfileResponse])
def listar_membros(db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    tenant_id = current_user.get("tenant_id")
    membros = db.query(models.Profile).filter(models.Profile.tenant_id == tenant_id).all()
    return membros

@router.post("", response_model=ProfileResponse, status_code=status.HTTP_201_CREATED)
def adicionar_membro(
    membro_in: ProfileCreate, 
    db: Session = Depends(get_db), 
    admin_user: dict = Depends(verificar_admin)
):
    tenant_id = admin_user.get("tenant_id")
    
    # 1. Verifica no banco se o e-mail já existe
    existe = db.query(models.Profile).filter(models.Profile.email == membro_in.email).first()
    if existe:
        raise HTTPException(status_code=400, detail="Este e-mail já está cadastrado no sistema.")
        
    # 2. Cria o usuário diretamente no Supabase Auth via API Admin
    # Isso cria o usuário na hora, dispara a trigger do banco e retorna o ID dele
    url_create = f"{SUPABASE_URL.rstrip('/')}/auth/v1/admin/users"
    headers = {
        "apikey": SUPABASE_SERVICE_KEY,
        "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
        "Content-Type": "application/json"
    }
    payload_create = {
        "email": membro_in.email,
        "email_confirm": True, # Define como true para não exigir confirmação por email agora
        "user_metadata": {
            "name": membro_in.name,
            "tenant_id": str(tenant_id)
        }
    }

    try:
        with httpx.Client() as client:
            response = client.post(url_create, json=payload_create, headers=headers)
            
            if response.status_code not in [200, 201]:
                # Se der erro aqui, provavelmente é a SUPABASE_SERVICE_KEY incorreta
                raise HTTPException(
                    status_code=response.status_code, 
                    detail=f"Erro no Supabase Auth: {response.text}"
                )
            
            dados_supabase = response.json()
            novo_user_id = dados_supabase.get("id")

        if not novo_user_id:
            raise HTTPException(status_code=500, detail="Supabase não retornou o ID do novo usuário.")

        # 3. Busca o perfil que a sua Trigger do banco criou automaticamente
        # O expire_all garante que o SQLAlchemy leia os dados novos do banco
        db.expire_all()
        perfil_criado = db.query(models.Profile).filter(models.Profile.id == novo_user_id).first()
        
        if perfil_criado:
            # Sincroniza os campos que vieram do frontend
            perfil_criado.name = membro_in.name
            perfil_criado.role = membro_in.role
            perfil_criado.tenant_id = tenant_id
            db.commit()
            db.refresh(perfil_criado)
            try:
                url_recover = f"{SUPABASE_URL.rstrip('/')}/auth/v1/recover"
                headers = {
                    "apikey": SUPABASE_SERVICE_KEY,
                    "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
                    "Content-Type": "application/json"
                }
                payload_recover = {"email": membro_in.email}
                
                with httpx.Client() as client:
                    # Dispara o e-mail do Supabase para o usuário definir a senha
                    client.post(url_recover, json=payload_recover, headers=headers)
            except Exception as e:
                # Se o e-mail falhar, não trava o cadastro que já foi feito, apenas loga o erro
                print(f"Erro ao enviar e-mail de definição de senha: {e}")
            return perfil_criado
        else:
            # FALLBACK: Se a trigger não existir ou falhar, criamos o perfil manualmente aqui
            try:
                novo_perfil = models.Profile(
                    id=novo_user_id,
                    name=membro_in.name,
                    email=membro_in.email,
                    role=membro_in.role,
                    tenant_id=tenant_id
                )
                db.add(novo_perfil)
                db.commit()
                db.refresh(novo_perfil)
                return novo_perfil
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Usuário criado no Auth, mas falha ao criar Profile: {str(e)}")

    except httpx.RequestError as e:
        raise HTTPException(status_code=500, detail=f"Falha de rede ao conectar com o Supabase: {str(e)}")

@router.delete("/{membro_id}", status_code=status.HTTP_204_NO_CONTENT)
def remover_membro(
    membro_id: UUID, 
    db: Session = Depends(get_db), 
    admin_user: dict = Depends(verificar_admin)
):
    tenant_id = admin_user.get("tenant_id")
    
    membro = db.query(models.Profile).filter(models.Profile.id == membro_id, models.Profile.tenant_id == tenant_id).first()
    if not membro:
        raise HTTPException(status_code=404, detail="Membro não encontrado.")
        
    if str(membro.id) == admin_user.get("user_id"): # <--- CORRIGIDO AQUI
        raise HTTPException(status_code=400, detail="Você não pode excluir sua própria conta.")
        
    db.delete(membro)
    db.commit()
    return None