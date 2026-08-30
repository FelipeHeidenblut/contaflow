"""Report aggregation, access rules and tenant-scoped queries."""

from collections import defaultdict
from datetime import date, datetime, timezone
from uuid import UUID
from zoneinfo import ZoneInfo

import models
from access_control import (
    Permission,
    apply_client_scope,
    apply_task_scope,
    get_accessible_client,
    require_permission,
    tenant_repository,
)
from enums import TaskStatus
from fastapi import HTTPException, status
from plan_config import PAID_PLAN_IDS
from sqlalchemy.orm import Session


REPORT_CAPABILITIES = {
    "basico": {
        "advanced": False,
        "can_export": False,
        "max_report_days": 92,
    },
    "profissional": {
        "advanced": True,
        "can_export": True,
        "max_report_days": 366,
    },
    "escritorio": {
        "advanced": True,
        "can_export": True,
        "max_report_days": 366,
    },
    "business": {
        "advanced": True,
        "can_export": True,
        "max_report_days": 366,
    },
}
NO_REPORT_CAPABILITIES = {
    "advanced": False,
    "can_export": False,
    "max_report_days": 0,
}
BUSINESS_TIMEZONE = ZoneInfo("America/Sao_Paulo")


def get_report_capabilities(plan: str) -> dict:
    return REPORT_CAPABILITIES.get(plan, NO_REPORT_CAPABILITIES).copy()


def business_date(reference: datetime | None = None) -> date:
    current = reference or datetime.now(timezone.utc)
    if current.tzinfo is None:
        current = current.replace(tzinfo=timezone.utc)
    return current.astimezone(BUSINESS_TIMEZONE).date()


def ensure_report_access(current_user: dict) -> dict:
    require_permission(current_user, Permission.REPORT_READ)
    if current_user.get("plan") not in PAID_PLAN_IDS:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Relatórios estão disponíveis somente nos planos pagos.",
        )
    if current_user.get("payment_status") != "ativo":
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail="Regularize a assinatura para acessar os relatórios.",
        )
    return current_user


def validate_report_request(
    current_user: dict,
    *,
    start_date: date,
    end_date: date,
    client_id: UUID | None,
    member_id: UUID | None,
    task_status: str | None,
) -> dict:
    capabilities = get_report_capabilities(current_user.get("plan", ""))
    if start_date > end_date:
        raise HTTPException(
            status_code=422,
            detail="A data inicial deve anteceder a data final.",
        )
    if (end_date - start_date).days > capabilities["max_report_days"]:
        period_label = "3 meses" if current_user.get("plan") == "basico" else "12 meses"
        raise HTTPException(
            status_code=422,
            detail=f"O período máximo do seu plano é de {period_label}.",
        )
    if (client_id or member_id) and not capabilities["advanced"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "Filtros por cliente e responsável estão disponíveis a partir do "
                "plano Profissional."
            ),
        )

    valid_statuses = {item.value for item in TaskStatus}
    if task_status and task_status not in valid_statuses:
        raise HTTPException(status_code=422, detail="Status de tarefa inválido.")
    return capabilities


def _month_key(value: date) -> str:
    return f"{value.year:04d}-{value.month:02d}"


def _month_label(year: int, month: int) -> str:
    names = (
        "",
        "Jan",
        "Fev",
        "Mar",
        "Abr",
        "Mai",
        "Jun",
        "Jul",
        "Ago",
        "Set",
        "Out",
        "Nov",
        "Dez",
    )
    return f"{names[month]}/{str(year)[2:]}"


def _month_range(start_date: date, end_date: date):
    year, month = start_date.year, start_date.month
    while (year, month) <= (end_date.year, end_date.month):
        yield year, month
        if month == 12:
            year, month = year + 1, 1
        else:
            month += 1


