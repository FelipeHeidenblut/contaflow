import calendar
import logging
import os
import secrets
import uuid
from datetime import date, datetime, timedelta, timezone

import models
from enums import TaskStatus
from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


def adjust_to_business_day(due_date: date) -> date:
    """Move vencimentos de sábado ou domingo para a segunda-feira."""
    if due_date.weekday() == 5:
        return due_date + timedelta(days=2)
    if due_date.weekday() == 6:
        return due_date + timedelta(days=1)
    return due_date


def recurrence_period_for(due_date: date) -> date:
    """Representa a competência mensal, independentemente do dia útil ajustado."""
    return due_date.replace(day=1)


def next_recurrence_period(period: date) -> date:
    if period.month == 12:
        return date(period.year + 1, 1, 1)
    return date(period.year, period.month + 1, 1)


def recurrence_due_date(period: date, recurrence_day: int) -> date:
    last_day = calendar.monthrange(period.year, period.month)[1]
    nominal_due_date = date(period.year, period.month, min(recurrence_day, last_day))
    return adjust_to_business_day(nominal_due_date)


def initialize_task_recurrence(
    task: models.Task,
    nominal_due_date: date,
    *,
    restart_series: bool = False,
) -> None:
    """Inicializa a identidade da série sem alterar séries já em andamento."""
    if not task.is_recurring:
        return

    if restart_series or not task.recurrence_series_id:
        task.recurrence_series_id = uuid.uuid4()
        task.recurrence_period = recurrence_period_for(nominal_due_date)
        task.next_occurrence_id = None
        task.recurrence_processed_at = None
    elif not task.recurrence_period:
        task.recurrence_period = recurrence_period_for(nominal_due_date)


def _find_occurrence(
    db: Session,
    tenant_id: uuid.UUID,
    series_id: uuid.UUID,
    period: date,
) -> models.Task | None:
    return (
        db.query(models.Task)
        .filter(
            models.Task.tenant_id == tenant_id,
            models.Task.recurrence_series_id == series_id,
            models.Task.recurrence_period == period,
        )
        .first()
    )


def ensure_next_occurrence(
    db: Session, task: models.Task
) -> tuple[models.Task | None, bool]:
    """Garante, de forma idempotente, uma única tarefa para a próxima competência."""
    if (
        not task.is_recurring
        or not task.recurrence_day
        or not task.recurrence_series_id
        or not task.recurrence_period
    ):
        return None, False

    if task.recurrence_processed_at:
        if task.next_occurrence_id:
            existing = (
                db.query(models.Task)
                .filter(
                    models.Task.id == task.next_occurrence_id,
                    models.Task.tenant_id == task.tenant_id,
                )
                .first()
            )
            return existing, False
        return None, False

    target_period = next_recurrence_period(task.recurrence_period)
    next_task = _find_occurrence(
        db,
        task.tenant_id,
        task.recurrence_series_id,
        target_period,
    )
    created = False

    if not next_task:
        next_task = models.Task(
            id=uuid.uuid4(),
            tenant_id=task.tenant_id,
            client_id=task.client_id,
            title=task.title,
            description=task.description,
            due_date=recurrence_due_date(target_period, task.recurrence_day),
            status=TaskStatus.PENDENTE.value,
            assigned_to=task.assigned_to,
            grau_importancia=task.grau_importancia,
            is_recurring=True,
            recurrence_day=task.recurrence_day,
            recurrence_series_id=task.recurrence_series_id,
            recurrence_period=target_period,
        )
        try:
            with db.begin_nested():
                db.add(next_task)
                db.flush()
            created = True
        except IntegrityError:
            # Outro worker pode ter criado a mesma competência no intervalo.
            next_task = _find_occurrence(
                db,
                task.tenant_id,
                task.recurrence_series_id,
                target_period,
            )
            if not next_task:
                raise

    task.next_occurrence_id = next_task.id
    task.recurrence_processed_at = datetime.now(timezone.utc)
    return next_task, created


def run_recurrence_reconciliation(
    db: Session, batch_size: int = 1000
) -> dict[str, int | str]:
    """Reprocessa conclusões interrompidas e registra o resultado operacional."""
    run = models.RecurrenceRun(status="running")
    db.add(run)
    db.commit()
    db.refresh(run)

    processed = 0
    created = 0
    try:
        tasks = (
            db.query(models.Task)
            .filter(
                models.Task.status == TaskStatus.CONCLUIDA.value,
                models.Task.is_recurring.is_(True),
                models.Task.recurrence_processed_at.is_(None),
                models.Task.recurrence_series_id.isnot(None),
                models.Task.recurrence_period.isnot(None),
            )
            .order_by(models.Task.due_date, models.Task.id)
            .with_for_update(skip_locked=True)
            .limit(batch_size)
            .all()
        )
        for task in tasks:
            _, was_created = ensure_next_occurrence(db, task)
            processed += 1
            created += int(was_created)

        run.status = "success"
        run.processed_tasks = processed
        run.created_tasks = created
        run.finished_at = datetime.now(timezone.utc)
        db.commit()
    except Exception as error:
        db.rollback()
        failed_run = (
            db.query(models.RecurrenceRun)
            .filter(models.RecurrenceRun.id == run.id)
            .first()
        )
        if failed_run:
            failed_run.status = "failed"
            failed_run.processed_tasks = processed
            failed_run.created_tasks = created
            failed_run.error = str(error)[:1000]
            failed_run.finished_at = datetime.now(timezone.utc)
            db.commit()
        logger.exception("Falha ao reconciliar recorrências no lote %s", run.id)
        raise

    return {
        "run_id": str(run.id),
        "processed_tasks": processed,
        "created_tasks": created,
    }


def verify_recurrence_cron_secret(received_secret: str | None) -> None:
    configured_secret = os.getenv("RECURRENCE_CRON_SECRET")
    if not configured_secret or len(configured_secret) < 32:
        logger.error("RECURRENCE_CRON_SECRET não configurado.")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Processador de recorrências não configurado.",
        )
    if not received_secret or not secrets.compare_digest(received_secret, configured_secret):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credencial inválida.",
        )
