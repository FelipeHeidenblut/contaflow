from collections import defaultdict
from datetime import date
from typing import Optional
from uuid import UUID

import models
from database import get_db
from enums import TaskStatus
from fastapi import APIRouter, Depends, HTTPException, Query, status
from security import get_current_user
from sqlalchemy.orm import Session

router = APIRouter(prefix="/api/v1/relatorios", tags=["Relatórios"])

PAID_PLANS = {"basico", "profissional", "business"}
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
    "business": {
        "advanced": True,
        "can_export": True,
        "max_report_days": 366,
    },
}


def get_report_capabilities(plan: str):
    return REPORT_CAPABILITIES.get(
        plan,
        {"advanced": False, "can_export": False, "max_report_days": 0},
    ).copy()


def require_paid_reports(
    db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)
):
    tenant = (
        db.query(models.Tenant)
        .filter(models.Tenant.id == current_user["tenant_id"])
        .first()
    )
    if not tenant:
        raise HTTPException(status_code=404, detail="Escritório não encontrado.")
    if tenant.plano not in PAID_PLANS:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Relatórios estão disponíveis somente nos planos pagos.",
        )
    if tenant.status_pagamento != "ativo":
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail="Regularize a assinatura para acessar os relatórios.",
        )
    return {**current_user, "plan": tenant.plano}


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


def build_report(tasks, clients, members, start_date: date, end_date: date, today: date):
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
    client_stats = defaultdict(lambda: {"total": 0, "completed": 0, "open": 0, "overdue": 0})
    member_stats = defaultdict(lambda: {"total": 0, "completed": 0, "open": 0, "overdue": 0})
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
                "percentage": round((status_counts.get(item, 0) / total) * 100) if total else 0,
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


@router.get("")
def get_reports(
    start_date: date = Query(...),
    end_date: date = Query(...),
    client_id: Optional[UUID] = Query(None),
    member_id: Optional[UUID] = Query(None),
    task_status: Optional[str] = Query(None, alias="status"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_paid_reports),
):
    capabilities = get_report_capabilities(current_user["plan"])
    if start_date > end_date:
        raise HTTPException(status_code=422, detail="A data inicial deve anteceder a data final.")
    if (end_date - start_date).days > capabilities["max_report_days"]:
        period_label = "3 meses" if current_user["plan"] == "basico" else "12 meses"
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

    tenant_id = current_user["tenant_id"]
    query = db.query(models.Task).filter(
        models.Task.tenant_id == tenant_id,
        models.Task.due_date >= start_date,
        models.Task.due_date <= end_date,
    )
    if client_id:
        query = query.filter(models.Task.client_id == client_id)
    if member_id:
        query = query.filter(models.Task.assigned_to == member_id)
    if task_status:
        query = query.filter(models.Task.status == task_status)

    clients = db.query(models.Client).filter(models.Client.tenant_id == tenant_id).all()
    members = db.query(models.Profile).filter(models.Profile.tenant_id == tenant_id).all()
    report = build_report(query.all(), clients, members, start_date, end_date, date.today())
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
