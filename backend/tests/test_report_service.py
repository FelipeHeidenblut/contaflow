import os
import sys
from datetime import date, datetime, timezone
from unittest.mock import MagicMock
from uuid import uuid4

import pytest
from fastapi import HTTPException


sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import models
import report_service


def _user(plan="profissional", role="admin"):
    return {
        "tenant_id": str(uuid4()),
        "user_id": str(uuid4()),
        "role": role,
        "plan": plan,
        "payment_status": "ativo",
    }


def _empty_query():
    query = MagicMock()
    query.filter.return_value = query
    query.join.return_value = query
    query.all.return_value = []
    return query


def test_data_operacional_usa_fuso_de_sao_paulo():
    beginning_of_utc_day = datetime(2026, 9, 1, 1, tzinfo=timezone.utc)

    assert report_service.business_date(beginning_of_utc_day) == date(2026, 8, 31)


def test_periodo_invertido_e_rejeitado_antes_de_consultar_banco():
    db = MagicMock()

    with pytest.raises(HTTPException) as error:
        report_service.generate_report(
            db,
            _user(),
            start_date=date(2026, 8, 31),
            end_date=date(2026, 8, 1),
            today=date(2026, 8, 31),
        )

    assert error.value.status_code == 422
    db.query.assert_not_called()


@pytest.mark.parametrize(
    ("plan", "payment_status", "expected_status"),
    [
        ("free", "ativo", 403),
        ("profissional", "inadimplente", 402),
    ],
)
def test_servico_falha_fechado_sem_plano_pago_ativo(
    plan,
    payment_status,
    expected_status,
):
    db = MagicMock()
    current_user = _user(plan=plan)
    current_user["payment_status"] = payment_status

    with pytest.raises(HTTPException) as error:
        report_service.generate_report(
            db,
            current_user,
            start_date=date(2026, 8, 1),
            end_date=date(2026, 8, 31),
            today=date(2026, 8, 31),
        )

    assert error.value.status_code == expected_status
    db.query.assert_not_called()


def test_plano_essencial_nao_consulta_nomes_descartados_do_relatorio():
    task_query = _empty_query()
    queried_models = []
    db = MagicMock()

    def query(model):
        queried_models.append(model)
        return task_query

    db.query.side_effect = query

    report = report_service.generate_report(
        db,
        _user(plan="basico"),
        start_date=date(2026, 8, 1),
        end_date=date(2026, 8, 31),
        today=date(2026, 8, 31),
    )

    assert queried_models == [models.Task]
    assert report["clients"] == []
    assert report["team"] == []
    assert report["filters"] == {"clients": [], "members": []}
    assert report["access"]["advanced"] is False


def test_filtro_de_cliente_inacessivel_falha_sem_consultar_tarefas(monkeypatch):
    db = MagicMock()

    def reject_client(*_args, **_kwargs):
        raise HTTPException(status_code=404, detail="Cliente não encontrado.")

    monkeypatch.setattr(report_service, "get_accessible_client", reject_client)

    with pytest.raises(HTTPException) as error:
        report_service.generate_report(
            db,
            _user(),
            start_date=date(2026, 8, 1),
            end_date=date(2026, 8, 31),
            today=date(2026, 8, 31),
            client_id=uuid4(),
        )

    assert error.value.status_code == 404
    db.query.assert_not_called()


def test_relatorio_aplica_escopo_da_carteira_antes_de_agregar(monkeypatch):
    task_query = _empty_query()
    client_query = _empty_query()
    member_query = _empty_query()
    db = MagicMock()
    queries = {
        models.Task: task_query,
        models.Client: client_query,
        models.Profile: member_query,
    }
    db.query.side_effect = queries.__getitem__
    scoped = []

    def apply_scope(query, current_user):
        scoped.append((query, current_user))
        return query

    monkeypatch.setattr(report_service, "apply_task_scope", apply_scope)

    report_service.generate_report(
        db,
        _user(role="colaborador"),
        start_date=date(2026, 8, 1),
        end_date=date(2026, 8, 31),
        today=date(2026, 8, 31),
    )

    assert len(scoped) == 1
    assert scoped[0][0] is task_query
    assert scoped[0][1]["role"] == "colaborador"


def test_status_desconhecido_e_rejeitado_antes_de_consultar_banco():
    db = MagicMock()

    with pytest.raises(HTTPException) as error:
        report_service.generate_report(
            db,
            _user(),
            start_date=date(2026, 8, 1),
            end_date=date(2026, 8, 31),
            today=date(2026, 8, 31),
            task_status="apagada",
        )

    assert error.value.status_code == 422
    db.query.assert_not_called()
