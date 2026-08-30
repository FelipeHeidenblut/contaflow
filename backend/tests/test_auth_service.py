from types import SimpleNamespace
from uuid import uuid4

import models
import pytest
from auth_service import (
    RegistrationCommand,
    resolve_user_context,
    synchronize_registration,
)
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError


class SequentialQuery:
    def __init__(self, value):
        self.value = value

    def join(self, *_args):
        return self

    def filter(self, *_args):
        return self

    def first(self):
        return self.value


class RegistrationDb:
    def __init__(self, query_results):
        self.query_results = iter(query_results)
        self.added = []
        self.commits = 0
        self.rollbacks = 0

    def query(self, *_entities):
        return SequentialQuery(next(self.query_results))

    def add(self, entity):
        self.added.append(entity)

    def flush(self):
        self.added[0].id = uuid4()

    def commit(self):
        self.commits += 1

    def rollback(self):
        self.rollbacks += 1


def test_sync_registration_creates_office_and_admin_in_one_transaction():
    database = RegistrationDb([None, None, None])
    user_id = uuid4()
    command = RegistrationCommand(
        user_id=user_id,
        email="admin@escritorio.test",
        full_name="Usuário Teste",
        office_name="Escritório Teste",
        document="52998224725",
    )

    result = synchronize_registration(database, command)

    tenant, profile = database.added
    assert isinstance(tenant, models.Tenant)
    assert isinstance(profile, models.Profile)
    assert profile.id == user_id
    assert profile.tenant_id == tenant.id
    assert profile.role == "admin"
    assert database.commits == 1
    assert database.rollbacks == 0
    assert result == {
        "status": "sucesso",
        "message": "Escritório e usuário sincronizados com sucesso!",
        "tenant_id": tenant.id,
    }


def test_sync_registration_is_idempotent_for_an_existing_profile():
    database = RegistrationDb([SimpleNamespace(id=uuid4())])
    command = RegistrationCommand(
        user_id=uuid4(),
        email="admin@escritorio.test",
        full_name="Usuário Teste",
        office_name="Escritório Teste",
        document="52998224725",
    )

    result = synchronize_registration(database, command)

    assert result == {
        "status": "ja_existente",
        "message": "Usuário já sincronizado no sistema local.",
    }
    assert database.added == []
    assert database.commits == 0


def test_sync_registration_rolls_back_database_conflicts():
    class ConflictingDb(RegistrationDb):
        def flush(self):
            raise IntegrityError("INSERT", {}, RuntimeError("duplicate"))

    database = ConflictingDb([None, None, None])
    command = RegistrationCommand(
        user_id=uuid4(),
        email="admin@escritorio.test",
        full_name="Usuário Teste",
        office_name="Escritório Teste",
        document="52998224725",
    )

    with pytest.raises(HTTPException) as error:
        synchronize_registration(database, command)

    assert error.value.status_code == 409
    assert database.commits == 0
    assert database.rollbacks == 1


def test_resolve_user_context_returns_profile_and_office_billing_context():
    tenant_id = uuid4()
    user_id = uuid4()
    profile = SimpleNamespace(
        id=user_id,
        tenant_id=tenant_id,
        role="admin",
        is_superadmin=False,
    )
    tenant = SimpleNamespace(
        plano="profissional",
        billing_cycle="annual",
        status_pagamento="ativo",
        subscription_status="active",
    )
    database = RegistrationDb([(profile, tenant)])

    result = resolve_user_context(
        database,
        {"sub": str(user_id), "email": "admin@escritorio.test"},
    )

    assert result == {
        "user_id": str(user_id),
        "email": "admin@escritorio.test",
        "tenant_id": str(tenant_id),
        "role": "admin",
        "is_superadmin": False,
        "plan": "profissional",
        "billing_cycle": "annual",
        "payment_status": "ativo",
        "subscription_status": "active",
    }
