import os
import sys
from types import SimpleNamespace
from uuid import uuid4

import pytest
from fastapi import HTTPException

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import models
from security import get_active_user, get_current_user


class IdentityQuery:
    def __init__(self, resolved):
        self.resolved = resolved

    def join(self, *_args):
        return self

    def filter(self, *_args):
        return self

    def first(self):
        return self.resolved


class IdentityDb:
    def __init__(self, resolved):
        self.resolved = resolved

    def query(self, *entities):
        assert entities == (models.Profile, models.Tenant)
        return IdentityQuery(self.resolved)


def test_identidade_resolve_usuario_papel_e_organizacao_juntos():
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

    result = get_current_user(
        {"sub": str(user_id), "email": "admin@escritorio.test"},
        IdentityDb((profile, tenant)),
    )

    assert result["user_id"] == str(user_id)
    assert result["tenant_id"] == str(tenant_id)
    assert result["role"] == "admin"
    assert result["plan"] == "profissional"
    assert result["billing_cycle"] == "annual"


def test_identidade_sem_vinculo_valido_com_organizacao_e_bloqueada():
    with pytest.raises(HTTPException) as error:
        get_current_user(
            {"sub": str(uuid4()), "email": "user@invalid.test"},
            IdentityDb(None),
        )

    assert error.value.status_code == 403


@pytest.mark.parametrize(
    "payment_status", ["inadimplente", "cancelado", "estornado", "chargeback"]
)
def test_conta_sem_assinatura_operacional_nao_pode_realizar_mutacoes(payment_status):
    with pytest.raises(HTTPException) as error:
        get_active_user({"payment_status": payment_status})

    assert error.value.status_code == 402
