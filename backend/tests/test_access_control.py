import os
import sys
from types import SimpleNamespace
from uuid import uuid4

import pytest
from fastapi import HTTPException
from pydantic import ValidationError

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import models
from access_control import (
    Permission,
    TenantContext,
    has_management_access,
    has_permission,
    require_management_access,
    tenant_repository,
)
from comentarios import CommentCreate


def make_user(role: str, tenant_id=None, user_id=None):
    return {
        "role": role,
        "tenant_id": str(tenant_id or uuid4()),
        "user_id": str(user_id or uuid4()),
    }


def test_admin_e_gerente_possuem_acesso_de_gestao():
    assert has_management_access(make_user("admin")) is True
    assert has_management_access(make_user("gerente")) is True
    assert has_management_access(make_user("colaborador")) is False


def test_colaborador_nao_recebe_permissao_de_gestao():
    with pytest.raises(HTTPException) as error:
        require_management_access(make_user("colaborador"))

    assert error.value.status_code == 403


def test_comentario_remove_espacos_e_rejeita_conteudo_vazio():
    payload = CommentCreate(client_id=uuid4(), content="  Observação interna  ")
    assert payload.content == "Observação interna"

    with pytest.raises(ValidationError):
        CommentCreate(client_id=uuid4(), content="   ")


def test_matriz_de_permissoes_diferencia_os_tres_papeis():
    collaborator = make_user("colaborador")
    manager = make_user("gerente")
    admin = make_user("admin")

    assert has_permission(collaborator, Permission.TASK_WRITE)
    assert not has_permission(collaborator, Permission.TASK_DELETE)
    assert has_permission(manager, Permission.TASK_DELETE)
    assert not has_permission(manager, Permission.MEMBER_MANAGE)
    assert has_permission(admin, Permission.MEMBER_MANAGE)
    assert has_permission(admin, Permission.BILLING_MANAGE)


def test_papel_desconhecido_falha_de_forma_fechada():
    with pytest.raises(HTTPException) as error:
        TenantContext.from_user(make_user("owner"))

    assert error.value.status_code == 403


class InMemoryTenantQuery:
    def __init__(self, resources):
        self.resources = list(resources)

    def filter(self, *conditions):
        for condition in conditions:
            column = getattr(getattr(condition, "left", None), "key", None)
            expected = getattr(getattr(condition, "right", None), "value", None)
            if column in {"id", "tenant_id"}:
                self.resources = [
                    resource
                    for resource in self.resources
                    if str(getattr(resource, column)) == str(expected)
                ]
        return self

    def first(self):
        return self.resources[0] if self.resources else None

    def all(self):
        return self.resources

    def with_for_update(self):
        return self


class InMemoryTenantDb:
    def __init__(self, resources_by_model):
        self.resources_by_model = resources_by_model

    def query(self, model):
        return InMemoryTenantQuery(self.resources_by_model.get(model, []))


@pytest.mark.parametrize(
    "model",
    [models.Client, models.Task, models.Document, models.Comment, models.Profile],
)
def test_repositorio_nao_expoe_recurso_de_outro_escritorio_mesmo_com_id(model):
    tenant_a = uuid4()
    tenant_b = uuid4()
    resource_a = SimpleNamespace(id=uuid4(), tenant_id=tenant_a)
    resource_b = SimpleNamespace(id=uuid4(), tenant_id=tenant_b)
    db = InMemoryTenantDb({model: [resource_a, resource_b]})
    repository = tenant_repository(db, make_user("admin", tenant_a))

    assert repository.query(model).all() == [resource_a]
    with pytest.raises(HTTPException) as error:
        repository.get(model, resource_b.id)

    assert error.value.status_code == 404
