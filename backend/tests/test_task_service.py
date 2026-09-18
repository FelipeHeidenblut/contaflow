from datetime import date
from types import SimpleNamespace
from uuid import UUID, uuid4

import task_service
import pytest
from fastapi import HTTPException
from enums import TaskStatus
from schemas import TaskCreate


class TaskDb:
    def __init__(self):
        self.added = []
        self.deleted = []
        self.flushes = 0
        self.commits = 0
        self.refreshed = []

    def add(self, value):
        self.added.append(value)

    def delete(self, value):
        self.deleted.append(value)

    def flush(self):
        self.flushes += 1

    def commit(self):
        self.commits += 1

    def refresh(self, value):
        self.refreshed.append(value)


def make_user(role="admin"):
    return {
        "tenant_id": str(uuid4()),
        "user_id": str(uuid4()),
        "role": role,
    }


def test_create_task_applies_business_day_and_collaborator_assignment(monkeypatch):
    database = TaskDb()
    current_user = make_user("colaborador")
    payload = TaskCreate(
        title="Enviar obrigação",
        due_date=date(2026, 8, 29),
        client_id=uuid4(),
        assigned_to=None,
    )
    monkeypatch.setattr(task_service, "get_accessible_client", lambda *_args, **_kwargs: object())

    task = task_service.create_task(database, current_user, payload)

    assert task.due_date == date(2026, 8, 31)
    assert str(task.assigned_to) == current_user["user_id"]
    assert task.tenant_id == UUID(current_user["tenant_id"])
    assert database.added == [task]
    assert database.commits == 1
    assert database.refreshed == [task]


def test_complete_task_marks_status_and_processes_recurrence(monkeypatch):
    database = TaskDb()
    current_user = make_user()
    task = SimpleNamespace(status=TaskStatus.PENDENTE.value)
    processed = []
    monkeypatch.setattr(task_service, "get_accessible_task", lambda *_args, **_kwargs: task)
    monkeypatch.setattr(
        task_service,
        "ensure_next_occurrence",
        lambda db, current_task: processed.append((db, current_task)),
    )

    result = task_service.complete_task(database, current_user, uuid4())

    assert result is task
    assert task.status == TaskStatus.CONCLUIDA.value
    assert processed == [(database, task)]
    assert database.commits == 1
    assert database.refreshed == [task]


@pytest.mark.parametrize("new_status", list(TaskStatus))
def test_kanban_changes_only_status_and_keeps_assignment(monkeypatch, new_status):
    database = TaskDb()
    current_user = make_user("colaborador")
    task_id = uuid4()
    task = SimpleNamespace(
        status=TaskStatus.CONCLUIDA.value,
        assigned_to=uuid4(),
        client_id=uuid4(),
        due_date=date(2026, 9, 15),
        title="Fechamento mensal",
        recurrence_series_id=uuid4(),
        recurrence_period=date(2026, 9, 1),
        is_recurring=True,
        recurrence_day=15,
    )
    original = vars(task).copy()
    processed = []

    def accessible_task(db, identifier, user, *, for_update=False):
        assert (db, user, identifier) == (database, current_user, task_id)
        assert for_update is True
        return task

    monkeypatch.setattr(task_service, "get_accessible_task", accessible_task)
    monkeypatch.setattr(
        task_service, "ensure_next_occurrence", lambda db, value: processed.append(value)
    )

    result = task_service.change_task_status(database, current_user, task_id, new_status)

    assert result is task
    assert vars(task) == {**original, "status": new_status.value}
    assert processed == ([task] if new_status == TaskStatus.CONCLUIDA else [])
    assert database.commits == 1


def test_kanban_cannot_change_an_inaccessible_task(monkeypatch):
    database = TaskDb()

    def inaccessible_task(*args, **kwargs):
        raise HTTPException(status_code=404, detail="Tarefa não encontrada.")

    monkeypatch.setattr(task_service, "get_accessible_task", inaccessible_task)
    with pytest.raises(HTTPException) as error:
        task_service.change_task_status(database, make_user(), uuid4(), TaskStatus.EM_ANDAMENTO)

    assert error.value.status_code == 404
    assert database.commits == 0


