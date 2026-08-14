from uuid import UUID

import models
from fastapi import HTTPException, status
from sqlalchemy import or_
from sqlalchemy.orm import Query, Session

MANAGEMENT_ROLES = {"admin", "gerente"}


def has_management_access(current_user: dict) -> bool:
    return current_user.get("role") in MANAGEMENT_ROLES


def require_management_access(current_user: dict) -> None:
    if not has_management_access(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas administradores e gerentes podem realizar esta ação.",
        )


def apply_client_scope(query: Query, current_user: dict) -> Query:
    """Limita colaboradores à própria carteira, mantendo não atribuídos visíveis."""
    if has_management_access(current_user):
        return query
    return query.filter(
        or_(
            models.Client.responsible_profile_id.is_(None),
            models.Client.responsible_profile_id == current_user["user_id"],
        )
    )


def apply_task_scope(query: Query, current_user: dict) -> Query:
    if has_management_access(current_user):
        return query
    return query.join(
        models.Client,
        (models.Task.client_id == models.Client.id)
        & (models.Task.tenant_id == models.Client.tenant_id),
    ).filter(
        or_(
            models.Client.responsible_profile_id.is_(None),
            models.Client.responsible_profile_id == current_user["user_id"],
        )
    )


def get_accessible_client(
    db: Session, client_id: UUID, current_user: dict, *, active_only: bool = False
) -> models.Client:
    query = db.query(models.Client).filter(
        models.Client.id == client_id,
        models.Client.tenant_id == current_user["tenant_id"],
    )
    if active_only:
        query = query.filter(models.Client.ativo.is_(True))
    client = apply_client_scope(query, current_user).first()
    if not client:
        raise HTTPException(status_code=404, detail="Cliente não encontrado.")
    return client


def validate_responsible_profile(
    db: Session, tenant_id: str, profile_id: UUID | None
) -> models.Profile | None:
    if profile_id is None:
        return None
    profile = (
        db.query(models.Profile)
        .filter(
            models.Profile.id == profile_id,
            models.Profile.tenant_id == tenant_id,
        )
        .first()
    )
    if not profile:
        raise HTTPException(
            status_code=404,
            detail="Responsável não encontrado neste escritório.",
        )
    return profile

