import os
import sys
from datetime import date, datetime, timedelta, timezone
from types import SimpleNamespace
from unittest.mock import MagicMock
from uuid import uuid4

import pytest
from fastapi import HTTPException

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import alert_service


def _current_user(role="colaborador"):
    return {
        "tenant_id": str(uuid4()),
        "user_id": str(uuid4()),
        "role": role,
        "is_superadmin": False,
    }


def test_preferencias_sao_lidas_do_perfil_do_escritorio():
    profile = SimpleNamespace(
        email="responsavel@escritorio.test",
        deadline_alerts_enabled=True,
        alert_advance_hours=168,
    )
    query = MagicMock()
    query.filter.return_value = query
    query.first.return_value = profile
    db = MagicMock()
    db.query.return_value = query

    result = alert_service.get_alert_preferences(db, _current_user())

    assert result == {
        "email": "responsavel@escritorio.test",
        "deadline_alerts_enabled": True,
        "alert_advance_hours": 168,
    }
    assert query.filter.call_count == 2


def test_preferencias_rejeitam_usuario_sem_permissao():
    db = MagicMock()

    with pytest.raises(HTTPException) as error:
        alert_service.get_alert_preferences(db, _current_user(role="invalido"))

    assert error.value.status_code == 403
    db.query.assert_not_called()


def test_nao_ativa_alerta_sem_email_no_perfil():
    profile = SimpleNamespace(
        email=None,
        deadline_alerts_enabled=False,
        alert_advance_hours=72,
    )
    query = MagicMock()
    query.filter.return_value = query
    query.first.return_value = profile
    db = MagicMock()
    db.query.return_value = query

    with pytest.raises(HTTPException) as error:
        alert_service.update_alert_preferences(
            db,
            _current_user(),
            enabled=True,
            advance_hours=48,
        )

    assert error.value.status_code == 422
    db.commit.assert_not_called()


def _claim_context(existing):
    query = MagicMock()
    query.filter.return_value = query
    query.with_for_update.return_value = query
    query.first.return_value = existing
    db = MagicMock()
    db.query.return_value = query
    task = SimpleNamespace(
        id="task-id",
        tenant_id="tenant-id",
        due_date=date(2026, 9, 2),
    )
    client = SimpleNamespace(id="client-id")
    recipient = SimpleNamespace(
        id="profile-id",
        email="funcionario@escritorio.test",
        alert_advance_hours=72,
    )
    return db, task, client, recipient, query


def test_claim_nao_reprocessa_reserva_recente():
    now = datetime(2026, 8, 30, 12, tzinfo=timezone.utc)
    existing = SimpleNamespace(
        status="processing",
        attempts=1,
        updated_at=now - timedelta(minutes=2),
    )
    db, task, client, recipient, query = _claim_context(existing)

    claimed = alert_service.claim_alert(
        db,
        task,
        client,
        recipient,
        now=now,
    )

    assert claimed is None
    query.with_for_update.assert_called_once_with(skip_locked=True)
    db.commit.assert_not_called()


def test_claim_recupera_reserva_abandonada():
    now = datetime(2026, 8, 30, 12, tzinfo=timezone.utc)
    existing = SimpleNamespace(
        status="processing",
        attempts=1,
        updated_at=now - alert_service.PROCESSING_LEASE - timedelta(seconds=1),
        last_error="erro anterior",
        recipient_email="antigo@escritorio.test",
    )
    db, task, client, recipient, _query = _claim_context(existing)

    claimed = alert_service.claim_alert(
        db,
        task,
        client,
        recipient,
        now=now,
    )

    assert claimed is existing
    assert existing.status == "processing"
    assert existing.attempts == 2
    assert existing.last_error is None
    assert existing.recipient_email == recipient.email
    db.commit.assert_called_once_with()
    db.refresh.assert_called_once_with(existing)


def test_processador_isola_falha_inesperada_e_continua_lote(monkeypatch):
    reference = date(2026, 8, 30)
    first_task = SimpleNamespace(
        id="task-1",
        tenant_id="tenant-id",
        title="Primeira tarefa",
        due_date=date(2026, 9, 2),
    )
    second_task = SimpleNamespace(
        id="task-2",
        tenant_id="tenant-id",
        title="Segunda tarefa",
        due_date=date(2026, 9, 2),
    )
    client = SimpleNamespace(id="client-id", razao_social="Cliente", nome=None)
    recipient = SimpleNamespace(
        id="profile-id",
        name="Responsável",
        email="responsavel@escritorio.test",
        alert_advance_hours=72,
    )
    first_alert = SimpleNamespace(id="alert-1", status="processing", sent_at=None)
    second_alert = SimpleNamespace(id="alert-2", status="processing", sent_at=None)

    query = MagicMock()
    query.join.return_value = query
    query.filter.return_value = query
    query.all.return_value = [
        (first_task, client, recipient),
        (second_task, client, recipient),
    ]
    db = MagicMock()
    db.query.return_value = query
    claimed = iter([first_alert, second_alert])
    monkeypatch.setattr(alert_service, "claim_alert", lambda *_args: next(claimed))

    sent = []

    def sender(payload):
        sent.append(payload.task_title)
        if payload.task_title == "Primeira tarefa":
            raise TypeError("falha inesperada do adaptador")

    result = alert_service.process_due_alerts(
        db,
        reference_date=reference,
        email_sender=sender,
    )

    assert result == {"candidates": 2, "sent": 1, "failed": 1, "skipped": 0}
    assert sent == ["Primeira tarefa", "Segunda tarefa"]
    assert first_alert.status == "failed"
    assert first_alert.last_error == "falha inesperada do adaptador"
    assert second_alert.status == "sent"
    assert second_alert.sent_at is not None
    assert db.commit.call_count == 2


def test_smtp_autenticado_exige_transporte_seguro():
    settings = alert_service.SmtpSettings.from_mapping(
        {
            "SMTP_HOST": "smtp.example.test",
            "SMTP_PORT": "25",
            "SMTP_USERNAME": "user",
            "SMTP_PASSWORD": "secret",
            "SMTP_USE_SSL": "false",
            "SMTP_USE_TLS": "false",
            "ALERT_FROM_EMAIL": "alertas@example.test",
        }
    )

    try:
        settings.validate()
    except RuntimeError as error:
        assert "TLS ou SSL" in str(error)
    else:
        raise AssertionError("Credenciais SMTP não podem trafegar sem TLS ou SSL.")
