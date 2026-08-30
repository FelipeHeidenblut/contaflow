import os
import sys
from datetime import date
from types import SimpleNamespace
from unittest.mock import MagicMock
from uuid import uuid4

import pytest
from fastapi import HTTPException

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from recurrence import (
    ensure_next_occurrence,
    initialize_task_recurrence,
    next_recurrence_period,
    recurrence_due_date,
    verify_recurrence_cron_secret,
)


def make_recurring_task(**overrides):
    values = {
        "id": uuid4(),
        "tenant_id": uuid4(),
        "client_id": uuid4(),
        "title": "Fechamento contábil",
        "description": "Conferir documentos do mês",
        "due_date": date(2026, 12, 15),
        "status": "concluida",
        "assigned_to": uuid4(),
        "grau_importancia": "Alta",
        "is_recurring": True,
        "recurrence_day": 15,
        "recurrence_series_id": uuid4(),
        "recurrence_period": date(2026, 12, 1),
        "next_occurrence_id": None,
        "recurrence_processed_at": None,
    }
    values.update(overrides)
    return SimpleNamespace(**values)


def test_proxima_competencia_atravessa_a_virada_do_ano():
    assert next_recurrence_period(date(2026, 12, 1)) == date(2027, 1, 1)


def test_fevereiro_limita_dia_inexistente_e_move_domingo():
    # 28/02/2027 é domingo; o vencimento passa para a segunda-feira.
    assert recurrence_due_date(date(2027, 2, 1), 31) == date(2027, 3, 1)


def test_fevereiro_bissexto_aceita_dia_29():
    assert recurrence_due_date(date(2028, 2, 1), 31) == date(2028, 2, 29)


def test_inicializacao_cria_identidade_e_competencia():
    task = make_recurring_task(
        recurrence_series_id=None,
        recurrence_period=None,
    )

    initialize_task_recurrence(task, date(2026, 8, 31))

    assert task.recurrence_series_id is not None
    assert task.recurrence_period == date(2026, 8, 1)


def test_edicao_preserva_serie_ativa_e_reativacao_inicia_outra():
    task = make_recurring_task()
    original_series = task.recurrence_series_id
    original_period = task.recurrence_period

    initialize_task_recurrence(task, date(2027, 2, 20))
    assert task.recurrence_series_id == original_series
    assert task.recurrence_period == original_period

    initialize_task_recurrence(
        task,
        date(2027, 2, 20),
        restart_series=True,
    )
    assert task.recurrence_series_id != original_series
    assert task.recurrence_period == date(2027, 2, 1)


def test_reprocessamento_nao_duplica_a_proxima_competencia():
    task = make_recurring_task()
    query = MagicMock()
    query.filter.return_value = query
    query.first.side_effect = [None, None]
    db = MagicMock()
    db.query.return_value = query

    next_task, created = ensure_next_occurrence(db, task)
    query.first.side_effect = [next_task]
    repeated_task, repeated_created = ensure_next_occurrence(db, task)

    assert created is True
    assert repeated_created is False
    assert repeated_task is next_task
    assert next_task.recurrence_period == date(2027, 1, 1)
    assert next_task.due_date == date(2027, 1, 15)
    assert task.next_occurrence_id == next_task.id
    assert db.add.call_count == 1


def test_ocorrencia_ja_existente_e_reutilizada():
    task = make_recurring_task()
    existing = make_recurring_task(
        recurrence_series_id=task.recurrence_series_id,
        recurrence_period=date(2027, 1, 1),
        status="pendente",
    )
    query = MagicMock()
    query.filter.return_value = query
    query.first.return_value = existing
    db = MagicMock()
    db.query.return_value = query

    next_task, created = ensure_next_occurrence(db, task)

    assert created is False
    assert next_task is existing
    assert task.next_occurrence_id == existing.id
    db.add.assert_not_called()


def test_segredo_do_reconciliador_e_obrigatorio(monkeypatch):
    configured_secret = "segredo-de-recorrencia-com-32-caracteres"
    monkeypatch.setenv("RECURRENCE_CRON_SECRET", configured_secret)

    with pytest.raises(HTTPException) as error:
        verify_recurrence_cron_secret("segredo-incorreto")
    assert error.value.status_code == 401

    verify_recurrence_cron_secret(configured_secret)
