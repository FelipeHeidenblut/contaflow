from types import SimpleNamespace
from uuid import uuid4

import pytest
from fastapi import HTTPException

import subscription_service


class FakeDb:
    def __init__(self):
        self.commits = 0
        self.flushes = 0
        self.added = []

    def commit(self):
        self.commits += 1

    def flush(self):
        self.flushes += 1

    def add(self, entity):
        self.added.append(entity)


class FakeResponse:
    def __init__(self, status_code, payload):
        self.status_code = status_code
        self._payload = payload

    def json(self):
        return self._payload


def make_client(response, calls):
    class FakeClient:
        def __init__(self, **_kwargs):
            pass

        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return None

        def post(self, url, json, headers):
            calls.append(("POST", url, json, headers))
            return response

        def put(self, url, json, headers):
            calls.append(("PUT", url, json, headers))
            return response

        def get(self, url, headers):
            calls.append(("GET", url, None, headers))
            return response

    return FakeClient


@pytest.mark.parametrize(
    ("raw_document", "expected"),
    [
        ("529.982.247-25", "52998224725"),
        ("12.345.678/0001-90", "12345678000190"),
        ("AB.CDE.123/0001-90", "ABCDE123000190"),
    ],
)
def test_billing_document_accepts_cpf_and_both_cnpj_formats(raw_document, expected):
    assert subscription_service.normalize_billing_document(raw_document) == expected


@pytest.mark.parametrize("raw_document", [None, "", "123", "ABCDEFGHIJKLMN"])
def test_billing_document_rejects_invalid_format(raw_document):
    with pytest.raises(HTTPException) as error:
        subscription_service.normalize_billing_document(raw_document)

    assert error.value.status_code == 422


def test_new_asaas_customer_is_created_with_cpf(monkeypatch):
    calls = []
    monkeypatch.setattr(
        subscription_service.httpx,
        "Client",
        make_client(FakeResponse(201, {"id": "cus_new"}), calls),
    )
    tenant = SimpleNamespace(
        id=uuid4(),
        razao_social="Escritório Teste",
        cnpj="529.982.247-25",
        asaas_customer_id=None,
    )
    db = FakeDb()

    customer_id = subscription_service.ensure_asaas_customer(db, tenant)

    assert customer_id == "cus_new"
    assert tenant.asaas_customer_id == "cus_new"
    assert db.commits == 0
    assert db.flushes == 1
    assert calls[-1][0] == "POST"
    assert calls[-1][2]["cpfCnpj"] == "52998224725"
    assert calls[-1][2]["externalReference"] == str(tenant.id)


def test_existing_asaas_customer_is_updated_with_cpf(monkeypatch):
    calls = []
    monkeypatch.setattr(
        subscription_service.httpx,
        "Client",
        make_client(FakeResponse(200, {}), calls),
    )
    tenant = SimpleNamespace(
        id=uuid4(),
        razao_social="Escritório Teste",
        cnpj="52998224725",
        asaas_customer_id="cus_existing",
    )
    db = FakeDb()

    customer_id = subscription_service.ensure_asaas_customer(db, tenant)

    assert customer_id == "cus_existing"
    assert db.commits == 0
    assert calls[0][0] == "PUT"
    assert calls[0][1].endswith("/customers/cus_existing")
    assert calls[0][2]["cpfCnpj"] == "52998224725"


def test_gateway_rejection_returns_safe_error(monkeypatch):
    calls = []
    monkeypatch.setattr(
        subscription_service.httpx,
        "Client",
        make_client(
            FakeResponse(
                400,
                {"errors": [{"description": "CPF ou CNPJ inválido"}]},
            ),
            calls,
        ),
    )
    tenant = SimpleNamespace(
        id=uuid4(),
        razao_social="Escritório Teste",
        cnpj="52998224725",
        asaas_customer_id="cus_existing",
    )

    with pytest.raises(HTTPException) as error:
        subscription_service.ensure_asaas_customer(FakeDb(), tenant)

    assert error.value.status_code == 502
    assert "CPF/CNPJ" in error.value.detail


def test_annual_office_subscription_uses_yearly_cycle(monkeypatch):
    requests = []

    class TenantQuery:
        def __init__(self, tenant):
            self.tenant = tenant

        def filter(self, *_args):
            return self

        def with_for_update(self):
            return self

        def order_by(self, *_args):
            return self

        def first(self):
            return self.tenant

    class TenantDb(FakeDb):
        def __init__(self, tenant):
            super().__init__()
            self.tenant = tenant

        def query(self, entity):
            if entity is subscription_service.models.Tenant:
                return TenantQuery(self.tenant)
            return TenantQuery(None)

    tenant = SimpleNamespace(
        id=uuid4(),
        razao_social="Escritório Teste",
        cnpj="52998224725",
        asaas_customer_id="cus_existing",
        asaas_subscription_id=None,
        status_pagamento="ativo",
        plano="free",
        billing_cycle="monthly",
        subscription_status="none",
        billing_status_updated_at=None,
    )
    db = TenantDb(tenant)
    monkeypatch.setattr(
        subscription_service,
        "ensure_asaas_customer",
        lambda *_args: "cus_existing",
    )
    monkeypatch.setattr(
        subscription_service,
        "_find_remote_subscription",
        lambda *_args: None,
    )
    monkeypatch.setattr(
        subscription_service,
        "_first_subscription_invoice",
        lambda *_args: ("https://checkout.test", []),
    )

    def fake_request(method, url, _headers, **kwargs):
        requests.append((method, url, kwargs.get("json_payload"), _headers))
        return FakeResponse(201, {"id": "sub_annual"})

    monkeypatch.setattr(subscription_service, "request_asaas", fake_request)

    result = subscription_service.create_subscription(
        db,
        {"tenant_id": str(tenant.id), "user_id": str(uuid4()), "role": "admin"},
        "escritorio",
        "annual",
    )

    subscription_payload = requests[0][2]
    assert subscription_payload["value"] == 2499.0
    assert subscription_payload["cycle"] == "YEARLY"
    assert tenant.billing_cycle == "annual"
    assert tenant.asaas_subscription_id == "sub_annual"
    assert result["invoice_url"] == "https://checkout.test"
    subscription = next(
        entity
        for entity in db.added
        if isinstance(entity, subscription_service.models.BillingSubscription)
    )
    assert subscription.plan_code == "escritorio"
    assert ":escritorio:annual" in subscription.external_reference
