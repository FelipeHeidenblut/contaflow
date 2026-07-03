import re
from uuid import UUID

import models
from database import get_db
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr, Field, field_validator
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

router = APIRouter(prefix="/api/v1/auth", tags=["Autenticação e Sincronização"])


# Schema Refatorado: Incluída validação rigorosa de Documento (Shift-Left)
class SincronizarCadastroSchema(BaseModel):
    supabase_user_id: UUID
    email: EmailStr
    nome_completo: str = Field(..., min_length=2, max_length=150)
    nome_escritorio: str = Field(..., min_length=2, max_length=150)
    documento: str = Field(..., description="CPF ou CNPJ contendo apenas números")

    @field_validator("documento")
    @classmethod
    def validar_documento(cls, v):
        # Limpa qualquer formatação residual que possa ter escapado do front-end
        v = re.sub(r"\D", "", v)

        if len(v) not in [11, 14]:
            raise ValueError(
                "Documento deve ser um CPF (11 dígitos) ou CNPJ (14 dígitos) válido."
            )

        return v


@router.post("/sincronizar-cadastro", status_code=status.HTTP_201_CREATED)
def sincronizar_cadastro(
    payload: SincronizarCadastroSchema, db: Session = Depends(get_db)
):

    # 1. Fail-Fast: Verifica duplicidade de usuário
    usuario_existente = (
        db.query(models.Profile).filter(models.Profile.email == payload.email).first()
    )
    if usuario_existente:
        return {
            "status": "ja_existente",
            "message": "Usuário já sincronizado no sistema local.",
            "tenant_id": usuario_existente.tenant_id,
        }

    # 2. Fail-Fast: Verifica duplicidade de CNPJ/CPF no Tenant (Garante integridade fiscal)
    tenant_existente = (
        db.query(models.Tenant).filter(models.Tenant.cnpj == payload.documento).first()
    )
    if tenant_existente:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Este CPF/CNPJ já está atrelado a outro escritório no sistema.",
        )

    try:
        # 3. Criação do Tenant (Inquilino SaaS)
        # O campo 'documento' é salvo na coluna 'cnpj' para manter compatibilidade com a modelagem existente[cite: 3, 5]
        novo_tenant = models.Tenant(
            razao_social=payload.nome_escritorio, cnpj=payload.documento
        )
        db.add(novo_tenant)
        db.flush()  # Gera o ID do Tenant para usarmos no Profile, mantendo a transação aberta

        # 4. Criação do Profile vinculado ao Tenant (Isolamento Multi-tenant)[cite: 5]
        novo_perfil = models.Profile(
            id=payload.supabase_user_id,
            tenant_id=novo_tenant.id,
            email=payload.email,
            name=payload.nome_completo,
            role="admin",  # Padrão RBAC: O criador do tenant é o admin[cite: 5]
        )
        db.add(novo_perfil)

        # 5. Commit final da transação
        db.commit()

        return {
            "status": "sucesso",
            "message": "Escritório e usuário sincronizados com sucesso!",
            "tenant_id": novo_tenant.id,
        }

    # Tratamento específico para erros de banco de dados[cite: 5]
    except IntegrityError as e:
        db.rollback()
        print(f"[IntegrityError] Falha na sincronização: {str(e.orig)}")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Conflito de dados: O registro já existe ou viola uma restrição do banco.",
        )

    # Fallback para erros genéricos[cite: 5]
    except Exception as e:
        db.rollback()
        print(f"[Exception] Erro inesperado na sincronização: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao persistir a estrutura do escritório.",
        )
