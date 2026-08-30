from types import SimpleNamespace
from uuid import uuid4

import pytest
from fastapi import HTTPException

import subscription_service


def test_create_subscription_rejects_free_plan_before_database_access():
    with pytest.raises(HTTPException) as error:
        subscription_service.create_subscription(
            None,
            {"tenant_id": "tenant", "user_id": "user", "role": "admin"},
            "free",
            "monthly",
        )

    assert error.value.status_code == 400
    assert error.value.detail == "Plano inválido ou gratuito."


def test_create_subscription_rejects_invalid_cycle_before_database_access():
    with pytest.raises(HTTPException) as error:
        subscription_service.create_subscription(
            None,
            {"tenant_id": "tenant", "user_id": "user", "role": "admin"},
            "profissional",
            "weekly",
        )

    assert error.value.status_code == 400
    assert error.value.detail == "Ciclo de cobrança inválido."


def test_create_subscription_rejects_collaborator_before_database_access():
    with pytest.raises(HTTPException) as error:
        subscription_service.create_subscription(
            None,
            {
                "tenant_id": str(uuid4()),
                "user_id": str(uuid4()),
                "role": "colaborador",
            },
            "profissional",
            "monthly",
        )

    assert error.value.status_code == 403
    assert error.value.detail == "Apenas administradores podem contratar planos."


@pytest.mark.parametrize(
    ("raw_document", "expected"),
    [
        ("529.982.247-25", "52998224725"),
        ("12.345.678/0001-90", "12345678000190"),
        ("AB.CDE.123/0001-90", "ABCDE123000190"),
    ],
)
def test_normalize_billing_document_accepts_supported_formats(
    raw_document,
    expected,
):
    assert subscription_service.normalize_billing_document(raw_document) == expected


def test_first_subscription_invoice_ignores_malformed_payment_items(monkeypatch):
    monkeypatch.setattr(
        subscription_service,
        "request_asaas",
        lambda *_args, **_kwargs: SimpleNamespace(
            status_code=200,
            json=lambda: {
                "data": [
                    "invalid",
                    {"id": "pay_123", "invoiceUrl": "https://invoice.test"},
                ]
            },
        ),
    )

    invoice_url, payments = subscription_service._first_subscription_invoice(
        "sub_123"
    )

    assert invoice_url == "https://invoice.test"
    assert payments == [
        {"id": "pay_123", "invoiceUrl": "https://invoice.test"}
    ]
