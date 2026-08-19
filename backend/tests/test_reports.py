import os
import sys
from datetime import date
from types import SimpleNamespace
from uuid import uuid4

import pytest
from fastapi import HTTPException

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import models
from relatorios import build_report, get_report_capabilities, require_paid_reports


class TenantQuery:
    def __init__(self, tenant):
        self.tenant = tenant

    def filter(self, *args):
        return self

    def first(self):
        return self.tenant


class TenantDb:
    def __init__(self, tenant):
        self.tenant = tenant

    def query(self, entity):
        assert entity is models.Tenant
        return TenantQuery(self.tenant)


def test_relatorios_bloqueiam_plano_gratuito():
    tenant = SimpleNamespace(plano="free", status_pagamento="ativo")
    with pytest.raises(HTTPException) as error:
        require_paid_reports(TenantDb(tenant), {"tenant_id": str(uuid4())})
    assert error.value.status_code == 403


def test_relatorios_liberam_plano_pago_ativo():
    tenant = SimpleNamespace(plano="profissional", status_pagamento="ativo")
    user = {"tenant_id": str(uuid4()), "role": "admin"}
    result = require_paid_reports(TenantDb(tenant), user)
    assert result["plan"] == "profissional"


def test_plano_essencial_recebe_apenas_relatorio_resumido():
    capabilities = get_report_capabilities("basico")

    assert capabilities == {
        "advanced": False,
        "can_export": False,
        "max_report_days": 92,
    }


def test_plano_profissional_recebe_relatorio_avancado():
    capabilities = get_report_capabilities("profissional")

    assert capabilities == {
        "advanced": True,
        "can_export": True,
        "max_report_days": 366,
    }


def test_plano_escritorio_recebe_relatorio_avancado():
    capabilities = get_report_capabilities("escritorio")

    assert capabilities == {
        "advanced": True,
        "can_export": True,
        "max_report_days": 366,
    }


def test_agregacao_do_relatorio_usa_apenas_dados_recebidos():
    client_id = uuid4()
    member_id = uuid4()
    clients = [
        SimpleNamespace(
            id=client_id, razao_social="Empresa Teste", nome=None, ativo=True
        )
    ]
    members = [SimpleNamespace(id=member_id, name="Ana Contadora")]
    tasks = [
        SimpleNamespace(
            client_id=client_id,
            assigned_to=member_id,
            due_date=date(2026, 7, 10),
            status="concluida",
        ),
        SimpleNamespace(
            client_id=client_id,
            assigned_to=member_id,
            due_date=date(2026, 7, 20),
            status="pendente",
        ),
    ]

    report = build_report(
        tasks,
        clients,
        members,
        date(2026, 7, 1),
        date(2026, 7, 31),
        date(2026, 8, 1),
    )

    assert report["summary"] == {
        "total": 2,
        "completed": 1,
        "open": 1,
        "overdue": 1,
        "completion_rate": 50,
        "clients_with_overdue": 1,
    }
    assert report["clients"][0]["name"] == "Empresa Teste"
    assert report["team"][0]["name"] == "Ana Contadora"
    assert report["timeline"][0]["total"] == 2
