from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from uuid import uuid4

import pytest
from fastapi import HTTPException
from starlette.requests import Request

from auth_service import resolve_user_context
from security import get_active_user
from trial_service import effective_plan, start_trial, trial_details
from test_auth_service import RegistrationDb
from test_billing import FakeBillingDb, make_context, payment_payload
import billing

NOW = datetime(2026, 10, 27, 12, tzinfo=timezone.utc)


def office(**overrides):
    data = dict(plano="free", trial_started_at=NOW, trial_ends_at=NOW + timedelta(days=14),
                trial_converted_at=None, status_pagamento="ativo", subscription_status="none", billing_cycle="monthly")
    return SimpleNamespace(**(data | overrides))


def test_exact_expiry_and_no_extension_on_retry():
    tenant = office()
    end = tenant.trial_ends_at
    start_trial(tenant, NOW + timedelta(days=3))
    assert tenant.trial_ends_at == end
    assert effective_plan(tenant, end - timedelta(microseconds=1)) == "profissional"
    assert effective_plan(tenant, end) == "free"
    assert trial_details(tenant, end)["days_remaining"] == 0
    assert trial_details(tenant, NOW)["days_remaining"] == 14


def test_legacy_office_gets_no_trial_and_paid_plan_takes_precedence():
    tenant = office(trial_started_at=None, trial_ends_at=None)
    assert effective_plan(tenant, NOW) == "free"
    assert trial_details(tenant, NOW)["status"] == "none"
    tenant = office(plano="basico")
    assert effective_plan(tenant, NOW) == "basico"
    assert trial_details(tenant, NOW)["status"] == "converted"


@pytest.mark.parametrize('payment_status', ['aguardando_pagamento', 'inadimplente', 'cancelado'])
def test_unpaid_checkout_does_not_revoke_active_trial(payment_status):
    now = datetime.now(timezone.utc)
    tenant = office(trial_started_at=now, trial_ends_at=now + timedelta(days=14), status_pagamento=payment_status)
    profile = SimpleNamespace(id=uuid4(), tenant_id=uuid4(), role="admin", is_superadmin=False)
    user = resolve_user_context(RegistrationDb([(profile, tenant)]), {"sub": str(profile.id)})
    assert user['plan'] == 'profissional'
    assert user['contracted_plan'] == 'free'
    assert get_active_user(user)['payment_status'] == 'ativo'


def test_first_payment_ends_trial_permanently():
    tenant, subscription = make_context()
    tenant.trial_started_at = NOW - timedelta(days=1)
    tenant.trial_ends_at = NOW + timedelta(days=13)
    tenant.trial_converted_at = None
    db = FakeBillingDb(subscription, tenant)
    billing.apply_payment_event(db, payment_payload(), 'PAYMENT_CONFIRMED', 'evt_trial', NOW)
    assert tenant.trial_converted_at == NOW
    assert trial_details(tenant, NOW)['status'] == 'converted'
    tenant.plano = 'free'
    assert effective_plan(tenant, NOW) == 'free'


@pytest.mark.parametrize(('method', 'path', 'role', 'allowed'), [
    ('POST', '/api/v1/obrigacoes', 'admin', False),
    ('POST', '/api/v1/documentos', 'admin', False),
    ('DELETE', '/api/v1/membros/{membro_id}', 'admin', True),
    ('PATCH', '/api/v1/clientes/{cliente_id}/desativar', 'admin', True),
    ('PATCH', '/api/v1/clientes/{cliente_id}/desativar', 'gerente', False),
])
def test_read_only_allows_only_admin_usage_reduction(method, path, role, allowed):
    user = dict(payment_status='ativo', trial_read_only=True, role=role)
    request = Request({'type': 'http', 'method': method, 'path': path, 'route': SimpleNamespace(path=path)})
    if allowed:
        assert get_active_user(user, request) == user
    else:
        with pytest.raises(HTTPException) as error:
            get_active_user(user, request)
        assert error.value.status_code == 403


@pytest.mark.parametrize(('clients', 'members', 'restricted'), [(5, 1, False), (6, 1, True), (5, 2, True)])
def test_expired_trial_counts_usage_and_returns_free(clients, members, restricted):
    tenant = office(trial_started_at=NOW - timedelta(days=40), trial_ends_at=NOW - timedelta(days=26))
    profile = SimpleNamespace(id=uuid4(), tenant_id=uuid4(), role='admin', is_superadmin=False)
    class Query:
        def __init__(self, value): self.value = value
        def join(self, *_): return self
        def filter(self, *_): return self
        def first(self): return self.value
        def count(self): return self.value
    class Db:
        values = iter([(profile, tenant), clients, members])
        def query(self, *_): return Query(next(self.values))
    user = resolve_user_context(Db(), {'sub': str(profile.id)})
    assert user['plan'] == 'free'
    assert user['trial_read_only'] is restricted


def test_export_is_admin_only_and_scopes_every_query_to_office():
    from auth import export_office
    import json
    import models
    tenant_id = uuid4()
    user = dict(user_id=str(uuid4()), tenant_id=str(tenant_id), role='colaborador')
    with pytest.raises(HTTPException) as error:
        export_office(None, user)
    assert error.value.status_code == 403
    queried = []
    class Query:
        def __init__(self, model): self.model = model
        def filter(self, condition):
            assert condition.right.value == tenant_id
            return self
        def order_by(self, *_): return self
        def all(self):
            queried.append(self.model)
            if self.model == models.Document:
                return [models.Document(id=uuid4(), tenant_id=tenant_id, nome_arquivo='teste.pdf', storage_path='private-key')]
            return []
    class Db:
        def query(self, model): return Query(model)
    result = export_office(Db(), user | {'role': 'admin'})
    payload = json.loads(result.body)
    assert len(queried) == 4
    assert payload['documentos'][0]['nome_arquivo'] == 'teste.pdf'
    assert 'storage_path' not in payload['documentos'][0]
    assert result.headers['cache-control'] == 'private, no-store'
