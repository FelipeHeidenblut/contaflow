import os
import sys
from datetime import date
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException
from pydantic import ValidationError

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import alertas
import alert_service
from alertas import AlertPreferences, is_due_for_alert, lead_time_label, verify_cron_secret


def test_alerta_identifica_antecedencias_permitidas():
    reference = date(2026, 8, 13)

    assert is_due_for_alert(date(2026, 8, 15), 48, reference) is True
    assert is_due_for_alert(date(2026, 8, 16), 72, reference) is True
    assert is_due_for_alert(date(2026, 8, 20), 168, reference) is True
    assert is_due_for_alert(date(2026, 8, 14), 24, reference) is False


def test_preferencia_individual_aceita_antecedencia_valida():
    preferences = AlertPreferences(
        deadline_alerts_enabled=True,
        alert_advance_hours=72,
    )

    assert preferences.deadline_alerts_enabled is True
    assert preferences.alert_advance_hours == 72


def test_preferencia_rejeita_antecedencia_nao_suportada():
    with pytest.raises(ValidationError):
        AlertPreferences(
            deadline_alerts_enabled=True,
            alert_advance_hours=24,
        )


def test_rotulos_de_antecedencia():
    assert lead_time_label(48) == "2 dias"
    assert lead_time_label(72) == "3 dias"
    assert lead_time_label(168) == "1 semana"


def test_processador_envia_para_funcionario_responsavel(monkeypatch):
    reference = date(2026, 8, 13)
    task = SimpleNamespace(
        id="task-id",
        tenant_id="tenant-id",
        title="Entregar declaração",
        due_date=date(2026, 8, 16),
    )
    client = SimpleNamespace(
        id="client-id",
        razao_social="Empresa Cliente",
        nome=None,
        email="cliente@empresa.test",
    )
    employee = SimpleNamespace(
        id="profile-id",
        name="Funcionário Responsável",
        email="funcionario@escritorio.test",
        alert_advance_hours=72,
    )
    claimed_alert = SimpleNamespace(id="alert-id", status="processing", sent_at=None)

    query = MagicMock()
    query.join.return_value = query
    query.filter.return_value = query
    query.all.return_value = [(task, client, employee)]
    db = MagicMock()
    db.query.return_value = query

    sent_payloads = []
    monkeypatch.setattr(alert_service, "claim_alert", lambda *_args: claimed_alert)

    result = alertas.process_due_alerts(
        db,
        reference_date=reference,
        email_sender=sent_payloads.append,
    )

    assert result == {"candidates": 1, "sent": 1, "failed": 0, "skipped": 0}
    assert sent_payloads[0].recipient == "funcionario@escritorio.test"
    assert sent_payloads[0].recipient != client.email
    assert claimed_alert.status == "sent"


def test_segredo_do_cron_e_obrigatorio(monkeypatch):
    configured_secret = "segredo-forte-com-pelo-menos-32-caracteres"
    monkeypatch.setenv("ALERT_CRON_SECRET", configured_secret)

    with pytest.raises(HTTPException) as error:
        verify_cron_secret("segredo-incorreto")
    assert error.value.status_code == 401

    verify_cron_secret(configured_secret)