def test_kanban_endpoint_validates_status_and_updates_task(monkeypatch):
    from datetime import datetime, timezone
    from pydantic import ValidationError
    from schemas import TaskStatusUpdate
    import obrigacoes

    user = make_user()
    database = TaskDb()
    task_id = uuid4()
    calls = []

    def change_status(db, current_user, identifier, new_status):
        calls.append((db, current_user, identifier, new_status))
        return {
            "id": identifier,
            "tenant_id": user["tenant_id"],
            "client_id": uuid4(),
            "title": "Fechamento mensal",
            "due_date": date(2026, 9, 15),
            "status": new_status,
            "created_at": datetime.now(timezone.utc),
        }

    monkeypatch.setattr(obrigacoes, "change_task_status", change_status)
    with pytest.raises(ValidationError):
        TaskStatusUpdate(status="atrasada")
    assert calls == []
    response = obrigacoes.atualizar_status_obrigacao(
        task_id, TaskStatusUpdate(status="em_andamento"), database, user
    )

    assert response["status"] == TaskStatus.EM_ANDAMENTO
    assert calls == [(database, user, task_id, TaskStatus.EM_ANDAMENTO)]


def test_update_task_starts_recurrence_series_when_enabled(monkeypatch):
    database = TaskDb()
    current_user = make_user()
    task = SimpleNamespace(
        title="Tarefa anterior",
        description=None,
        client_id=uuid4(),
        due_date=date(2026, 8, 28),
        grau_importancia="Média",
        status=TaskStatus.PENDENTE.value,
        assigned_to=None,
        is_recurring=False,
        recurrence_day=None,
    )
    payload = TaskCreate(
        title="Fechamento mensal",
        due_date=date(2026, 8, 30),
        client_id=uuid4(),
        assigned_to=uuid4(),
        is_recurring=True,
        recurrence_day=30,
    )
    initialized = []
    monkeypatch.setattr(
        task_service,
        "get_accessible_task",
        lambda *_args, **_kwargs: task,
    )
    monkeypatch.setattr(
        task_service,
        "get_accessible_client",
        lambda *_args, **_kwargs: object(),
    )
    monkeypatch.setattr(
        task_service,
        "validate_responsible_profile",
        lambda *_args, **_kwargs: object(),
    )
    monkeypatch.setattr(
        task_service,
        "initialize_task_recurrence",
        lambda current_task, nominal_date, **options: initialized.append(
            (current_task, nominal_date, options)
        ),
    )

    result = task_service.update_task(database, current_user, uuid4(), payload)

    assert result is task
    assert task.title == "Fechamento mensal"
    assert task.due_date == date(2026, 8, 31)
    assert task.assigned_to == payload.assigned_to
    assert task.is_recurring is True
    assert task.recurrence_day == 30
    assert initialized == [
        (task, payload.due_date, {"restart_series": True})
    ]
    assert database.commits == 1
    assert database.refreshed == [task]


def test_delete_task_removes_authorized_task(monkeypatch):
    database = TaskDb()
    current_user = make_user()
    task = SimpleNamespace(id=uuid4())
    monkeypatch.setattr(
        task_service,
        "get_accessible_task",
        lambda *_args, **_kwargs: task,
    )

    task_service.delete_task(database, current_user, task.id)

    assert database.deleted == [task]
    assert database.commits == 1


def test_list_tasks_returns_paginated_summary_from_authorized_scope(monkeypatch):
    class TaskQuery:
        def with_entities(self, *_values):
            return self

        def one(self):
            return (12, 4, 5, 2, 1)

        def order_by(self, *_values):
            return self

    query = TaskQuery()
    repository = SimpleNamespace(query=lambda _model: query)
    monkeypatch.setattr(task_service, "tenant_repository", lambda *_args: repository)
    monkeypatch.setattr(task_service, "apply_task_scope", lambda value, _user: value)
    monkeypatch.setattr(
        task_service,
        "paginate",
        lambda value, **options: {"query": value, **options},
    )

    result = task_service.list_tasks(
        object(),
        make_user(),
        task_service.TaskListFilters(page=2, page_size=20),
    )

    assert result["query"] is query
    assert result["page"] == 2
    assert result["page_size"] == 20
    assert result["summary"] == {
        "total": 12,
        "concluidas": 4,
        "pendentes": 5,
        "aguardando": 2,
        "atrasadas": 1,
    }
