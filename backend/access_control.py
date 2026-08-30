from dataclasses import dataclass
from enum import StrEnum
from types import MappingProxyType
from typing import TypeVar
from uuid import UUID

import models
from fastapi import HTTPException, status
from sqlalchemy import or_
from sqlalchemy.orm import Query, Session


class Permission(StrEnum):
    CLIENT_READ = "client:read"
    CLIENT_MANAGE = "client:manage"
    TASK_READ = "task:read"
    TASK_WRITE = "task:write"
    TASK_DELETE = "task:delete"
    DOCUMENT_READ = "document:read"
    DOCUMENT_WRITE = "document:write"
    DOCUMENT_DELETE = "document:delete"
    COMMENT_READ = "comment:read"
    COMMENT_WRITE = "comment:write"
    COMMENT_DELETE_ANY = "comment:delete:any"
    REPORT_READ = "report:read"
    MEMBER_READ = "member:read"
    MEMBER_MANAGE = "member:manage"
    BILLING_MANAGE = "billing:manage"


_COLLABORATOR_PERMISSIONS = frozenset(
    {
        Permission.CLIENT_READ,
        Permission.TASK_READ,
        Permission.TASK_WRITE,
        Permission.DOCUMENT_READ,
        Permission.DOCUMENT_WRITE,
        Permission.COMMENT_READ,
        Permission.COMMENT_WRITE,
        Permission.REPORT_READ,
        Permission.MEMBER_READ,
    }
)
_MANAGER_PERMISSIONS = _COLLABORATOR_PERMISSIONS | {
    Permission.CLIENT_MANAGE,
    Permission.TASK_DELETE,
    Permission.DOCUMENT_DELETE,
    Permission.COMMENT_DELETE_ANY,
}
ROLE_PERMISSIONS = MappingProxyType(
    {
        "colaborador": _COLLABORATOR_PERMISSIONS,
        "gerente": frozenset(_MANAGER_PERMISSIONS),
        "admin": frozenset(
            _MANAGER_PERMISSIONS
            | {Permission.MEMBER_MANAGE, Permission.BILLING_MANAGE}
        ),
    }
)
MANAGEMENT_ROLES = frozenset({"admin", "gerente"})


@dataclass(frozen=True, slots=True)
class TenantContext:
    """Identidade autorizada resolvida pelo backend, nunca pelo payload da rota."""

    tenant_id: UUID
    user_id: UUID
    role: str
    is_superadmin: bool = False

    @classmethod
    def from_user(cls, current_user: dict) -> "TenantContext":
        try:
            tenant_id = UUID(str(current_user["tenant_id"]))
            user_id = UUID(str(current_user["user_id"]))
        except (KeyError, TypeError, ValueError) as error:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Contexto de acesso inválido.",
            ) from error

        role = str(current_user.get("role") or "").strip().lower()
        if role not in ROLE_PERMISSIONS:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Perfil sem papel de acesso válido.",
            )
        return cls(
            tenant_id=tenant_id,
            user_id=user_id,
            role=role,
            is_superadmin=bool(current_user.get("is_superadmin")),
        )

    def has(self, permission: Permission) -> bool:
        return permission in ROLE_PERMISSIONS[self.role]


ModelT = TypeVar("ModelT")


class TenantRepository:
    """Ponto único para consultas de modelos pertencentes a um escritório."""

    def __init__(self, db: Session, current_user: dict):
        self.db = db
        self.context = TenantContext.from_user(current_user)

    def query(self, model: type[ModelT]) -> Query:
        tenant_column = getattr(model, "tenant_id", None)
        if tenant_column is None:
            raise TypeError(f"{model.__name__} não é um recurso de organização.")
        return self.db.query(model).filter(tenant_column == self.context.tenant_id)

    def get(
        self,
        model: type[ModelT],
        resource_id: UUID,
        *,
        for_update: bool = False,
        detail: str = "Recurso não encontrado.",
    ) -> ModelT:
        query = self.query(model).filter(model.id == resource_id)
        if for_update:
            query = query.with_for_update()
        resource = query.first()
        if not resource:
            # 404 deliberado: não revela se o ID existe em outro escritório.
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail)
        return resource


def tenant_repository(db: Session, current_user: dict) -> TenantRepository:
    return TenantRepository(db, current_user)


def has_permission(current_user: dict, permission: Permission) -> bool:
    return TenantContext.from_user(current_user).has(permission)


def require_permission(
    current_user: dict,
    permission: Permission,
    *,
    detail: str = "Você não possui permissão para realizar esta ação.",
) -> None:
    if not has_permission(current_user, permission):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=detail)


def has_management_access(current_user: dict) -> bool:
    return has_permission(current_user, Permission.CLIENT_MANAGE)


def require_management_access(current_user: dict) -> None:
    require_permission(
        current_user,
        Permission.CLIENT_MANAGE,
        detail="Apenas administradores e gerentes podem realizar esta ação.",
    )


def apply_client_scope(query: Query, current_user: dict) -> Query:
    """Limita colaboradores à própria carteira, mantendo não atribuídos visíveis."""
    context = TenantContext.from_user(current_user)
    if context.has(Permission.CLIENT_MANAGE):
        return query
    return query.filter(
        or_(
            models.Client.responsible_profile_id.is_(None),
            models.Client.responsible_profile_id == context.user_id,
        )
    )


def apply_task_scope(query: Query, current_user: dict) -> Query:
    context = TenantContext.from_user(current_user)
    if context.has(Permission.CLIENT_MANAGE):
        return query
    return query.join(
        models.Client,
        (models.Task.client_id == models.Client.id)
        & (models.Task.tenant_id == models.Client.tenant_id),
    ).filter(
        or_(
            models.Client.responsible_profile_id.is_(None),
            models.Client.responsible_profile_id == context.user_id,
        )
    )


def get_accessible_client(
    db: Session, client_id: UUID, current_user: dict, *, active_only: bool = False
) -> models.Client:
    require_permission(current_user, Permission.CLIENT_READ)
    query = tenant_repository(db, current_user).query(models.Client).filter(
        models.Client.id == client_id
    )
    if active_only:
        query = query.filter(models.Client.ativo.is_(True))
    client = apply_client_scope(query, current_user).first()
    if not client:
        raise HTTPException(status_code=404, detail="Cliente não encontrado.")
    return client


def get_accessible_task(
    db: Session,
    task_id: UUID,
    current_user: dict,
    *,
    for_update: bool = False,
) -> models.Task:
    require_permission(current_user, Permission.TASK_READ)
    query = tenant_repository(db, current_user).query(models.Task).filter(
        models.Task.id == task_id
    )
    query = apply_task_scope(query, current_user)
    if for_update:
        query = query.with_for_update()
    task = query.first()
    if not task:
        raise HTTPException(status_code=404, detail="Tarefa não encontrada.")
    return task


def validate_responsible_profile(
    db: Session, current_user: dict, profile_id: UUID | None
) -> models.Profile | None:
    if profile_id is None:
        return None
    profile = (
        tenant_repository(db, current_user)
        .query(models.Profile)
        .filter(models.Profile.id == profile_id)
        .first()
    )
    if not profile:
        raise HTTPException(
            status_code=404,
            detail="Responsável não encontrado neste escritório.",
        )
    return profile
