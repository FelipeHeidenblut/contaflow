from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from uuid import uuid4

import pytest
from fastapi import HTTPException

import billing
import subscription_service


class FakeQuery:
    def __init__(self, value):
        self.value = value

    def filter(self, *_args):
        return self

    def with_for_update(self, *_args, **_kwargs):
        return self

    def order_by(self, *_args):
        return self

    def limit(self, *_args):
        return self

    def first(self):
        return self.value

    def all(self):
        if self.value is None:
            return []
        return self.value if isinstance(self.value, list) else [self.value]


class FakeBillingDb:
    def __init__(self, subscription, tenant, payment=None, event=None):
        self.subscription = subscription
        self.tenant = tenant
        self.payment = payment
        self.event = event
        self.added = []
        self.commits = 0
        self.rollbacks = 0

    def query(self, entity):
        if entity is billing.models.BillingSubscription:
            return FakeQuery(self.subscription)
        if entity is billing.models.Tenant:
            return FakeQuery(self.tenant)
        if entity is billing.models.PaymentRecord:
            return FakeQuery(self.payment)
        if entity is billing.models.AsaasWebhookEvent:
            return FakeQuery(self.event)
        return FakeQuery(None)

    def add(self, entity):
        self.added.append(entity)
        if isinstance(entity, billing.models.PaymentRecord):
            self.payment = entity

    def flush(self):
        return None

    def commit(self):
        self.commits += 1

    def rollback(self):
        self.rollbacks += 1


class FakeReconciliationDb(FakeBillingDb):
    def __init__(self, subscription, tenant):
        super().__init__(subscription, tenant)
        self.run = None

    def query(self, entity):
        if entity is billing.models.BillingReconciliationRun:
            return FakeQuery(self.run)
        return super().query(entity)

    def add(self, entity):
        super().add(entity)
        if isinstance(entity, billing.models.BillingReconciliationRun):
            self.run = entity

    def refresh(self, entity):
        if isinstance(entity, billing.models.BillingReconciliationRun) and entity.id is None:
            entity.id = uuid4()


def make_context():
    tenant_id = uuid4()
    tenant = SimpleNamespace(
        id=tenant_id,
        asaas_customer_id="cus_123",
        asaas_subscription_id="sub_123",
        status_pagamento="aguardando_pagamento",
        subscription_status="pending",
        plano="free",
        billing_cycle="monthly",
        billing_status_updated_at=None,
    )
    subscription = SimpleNamespace(
        id=uuid4(),
        tenant_id=tenant_id,
        provider_customer_id="cus_123",
        provider_subscription_id="sub_123",
        external_reference="reference",
        plan_code="profissional",
        billing_cycle="annual",
        status="pending",
        value=None,
        next_due_date=None,
        last_synced_at=None,
    )
    return tenant, subscription


def payment_payload(**overrides):
    payload = {
        "id": "pay_123",
        "customer": "cus_123",
        "subscription": "sub_123",
        "value": 1.00,
        "dueDate": "2026-08-26",
        "invoiceUrl": "https://invoice.test/pay_123",
    }
    payload.update(overrides)
    return payload


def test_referencia_de_assinatura_preserva_codigo_imutavel():
    local_id = uuid4()
    tenant_id = uuid4()
    value = billing.build_subscription_reference(
        local_id,
        tenant_id,
        "profissional",
        "annual",
    )

    parsed = billing.parse_subscription_reference(value)

    assert parsed.local_subscription_id == local_id
    assert parsed.tenant_id == tenant_id
    assert parsed.plan_code == "profissional"
    assert parsed.billing_cycle == "annual"


def test_pagamento_ativa_plano_pelo_codigo_e_nao_pelo_valor():
    tenant, subscription = make_context()
    db = FakeBillingDb(subscription, tenant)
    event_time = datetime(2026, 8, 25, 12, tzinfo=timezone.utc)

    billing.apply_payment_event(
        db,
        payment_payload(value="7.43"),
        "PAYMENT_CONFIRMED",
        "evt_confirmed",
        event_time,
    )

    assert tenant.plano == "profissional"
    assert tenant.billing_cycle == "annual"
    assert tenant.status_pagamento == "ativo"
    assert db.payment.plan_code == "profissional"
    assert db.payment.value == billing.Decimal("7.43")


@pytest.mark.parametrize(
    ("event_type", "expected_payment", "expected_tenant"),
    [
        ("PAYMENT_OVERDUE", "overdue", "inadimplente"),
        ("PAYMENT_REFUNDED", "refunded", "estornado"),
        ("PAYMENT_CHARGEBACK_REQUESTED", "chargeback", "chargeback"),
        ("PAYMENT_DELETED", "canceled", "aguardando_pagamento"),
    ],
)
def test_estados_financeiros_sao_separados(event_type, expected_payment, expected_tenant):
    tenant, subscription = make_context()
    db = FakeBillingDb(subscription, tenant)

    billing.apply_payment_event(
        db,
        payment_payload(),
        event_type,
        f"evt_{expected_payment}",
        datetime(2026, 8, 25, 12, tzinfo=timezone.utc),
    )

    assert db.payment.status == expected_payment
    assert tenant.status_pagamento == expected_tenant


