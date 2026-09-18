from dataclasses import dataclass
from datetime import date
from uuid import UUID

import models
import schemas
from access_control import (
    Permission,
    apply_task_scope,
    get_accessible_client,
    get_accessible_task,
    has_management_access,
    require_permission,
    tenant_repository,
    validate_responsible_profile,
)
from enums import TaskStatus
from fastapi import HTTPException, status
from pagination import paginate
from recurrence import (
    adjust_to_business_day,
    ensure_next_occurrence,
    initialize_task_recurrence,
)
from sqlalchemy import case, func, or_
from sqlalchemy.orm import Session


@dataclass(frozen=True, slots=True)
class TaskListFilters:
    search: str | None = None
    client_id: UUID | None = None
    assigned_to: UUID | None = None
    task_status: TaskStatus | None = None
    page: int = 1
    page_size: int = 20


def list_tasks(
    db: Session,
    current_user: dict,
    filters: TaskListFilters,
) -> dict:
    require_permission(current_user, Permission.TASK_READ)
    base_query = apply_task_scope(
        tenant_repository(db, current_user).query(models.Task),
        current_user,
    )
    total, completed, pending, waiting, overdue = base_query.with_entities(
        func.count(models.Task.id),
        func.count(models.Task.id).filter(
            models.Task.status == TaskStatus.CONCLUIDA.value
        ),
        func.count(models.Task.id).filter(
            models.Task.status == TaskStatus.PENDENTE.value
        ),
        func.count(models.Task.id).filter(
            models.Task.status == TaskStatus.AGUARDANDO_CLIENTE.value
        ),
        func.count(models.Task.id).filter(
            models.Task.due_date < date.today(),
            models.Task.status != TaskStatus.CONCLUIDA.value,
        ),
    ).one()

    query = base_query
    if filters.search:
        term = filters.search.strip()
        query = query.filter(
            or_(
                models.Task.title.icontains(term, autoescape=True),
                models.Task.description.icontains(term, autoescape=True),
            )
        )
    if filters.client_id:
        query = query.filter(models.Task.client_id == filters.client_id)
    if filters.assigned_to:
        query = query.filter(models.Task.assigned_to == filters.assigned_to)
    if filters.task_status:
        query = query.filter(models.Task.status == filters.task_status.value)

    priority_order = case(
        (models.Task.grau_importancia == "Urgente", 4),
        (models.Task.grau_importancia == "Alta", 3),
        (models.Task.grau_importancia == "Média", 2),
        else_=1,
    )
    query = query.order_by(
        priority_order.desc(),
        models.Task.due_date.asc(),
        models.Task.id.asc(),
    )
    return paginate(
        query,
        page=filters.page,
        page_size=filters.page_size,
        summary={
            "total": total,
            "concluidas": completed,
            "pendentes": pending,
            "aguardando": waiting,
            "atrasadas": overdue,
        },
    )


def _validate_task_relationships(
    db: Session,
    current_user: dict,
    task_input: schemas.TaskCreate,
) -> None:
    get_accessible_client(db, task_input.client_id, current_user, active_only=True)
    if task_input.assigned_to:
        validate_responsible_profile(db, current_user, task_input.assigned_to)
    if (
        not has_management_access(current_user)
        and task_input.assigned_to
        and str(task_input.assigned_to) != str(current_user["user_id"])
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Colaboradores só podem atribuir tarefas a si mesmos.",
        )


def _task_status_value(task_status: TaskStatus | str) -> str:
    return task_status.value if isinstance(task_status, TaskStatus) else task_status


def create_task(
    db: Session,
    current_user: dict,
    task_input: schemas.TaskCreate,
) -> models.Task:
    require_permission(current_user, Permission.TASK_WRITE)
    tenant_id = tenant_repository(db, current_user).context.tenant_id
    _validate_task_relationships(db, current_user, task_input)

    assigned_to = task_input.assigned_to
    if not has_management_access(current_user) and not assigned_to:
        assigned_to = current_user["user_id"]

    task = models.Task(
        tenant_id=tenant_id,
        client_id=task_input.client_id,
        title=task_input.title,
        description=task_input.description,
        due_date=adjust_to_business_day(task_input.due_date),
        status=_task_status_value(task_input.status),
        assigned_to=assigned_to,
        grau_importancia=task_input.grau_importancia,
        is_recurring=task_input.is_recurring,
        recurrence_day=task_input.recurrence_day,
    )
    initialize_task_recurrence(task, task_input.due_date)

    db.add(task)
    if task.status == TaskStatus.CONCLUIDA.value:
        db.flush()
        ensure_next_occurrence(db, task)
    db.commit()
    db.refresh(task)
    return task


def complete_task(
    db: Session,
    current_user: dict,
    task_id: UUID,
) -> models.Task:
    return change_task_status(db, current_user, task_id, TaskStatus.CONCLUIDA)


def change_task_status(
    db: Session,
    current_user: dict,
    task_id: UUID,
    task_status: TaskStatus,
) -> models.Task:
    require_permission(current_user, Permission.TASK_WRITE)
    task = get_accessible_task(db, task_id, current_user, for_update=True)
    task.status = task_status.value
    if task_status == TaskStatus.CONCLUIDA:
        ensure_next_occurrence(db, task)
    db.commit()
    db.refresh(task)
    return task


def delete_task(db: Session, current_user: dict, task_id: UUID) -> None:
    require_permission(current_user, Permission.TASK_DELETE)
    task = get_accessible_task(db, task_id, current_user, for_update=True)
    db.delete(task)
    db.commit()


def update_task(
    db: Session,
    current_user: dict,
    task_id: UUID,
    task_input: schemas.TaskCreate,
) -> models.Task:
    require_permission(current_user, Permission.TASK_WRITE)
    task = get_accessible_task(db, task_id, current_user, for_update=True)
    _validate_task_relationships(db, current_user, task_input)

    task.title = task_input.title
    task.description = task_input.description
    task.client_id = task_input.client_id
    task.due_date = adjust_to_business_day(task_input.due_date)
    task.grau_importancia = task_input.grau_importancia
    task.status = _task_status_value(task_input.status)
    task.assigned_to = (
        task_input.assigned_to
        if has_management_access(current_user)
        else current_user["user_id"]
    )

    was_recurring = task.is_recurring
    task.is_recurring = task_input.is_recurring
    task.recurrence_day = task_input.recurrence_day
    initialize_task_recurrence(
        task,
        task_input.due_date,
        restart_series=task.is_recurring and not was_recurring,
    )
    if task.status == TaskStatus.CONCLUIDA.value:
        ensure_next_occurrence(db, task)

    db.commit()
    db.refresh(task)
    return task
