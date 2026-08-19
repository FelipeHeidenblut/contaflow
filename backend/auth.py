import re
from uuid import UUID

import models
from database import get_db
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, ConfigDict, Field, field_validator
from security import get_current_user, verify_token
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

router = APIRouter(prefix="/api/v1/auth", tags=["Autenticação e Sincronização"])


# Schema Refatorado: Incluída validação rigorosa de Documento (Shift-Left)
class SincronizarCadastroSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")
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
    payload: SincronizarCadastroSchema,
    token_payload: dict = Depends(verify_token),
    db: Session = Depends(get_db),
):
    user_id = UUID(token_payload["sub"])
    email = token_payload.get("email")
    if not email:
        raise HTTPException(status_code=401, detail="Token sem e-mail.")

    usuario_existente = db.query(models.Profile).filter(models.Profile.id == user_id).first()
    if usuario_existente:
        return {
            "status": "ja_existente",
            "message": "Usuário já sincronizado no sistema local.",
        }
    if db.query(models.Profile).filter(models.Profile.email == email).first():
        raise HTTPException(status_code=409, detail="E-mail associado a outra identidade.")

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
            id=user_id,
            tenant_id=novo_tenant.id,
            email=email,
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
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Conflito de dados: O registro já existe ou viola uma restrição do banco.",
        )

    # Fallback para erros genéricos[cite: 5]
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao persistir a estrutura do escritório.",
        )


@router.get("/me", tags=["Autenticação e Sincronização"])
def get_me(
    current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)
):
    """Retorna os dados de permissão do usuário logado."""
    tenant = (
        db.query(models.Tenant)
        .filter(models.Tenant.id == current_user.get("tenant_id"))
        .first()
    )
    return {
        "user_id": current_user.get("user_id"),
        "role": current_user.get("role"),
        "is_superadmin": current_user.get("is_superadmin"),
        "tenant_id": current_user.get("tenant_id"),
        "plan": tenant.plano if tenant else "free",
        "billing_cycle": tenant.billing_cycle if tenant else "monthly",
        "payment_status": tenant.status_pagamento if tenant else "ativo",
    }
