from datetime import datetime
from typing import Any, Literal, Sequence
from zoneinfo import ZoneInfo

import models
from access_control import apply_task_scope, tenant_repository
from enums import TaskStatus
from sqlalchemy import func
from sqlalchemy.orm import Session


def attach_task_counts(
    db: Session,
    current_user: dict,
    items: Sequence[Any],
    *,
    group_by: Literal["client_id", "assigned_to"],
) -> None:
    """Count the visible open tasks for this page with one grouped query."""
    if not items:
        return
    column = getattr(models.Task, group_by)
    today = datetime.now(ZoneInfo("America/Sao_Paulo")).date()
    query = apply_task_scope(
        tenant_repository(db, current_user).query(models.Task), current_user
    )
    counts = {
        identifier: (open_count, overdue_count)
        for identifier, open_count, overdue_count in query.filter(
            column.in_([item.id for item in items]),
            models.Task.status != TaskStatus.CONCLUIDA.value,
        ).with_entities(
            column,
            func.count(models.Task.id),
            func.count(models.Task.id).filter(models.Task.due_date < today),
        ).group_by(column).all()
    }
    for item in items:
        item.open_tasks_count, item.overdue_tasks_count = counts.get(item.id, (0, 0))
