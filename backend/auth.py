from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from pydantic import BaseModel, EmailStr, Field
from uuid import UUID

from database import get_db
import models

router = APIRouter(
    prefix="/api/v1/auth",
    tags=["Autenticação e Sincronização"]
)

# Schema Refatorado: Adição de limites (Field) protege contra payloads maliciosos
class SincronizarCadastroSchema(BaseModel):
    supabase_user_id: UUID
    email: EmailStr
    nome_completo: str = Field(..., min_length=2, max_length=150)
    nome_escritorio: str = Field(..., min_length=2, max_length=150)

@router.post("/sincronizar-cadastro", status_code=status.HTTP_201_CREATED)
def sincronizar_cadastro(payload: SincronizarCadastroSchema, db: Session = Depends(get_db)):
    
    # 1. Fail-Fast: Verifica duplicidade antes de iniciar processamento pesado
    usuario_existente = db.query(models.Profile).filter(models.Profile.email == payload.email).first()
    if usuario_existente:
        # Se já existe, não precisa criar de novo! Apenas retornamos sucesso.
        return {
            "status": "ja_existente",
            "message": "Usuário já sincronizado no sistema local.",
            "tenant_id": usuario_existente.tenant_id
        }

    try:
        # 2. Criação do Tenant (Inquilino SaaS)
        # ATENÇÃO: A palavra 'razao_social' deve ser exatamente igual à coluna no seu models.py
        novo_tenant = models.Tenant(
            razao_social=payload.nome_escritorio
        )
        db.add(novo_tenant)
        db.flush() # Gera o ID do Tenant para usarmos no Profile, mantendo a transação aberta

        # 3. Criação do Profile vinculado ao Tenant (Isolamento Multi-tenant)
        novo_perfil = models.Profile(
            id=payload.supabase_user_id,
            tenant_id=novo_tenant.id,
            email=payload.email,
            name=payload.nome_completo,
            role="admin" # Padrão RBAC: O criador do tenant é o admin
        )
        db.add(novo_perfil)
        
        # 4. Commit final da transação
        db.commit()

        return {
            "status": "sucesso",
            "message": "Escritório e usuário sincronizados com sucesso!",
            "tenant_id": novo_tenant.id
        }

    # Tratamento específico para erros de banco de dados (ex: chaves duplicadas na hora do commit)
    except IntegrityError as e:
        db.rollback()
        # Logar o erro internamente em uma ferramenta de observabilidade (ex: Sentry/Datadog)
        print(f"[IntegrityError] Falha na sincronização: {str(e.orig)}")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, 
            detail="Conflito de dados: O registro já existe ou viola uma restrição do banco."
        )

    # Fallback para erros genéricos
    except Exception as e:
        db.rollback()
        print(f"[Exception] Erro inesperado na sincronização: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Erro interno ao persistir a estrutura do escritório."
        )