def build_report(
    tasks,
    clients,
    members,
    start_date: date,
    end_date: date,
    today: date,
):
    completed_status = TaskStatus.CONCLUIDA.value
    status_order = [
        TaskStatus.PENDENTE.value,
        TaskStatus.EM_ANDAMENTO.value,
        TaskStatus.AGUARDANDO_CLIENTE.value,
        completed_status,
    ]
    status_labels = {
        TaskStatus.PENDENTE.value: "Pendentes",
        TaskStatus.EM_ANDAMENTO.value: "Em andamento",
        TaskStatus.AGUARDANDO_CLIENTE.value: "Aguardando cliente",
        completed_status: "Concluídas",
    }

    client_map = {
        str(client.id): client.razao_social or client.nome or "Cliente sem nome"
        for client in clients
    }
    member_map = {str(member.id): member.name for member in members}

    status_counts = {item: 0 for item in status_order}
    client_stats = defaultdict(
        lambda: {"total": 0, "completed": 0, "open": 0, "overdue": 0}
    )
    member_stats = defaultdict(
        lambda: {"total": 0, "completed": 0, "open": 0, "overdue": 0}
    )
    month_stats = defaultdict(lambda: {"total": 0, "completed": 0, "overdue": 0})

    total = completed = overdue = open_tasks = 0
    for task in tasks:
        total += 1
        is_completed = task.status == completed_status
        is_overdue = not is_completed and task.due_date < today
        completed += int(is_completed)
        overdue += int(is_overdue)
        open_tasks += int(not is_completed)
        status_counts[task.status] = status_counts.get(task.status, 0) + 1

        month = month_stats[_month_key(task.due_date)]
        month["total"] += 1
        month["completed"] += int(is_completed)
        month["overdue"] += int(is_overdue)

        client = client_stats[str(task.client_id)]
        client["total"] += 1
        client["completed"] += int(is_completed)
        client["open"] += int(not is_completed)
        client["overdue"] += int(is_overdue)

        member_key = str(task.assigned_to) if task.assigned_to else "unassigned"
        member = member_stats[member_key]
        member["total"] += 1
        member["completed"] += int(is_completed)
        member["open"] += int(not is_completed)
        member["overdue"] += int(is_overdue)

    completion_rate = round((completed / total) * 100) if total else 0
    clients_with_overdue = sum(1 for item in client_stats.values() if item["overdue"])

    timeline = []
    for year, month in _month_range(start_date, end_date):
        values = month_stats[f"{year:04d}-{month:02d}"]
        timeline.append(
            {
                "month": f"{year:04d}-{month:02d}",
                "label": _month_label(year, month),
                **values,
            }
        )

    client_rows = [
        {
            "id": client_id,
            "name": client_map.get(client_id, "Cliente"),
            **values,
            "completion_rate": round((values["completed"] / values["total"]) * 100),
        }
        for client_id, values in client_stats.items()
    ]
    client_rows.sort(key=lambda item: (-item["overdue"], -item["open"], item["name"]))

    member_rows = [
        {
            "id": None if member_id == "unassigned" else member_id,
            "name": member_map.get(member_id, "Sem responsável"),
            **values,
            "share": round((values["total"] / total) * 100) if total else 0,
            "completion_rate": round((values["completed"] / values["total"]) * 100),
        }
        for member_id, values in member_stats.items()
    ]
    member_rows.sort(key=lambda item: (-item["total"], item["name"]))

    return {
        "period": {"start": start_date.isoformat(), "end": end_date.isoformat()},
        "summary": {
            "total": total,
            "completed": completed,
            "open": open_tasks,
            "overdue": overdue,
            "completion_rate": completion_rate,
            "clients_with_overdue": clients_with_overdue,
        },
        "status_distribution": [
            {
                "status": item,
                "label": status_labels.get(item, item.replace("_", " ").title()),
                "value": status_counts.get(item, 0),
                "percentage": (
                    round((status_counts.get(item, 0) / total) * 100) if total else 0
                ),
            }
            for item in status_order
        ],
        "timeline": timeline,
        "clients": client_rows,
        "team": member_rows,
        "filters": {
            "clients": [
                {"id": str(client.id), "name": client_map[str(client.id)]}
                for client in clients
                if client.ativo
            ],
            "members": [
                {"id": str(member.id), "name": member.name} for member in members
            ],
        },
    }


def generate_report(
    db: Session,
    current_user: dict,
    *,
    start_date: date,
    end_date: date,
    today: date | None = None,
    client_id: UUID | None = None,
    member_id: UUID | None = None,
    task_status: str | None = None,
) -> dict:
    ensure_report_access(current_user)
    capabilities = validate_report_request(
        current_user,
        start_date=start_date,
        end_date=end_date,
        client_id=client_id,
        member_id=member_id,
        task_status=task_status,
    )
    repository = tenant_repository(db, current_user)
    if client_id:
        get_accessible_client(db, client_id, current_user)
    if member_id:
        member = (
            repository.query(models.Profile)
            .filter(models.Profile.id == member_id)
            .first()
        )
        if not member:
            raise HTTPException(status_code=404, detail="Responsável não encontrado.")

    task_query = repository.query(models.Task).filter(
        models.Task.due_date >= start_date,
        models.Task.due_date <= end_date,
    )
    if client_id:
        task_query = task_query.filter(models.Task.client_id == client_id)
    if member_id:
        task_query = task_query.filter(models.Task.assigned_to == member_id)
    if task_status:
        task_query = task_query.filter(models.Task.status == task_status)
    task_query = apply_task_scope(task_query, current_user)

    clients = []
    members = []
    if capabilities["advanced"]:
        client_query = repository.query(models.Client)
        clients = apply_client_scope(client_query, current_user).all()
        members = repository.query(models.Profile).all()

    report = build_report(
        task_query.all(),
        clients,
        members,
        start_date,
        end_date,
        today or business_date(),
    )
    if not capabilities["advanced"]:
        report["clients"] = []
        report["team"] = []
        report["filters"] = {"clients": [], "members": []}
    report["access"] = {
        "plan": current_user["plan"],
        "paid": True,
        **capabilities,
    }
    return report
