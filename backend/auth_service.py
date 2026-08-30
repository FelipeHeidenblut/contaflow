from dataclasses import dataclass
from uuid import UUID

import models
from access_control import TenantContext
from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session


@dataclass(frozen=True, slots=True)
class RegistrationCommand:
    user_id: UUID
    email: str
    full_name: str
    office_name: str
    document: str


def synchronize_registration(db: Session, command: RegistrationCommand) -> dict:
    existing_profile = (
        db.query(models.Profile)
        .filter(models.Profile.id == command.user_id)
        .first()
    )
    if existing_profile:
        return {
            "status": "ja_existente",
            "message": "Usuário já sincronizado no sistema local.",
        }

    email_in_use = (
        db.query(models.Profile)
        .filter(models.Profile.email == command.email)
        .first()
    )
    if email_in_use:
        raise HTTPException(status_code=409, detail="E-mail associado a outra identidade.")

    document_in_use = (
        db.query(models.Tenant)
        .filter(models.Tenant.cnpj == command.document)
        .first()
    )
    if document_in_use:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Este CPF/CNPJ já está atrelado a outro escritório no sistema.",
        )

    try:
        tenant = models.Tenant(
            razao_social=command.office_name,
            cnpj=command.document,
        )
        db.add(tenant)
        db.flush()

        profile = models.Profile(
            id=command.user_id,
            tenant_id=tenant.id,
            email=command.email,
            name=command.full_name,
            role="admin",
        )
        db.add(profile)
        db.commit()
    except IntegrityError as error:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "Conflito de dados: O registro já existe ou viola uma "
                "restrição do banco."
            ),
        ) from error
    except Exception as error:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao persistir a estrutura do escritório.",
        ) from error

    return {
        "status": "sucesso",
        "message": "Escritório e usuário sincronizados com sucesso!",
        "tenant_id": tenant.id,
    }


def resolve_user_context(db: Session, token_payload: dict) -> dict:
    try:
        user_id = UUID(str(token_payload.get("sub")))
    except (TypeError, ValueError) as error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Identificador de usuário inválido.",
        ) from error

    resolved = (
        db.query(models.Profile, models.Tenant)
        .join(models.Tenant, models.Profile.tenant_id == models.Tenant.id)
        .filter(models.Profile.id == user_id)
        .first()
    )
    if not resolved:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "Perfil ou escritório não encontrado. "
                "Por favor, sincronize seu cadastro."
            ),
        )

    profile, tenant = resolved
    user = {
        "user_id": str(profile.id),
        "email": token_payload.get("email"),
        "tenant_id": str(profile.tenant_id),
        "role": str(profile.role or "").strip().lower(),
        "is_superadmin": profile.is_superadmin,
        "plan": tenant.plano,
        "billing_cycle": tenant.billing_cycle,
        "payment_status": tenant.status_pagamento,
        "subscription_status": tenant.subscription_status,
    }
    TenantContext.from_user(user)
    return user
