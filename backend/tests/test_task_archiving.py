from datetime import date, datetime, timezone
from uuid import uuid4

import models
import pytest
from enums import TaskStatus
from fastapi import HTTPException
from schemas import TaskCreate
from sqlalchemy import CheckConstraint, Column, MetaData, Table, create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from task_service import (
    TaskListFilters, archive_task, change_task_status, list_tasks, restore_task, update_task,
)


@pytest.fixture
def database():
    engine = create_engine("sqlite:///:memory:")
    metadata = MetaData()
    for model in (models.Client, models.Task):
        table = Table(model.__tablename__, metadata, *(
            Column(column.name, column.type, primary_key=column.primary_key)
            for column in model.__table__.columns
        ))
        if model is models.Task:
            table.append_constraint(CheckConstraint("archived_at IS NULL OR status = 'concluida'"))
    metadata.create_all(engine)
    with Session(engine) as session:
        yield session
    engine.dispose()


def user(*, role="admin", tenant_id=None):
    return {"role": role, "tenant_id": str(tenant_id or uuid4()), "user_id": str(uuid4())}


def task(database, current_user, **overrides):
    values = dict(
        id=uuid4(), tenant_id=current_user["tenant_id"], client_id=uuid4(),
        assigned_to=current_user["user_id"], title="Fechamento mensal",
        status="concluida", due_date=date(2026, 10, 28),
    )
    from uuid import UUID
    values["tenant_id"] = UUID(values["tenant_id"])
    values["assigned_to"] = UUID(values["assigned_to"])
    values.update(overrides)
    item = models.Task(**values)
    database.add(item)
    database.commit()
    return item


def test_archive_and_restore_are_idempotent_and_keep_recurrence_history(database):
    current_user = user()
    next_task = task(database, current_user, status="pendente")
    completed = task(database, current_user, next_occurrence_id=next_task.id,
                     is_recurring=True, recurrence_day=28,
                     recurrence_series_id=uuid4(), recurrence_period=date(2026, 10, 1))
    original = (completed.client_id, completed.assigned_to, completed.recurrence_series_id)

    archive_task(database, current_user, completed.id)
    timestamp = completed.archived_at
    assert timestamp is not None
    assert completed.status == "concluida"
    archive_task(database, current_user, completed.id)
    assert completed.archived_at == timestamp
    assert (completed.client_id, completed.assigned_to, completed.recurrence_series_id) == original
    assert completed.next_occurrence_id == next_task.id
    assert next_task.status == "pendente"
    assert next_task.archived_at is None
    assert database.query(models.Task).count() == 2

    restore_task(database, current_user, completed.id)
    restore_task(database, current_user, completed.id)
    assert completed.archived_at is None
    assert completed.status == "concluida"
    assert completed.next_occurrence_id == next_task.id


@pytest.mark.parametrize("status", ["pendente", "em_andamento", "aguardando_cliente"])
def test_only_completed_tasks_can_be_archived(database, status):
    current_user = user()
    item = task(database, current_user, status=status)
    with pytest.raises(HTTPException) as error:
        archive_task(database, current_user, item.id)
    assert error.value.status_code == 409
    assert item.archived_at is None
    assert item.status == status


def test_listings_hide_archives_but_offer_scoped_history(database):
    current_user = user()
    active = task(database, current_user)
    archived = task(database, current_user)
    archive_task(database, current_user, archived.id)
    foreign_user = user()
    foreign = task(database, foreign_user)
    archive_task(database, foreign_user, foreign.id)

    result = list_tasks(database, current_user, TaskListFilters())
    assert [item.id for item in result["items"]] == [active.id]
    assert result["summary"]["concluidas"] == 1
    result = list_tasks(database, current_user, TaskListFilters(
        archived=True, client_id=archived.client_id, assigned_to=archived.assigned_to,
        search="Fechamento", page_size=1,
    ))
    assert [item.id for item in result["items"]] == [archived.id]
    assert result["total"] == 1
    result = list_tasks(database, current_user, TaskListFilters(include_archived=True))
    assert {item.id for item in result["items"]} == {active.id, archived.id}
    assert result["summary"]["concluidas"] == 2


@pytest.mark.parametrize("action", [archive_task, restore_task])
def test_archive_access_is_scoped_to_tenant_and_portfolio(database, action):
    current_user = user(role="colaborador")
    foreign = task(database, user())
    private = task(database, current_user)
    database.add(models.Client(id=private.client_id, tenant_id=private.tenant_id,
                               responsible_profile_id=uuid4()))
    database.commit()
    for identifier in (foreign.id, private.id):
        with pytest.raises(HTTPException) as error:
            action(database, current_user, identifier)
        assert error.value.status_code == 404


def test_archived_tasks_require_restoration_before_status_or_content_changes(database):
    current_user = user()
    item = task(database, current_user)
    archive_task(database, current_user, item.id)
    payload = TaskCreate(title="Alterada", client_id=item.client_id, due_date=item.due_date)
    for operation in (
        lambda: change_task_status(database, current_user, item.id, TaskStatus.PENDENTE),
        lambda: update_task(database, current_user, item.id, payload),
    ):
        with pytest.raises(HTTPException) as error:
            operation()
        assert error.value.status_code == 409
    assert item.title == "Fechamento mensal"
    assert item.status == "concluida"
    assert item.archived_at is not None


def test_database_rejects_archived_unfinished_tasks(database):
    with pytest.raises(IntegrityError):
        task(database, user(), status="pendente", archived_at=datetime.now(timezone.utc))
    database.rollback()