def test_evento_antigo_nao_sobrescreve_estado_mais_recente():
    tenant, subscription = make_context()
    newest = datetime(2026, 8, 25, 15, tzinfo=timezone.utc)
    tenant.status_pagamento = "ativo"
    tenant.plano = "profissional"
    tenant.billing_cycle = "annual"
    tenant.billing_status_updated_at = newest
    payment = SimpleNamespace(
        provider_payment_id="pay_123",
        tenant_id=tenant.id,
        subscription_id="sub_123",
        provider_customer_id="cus_123",
        external_reference=None,
        plan_code="profissional",
        billing_cycle="annual",
        last_event_id="evt_received",
        provider_updated_at=newest,
        value=billing.Decimal("1499.00"),
        status="received",
        due_date=None,
        invoice_url=None,
        paid_at=newest,
    )
    db = FakeBillingDb(subscription, tenant, payment=payment)

    billing.apply_payment_event(
        db,
        payment_payload(),
        "PAYMENT_OVERDUE",
        "evt_old",
        newest - timedelta(hours=1),
    )

    assert payment.status == "received"
    assert tenant.status_pagamento == "ativo"


@pytest.mark.parametrize(
    ("provider_status", "local_status"),
    [("INACTIVE", "inactive"), ("EXPIRED", "expired")],
)
def test_reconciliacao_nao_reativa_assinatura_encerrada_com_pagamento_historico(
    monkeypatch, provider_status, local_status
):
    tenant, subscription = make_context()
    tenant.status_pagamento = "ativo"
    tenant.subscription_status = "active"
    db = FakeReconciliationDb(subscription, tenant)
    remote_subscription = {
        "id": "sub_123",
        "customer": "cus_123",
        "status": provider_status,
        "externalReference": subscription.external_reference,
    }
    historical_payment = payment_payload(
        status="RECEIVED",
        paymentDate="2026-07-25",
    )

    monkeypatch.setattr(
        subscription_service,
        "process_pending_webhooks",
        lambda *_args, **_kwargs: {
            "processed": 0,
            "failed": 0,
            "skipped": 0,
        },
    )
    monkeypatch.setattr(
        subscription_service,
        "request_asaas",
        lambda *_args, **_kwargs: SimpleNamespace(
            status_code=200,
            json=lambda: remote_subscription,
        ),
    )
    monkeypatch.setattr(
        subscription_service,
        "_first_subscription_invoice",
        lambda _subscription_id: (None, [historical_payment]),
    )

    subscription_service.reconcile_asaas(db)

    assert db.payment.status == "received"
    assert tenant.status_pagamento == "cancelado"
    assert tenant.subscription_status == local_status


def test_reconciliacao_rejeita_assinatura_de_outro_cliente_asaas(monkeypatch):
    tenant, subscription = make_context()
    db = FakeReconciliationDb(subscription, tenant)
    remote_subscription = {
        "id": "sub_123",
        "customer": "cus_outro_escritorio",
        "status": "ACTIVE",
        "externalReference": subscription.external_reference,
    }

    monkeypatch.setattr(
        subscription_service,
        "process_pending_webhooks",
        lambda *_args, **_kwargs: {
            "processed": 0,
            "failed": 0,
            "skipped": 0,
        },
    )
    monkeypatch.setattr(
        subscription_service,
        "request_asaas",
        lambda *_args, **_kwargs: SimpleNamespace(
            status_code=200,
            json=lambda: remote_subscription,
        ),
    )
    monkeypatch.setattr(
        subscription_service,
        "_first_subscription_invoice",
        lambda _subscription_id: (None, []),
    )

    result = subscription_service.reconcile_asaas(db)

    assert result["failures"] == 1
    assert subscription.provider_customer_id == "cus_123"


def test_evento_processado_nao_executa_novamente(monkeypatch):
    event = SimpleNamespace(
        id="evt_done",
        status="pending",
        processing_started_at=None,
        next_retry_at=None,
        attempts=0,
        payload={"id": "evt_done", "event": "PAYMENT_RECEIVED"},
        tenant_id=None,
        error=None,
        processed_at=None,
    )
    db = FakeBillingDb(None, None, event=event)
    calls = []
    tenant = SimpleNamespace(id=uuid4())

    def apply_once(*_args):
        calls.append(True)
        return tenant

    monkeypatch.setattr(billing, "apply_webhook_payload", apply_once)

    assert billing.process_webhook_event(db, event.id) == "success"
    assert billing.process_webhook_event(db, event.id) == "success"
    assert calls == [True]
    assert event.attempts == 1


def test_segredo_da_reconciliacao_e_obrigatorio(monkeypatch):
    secret = "segredo-de-reconciliacao-com-32-caracteres"
    monkeypatch.setenv("ASAAS_RECONCILIATION_SECRET", secret)

    with pytest.raises(HTTPException) as error:
        billing.verify_reconciliation_secret("incorreto")
    assert error.value.status_code == 401

    billing.verify_reconciliation_secret(secret)


def test_cliente_asaas_repete_falha_transitoria_com_backoff(monkeypatch):
    responses = iter(
        [
            SimpleNamespace(status_code=503),
            SimpleNamespace(status_code=200),
        ]
    )
    waits = []

    class FakeClient:
        def __init__(self, **_kwargs):
            pass

        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return None

        def get(self, _url, **_kwargs):
            return next(responses)

    monkeypatch.setattr(billing.httpx, "Client", FakeClient)
    monkeypatch.setattr(billing.time, "sleep", waits.append)

    response = billing.request_asaas(
        "GET",
        "https://api-sandbox.asaas.com/v3/subscriptions/sub_123",
        {"access_token": "test"},
    )

    assert response.status_code == 200
    assert waits == [0.2]
