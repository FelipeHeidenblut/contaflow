import csv
import io
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
from typing import Iterable, Iterator, Literal, Optional
from uuid import UUID

import models
from database import get_db
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from plan_config import PAID_PLAN_IDS, PLAN_CONFIG, get_monthly_equivalent
from pydantic import BaseModel, ConfigDict, Field
from security import get_super_admin
from sqlalchemy import case, func, or_
from sqlalchemy.orm import Session, aliased

router = APIRouter(prefix="/api/v1/admin", tags=["Super Admin Backoffice"])


class AdminStatusUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    status: Literal["ativo", "inadimplente", "aguardando_pagamento"]
    reason: str = Field(..., min_length=3, max_length=500)


def _month_start(value: date) -> date:
    return value.replace(day=1)


def _shift_month(value: date, offset: int) -> date:
    index = value.year * 12 + value.month - 1 + offset
    return date(index // 12, index % 12 + 1, 1)


def _percentage_change(current: float, previous: float) -> float | None:
    if previous == 0:
        return None if current == 0 else 100.0
    return round(((current - previous) / previous) * 100, 1)


def _mask_provider_id(value: str | None) -> str | None:
    return f"••••{value[-6:]}" if value else None


def _latest_activity(*values):
    return max((value for value in values if value is not None), default=None)


def _tenant_aggregate_query(db: Session):
    profiles = (
        db.query(
            models.Profile.tenant_id.label("tenant_id"),
            func.count(models.Profile.id).label("user_count"),
            func.max(models.Profile.created_at).label("last_profile_at"),
            func.max(
                case((models.Profile.role == "admin", models.Profile.email), else_=None)
            ).label("admin_email"),
        )
        .group_by(models.Profile.tenant_id)
        .subquery()
    )
    clients = (
        db.query(
            models.Client.tenant_id.label("tenant_id"),
            func.count(models.Client.id).label("client_count"),
        )
        .filter(models.Client.ativo.is_(True))
        .group_by(models.Client.tenant_id)
        .subquery()
    )
    tasks = (
        db.query(
            models.Task.tenant_id.label("tenant_id"),
            func.count(models.Task.id).label("task_count"),
            func.max(models.Task.created_at).label("last_task_at"),
        )
        .group_by(models.Task.tenant_id)
        .subquery()
    )
    documents = (
        db.query(
            models.Document.tenant_id.label("tenant_id"),
            func.max(models.Document.created_at).label("last_document_at"),
        )
        .group_by(models.Document.tenant_id)
        .subquery()
    )
    comments = (
        db.query(
            models.Comment.tenant_id.label("tenant_id"),
            func.max(models.Comment.created_at).label("last_comment_at"),
        )
        .group_by(models.Comment.tenant_id)
        .subquery()
    )
    query = (
        db.query(
            models.Tenant,
            profiles.c.user_count,
            profiles.c.admin_email,
            profiles.c.last_profile_at,
            clients.c.client_count,
            tasks.c.task_count,
            tasks.c.last_task_at,
            documents.c.last_document_at,
            comments.c.last_comment_at,
        )
        .outerjoin(profiles, profiles.c.tenant_id == models.Tenant.id)
        .outerjoin(clients, clients.c.tenant_id == models.Tenant.id)
        .outerjoin(tasks, tasks.c.tenant_id == models.Tenant.id)
        .outerjoin(documents, documents.c.tenant_id == models.Tenant.id)
        .outerjoin(comments, comments.c.tenant_id == models.Tenant.id)
    )
    columns = {
        "user_count": profiles.c.user_count,
        "client_count": clients.c.client_count,
        "admin_email": profiles.c.admin_email,
        "last_activity": func.greatest(
            profiles.c.last_profile_at,
            tasks.c.last_task_at,
            documents.c.last_document_at,
            comments.c.last_comment_at,
        ),
    }
    return query, columns


def _apply_filters(query, columns, search, plan, payment_status):
    if search:
        term = f"%{search.strip()}%"
        query = query.filter(
            or_(models.Tenant.razao_social.ilike(term), columns["admin_email"].ilike(term))
        )
    if plan:
        query = query.filter(models.Tenant.plano == plan)
    if payment_status:
        query = query.filter(models.Tenant.status_pagamento == payment_status)
    return query


def _serialize_tenant(row) -> dict:
    tenant, users, email, last_profile, clients, tasks, last_task, last_doc, last_comment = row
    return {
        "id": tenant.id,
        "razao_social": tenant.razao_social,
        "plano": tenant.plano,
        "billing_cycle": tenant.billing_cycle,
        "status_pagamento": tenant.status_pagamento,
        "admin_email": email or "N/A",
        "created_at": tenant.created_at,
        "user_count": users or 0,
        "client_count": clients or 0,
        "task_count": tasks or 0,
        "last_activity_at": _latest_activity(last_profile, last_task, last_doc, last_comment),
    }


def _safe_csv_cell(value: object) -> str:
    """Evita que planilhas interpretem conteúdo controlado pelo usuário como fórmula."""
    text = "" if value is None else str(value)
    if text.startswith(("\t", "\r")) or text.lstrip().startswith(
        ("=", "+", "-", "@")
    ):
        return f"'{text}"
    return text


def _stream_tenant_export(rows: Iterable[object]) -> Iterator[str]:
    """Gera o CSV linha a linha, sem manter toda a exportação em memória."""
    output = io.StringIO(newline="")
    writer = csv.writer(output, delimiter=";")
    writer.writerow(
        [
            "Escritório",
            "Administrador",
            "Plano",
            "Ciclo",
            "Status",
            "Usuários",
            "Clientes",
            "Cadastro",
            "Última atividade",
        ]
    )
    yield "\ufeff" + output.getvalue()
    output.seek(0)
    output.truncate(0)

    for row in rows:
        item = _serialize_tenant(row)
        writer.writerow(
            [
                _safe_csv_cell(item["razao_social"]),
                _safe_csv_cell(item["admin_email"]),
                item["plano"],
                item["billing_cycle"],
                item["status_pagamento"],
                item["user_count"],
                item["client_count"],
                item["created_at"].isoformat(),
                item["last_activity_at"].isoformat()
                if item["last_activity_at"]
                else "",
            ]
        )
        yield output.getvalue()
        output.seek(0)
        output.truncate(0)


def _financial_metrics(db: Session, tenants: list[models.Tenant], month: date) -> dict:
    active_paid = [
        tenant
        for tenant in tenants
        if tenant.status_pagamento == "ativo" and tenant.plano in PAID_PLAN_IDS
    ]
    latest_dates = (
        db.query(
            models.PaymentRecord.tenant_id,
            func.max(models.PaymentRecord.paid_at).label("latest_paid_at"),
        )
        .filter(models.PaymentRecord.status == "received")
        .group_by(models.PaymentRecord.tenant_id)
        .subquery()
    )
    payments = (
        db.query(models.PaymentRecord)
        .join(
            latest_dates,
            (models.PaymentRecord.tenant_id == latest_dates.c.tenant_id)
            & (models.PaymentRecord.paid_at == latest_dates.c.latest_paid_at),
        )
        .filter(models.PaymentRecord.status == "received")
        .all()
    )
    actual = {str(payment.tenant_id): Decimal(payment.value) for payment in payments}
    mrr = sum(
        (
            (
                actual[str(tenant.id)] / 12
                if tenant.billing_cycle == "annual" and str(tenant.id) in actual
                else actual[str(tenant.id)]
                if str(tenant.id) in actual
                else get_monthly_equivalent(tenant.plano, tenant.billing_cycle)
            )
            for tenant in active_paid
        ),
        Decimal("0.00"),
    )
    next_month = _shift_month(month, 1)
    previous_month = _shift_month(month, -1)

    def revenue(start, end):
        return (
            db.query(func.coalesce(func.sum(models.PaymentRecord.value), 0))
            .filter(
                models.PaymentRecord.status == "received",
                models.PaymentRecord.paid_at >= start,
                models.PaymentRecord.paid_at < end,
            )
            .scalar()
            or 0
        )

    return {
        "mrr": float(mrr),
        "mrr_actual_coverage": round(
            (sum(str(tenant.id) in actual for tenant in active_paid) / len(active_paid)) * 100
        )
        if active_paid
        else 100,
        "paying_offices": len(active_paid),
        "average_ticket": float(mrr / len(active_paid)) if active_paid else 0,
        "revenue_current": float(revenue(month, next_month)),
        "revenue_previous": float(revenue(previous_month, month)),
    }


@router.get("/overview")
def get_admin_overview(
    months: int = Query(6, ge=3, le=12),
    db: Session = Depends(get_db),
    _admin_user: dict = Depends(get_super_admin),
):
    now = datetime.now(timezone.utc)
    current_month = _month_start(now.date())
    previous_month = _shift_month(current_month, -1)
    tenants = db.query(models.Tenant).all()
    finances = _financial_metrics(db, tenants, current_month)
    new_current = sum(tenant.created_at.date() >= current_month for tenant in tenants)
    new_previous = sum(
        previous_month <= tenant.created_at.date() < current_month for tenant in tenants
    )
    delinquent = sum(tenant.status_pagamento == "inadimplente" for tenant in tenants)
    pending = sum(tenant.status_pagamento == "aguardando_pagamento" for tenant in tenants)
    total_users = db.query(func.count(models.Profile.id)).scalar() or 0
    total_clients = (
        db.query(func.count(models.Client.id)).filter(models.Client.ativo.is_(True)).scalar()
        or 0
    )

    plan_counts = {plan_id: 0 for plan_id in PLAN_CONFIG}
    for tenant in tenants:
        plan_counts[tenant.plano] = plan_counts.get(tenant.plano, 0) + 1

    trend_start = _shift_month(current_month, -(months - 1))
    signup_rows = (
        db.query(
            func.extract("year", models.Tenant.created_at),
            func.extract("month", models.Tenant.created_at),
            func.count(models.Tenant.id),
        )
        .filter(models.Tenant.created_at >= trend_start)
        .group_by(
            func.extract("year", models.Tenant.created_at),
            func.extract("month", models.Tenant.created_at),
        )
        .all()
    )
    revenue_rows = (
        db.query(
            func.extract("year", models.PaymentRecord.paid_at),
            func.extract("month", models.PaymentRecord.paid_at),
            func.coalesce(func.sum(models.PaymentRecord.value), 0),
        )
        .filter(
            models.PaymentRecord.status == "received",
            models.PaymentRecord.paid_at >= trend_start,
        )
        .group_by(
            func.extract("year", models.PaymentRecord.paid_at),
            func.extract("month", models.PaymentRecord.paid_at),
        )
        .all()
    )
    signups = {(int(y), int(m)): int(count) for y, m, count in signup_rows}
    revenues = {(int(y), int(m)): float(value) for y, m, value in revenue_rows}
    month_names = ("Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez")
    trend = []
    for offset in range(-(months - 1), 1):
        value = _shift_month(current_month, offset)
        key = (value.year, value.month)
        trend.append(
            {
                "month": value.isoformat(),
                "label": f"{month_names[value.month - 1]}/{str(value.year)[2:]}",
                "signups": signups.get(key, 0),
                "revenue": revenues.get(key, 0),
            }
        )

    aggregate_rows = _tenant_aggregate_query(db)[0].all()
    inactive = near_limit = 0
    inactivity_cutoff = now - timedelta(days=7)
    for row in aggregate_rows:
        tenant = row[0]
        data = _serialize_tenant(row)
        inactive += int(
            tenant.created_at < inactivity_cutoff
            and data["client_count"] == 0
            and data["task_count"] == 0
        )
        config = PLAN_CONFIG.get(tenant.plano, PLAN_CONFIG["free"])
        near_limit += int(
            bool(config["clients"] and data["client_count"] >= config["clients"] * 0.8)
            or bool(config["members"] and data["user_count"] >= config["members"] * 0.8)
        )
    failed_webhooks = (
        db.query(func.count(models.AsaasWebhookEvent.id))
        .filter(
            models.AsaasWebhookEvent.status.in_({"failed", "dead"}),
            models.AsaasWebhookEvent.created_at >= now - timedelta(days=7),
        )
        .scalar()
        or 0
    )
    attention = [
        ("delinquent", "critical", "Escritórios inadimplentes", "Contas bloqueadas que exigem acompanhamento.", delinquent, "inadimplente"),
        ("pending", "warning", "Pagamentos pendentes", "Assinaturas aguardando confirmação.", pending, "aguardando_pagamento"),
        ("webhooks", "critical", "Falhas de integração", "Webhooks do Asaas com falha em sete dias.", failed_webhooks, None),
        ("near_limit", "info", "Próximos do limite", "Contas usando pelo menos 80% do plano.", near_limit, None),
        ("inactive", "info", "Cadastros sem ativação", "Contas antigas sem clientes ou tarefas.", inactive, None),
    ]
    attention_items = [
        {
            "type": item[0],
            "severity": item[1],
            "title": item[2],
            "description": item[3],
            "count": item[4],
            "filter_status": item[5],
        }
        for item in attention
    ]
    return {
        "generated_at": now,
        "stats": {
            "mrr": finances["mrr"],
            "mrr_actual_coverage": finances["mrr_actual_coverage"],
            "paying_offices": finances["paying_offices"],
            "new_offices_month": new_current,
            "new_offices_change_pct": _percentage_change(new_current, new_previous),
            "delinquency_rate": round((delinquent / len(tenants)) * 100, 1) if tenants else 0,
            "total_users": total_users,
            "total_clients": total_clients,
            "average_ticket": finances["average_ticket"],
            "revenue_month": finances["revenue_current"],
            "revenue_change_pct": _percentage_change(
                finances["revenue_current"], finances["revenue_previous"]
            ),
        },
        "plans": [
            {"id": plan_id, "name": config["name"], "count": plan_counts[plan_id]}
            for plan_id, config in PLAN_CONFIG.items()
        ],
        "trend": trend,
        "attention": {
            "total": sum(item["count"] for item in attention_items),
            "items": attention_items,
        },
    }


@router.get("/dashboard-stats")
def get_legacy_dashboard_stats(
    db: Session = Depends(get_db), admin_user: dict = Depends(get_super_admin)
):
    overview = get_admin_overview(6, db, admin_user)
    total = db.query(func.count(models.Tenant.id)).scalar() or 0
    active = db.query(func.count(models.Tenant.id)).filter(models.Tenant.status_pagamento == "ativo").scalar() or 0
    delinquent = db.query(func.count(models.Tenant.id)).filter(models.Tenant.status_pagamento == "inadimplente").scalar() or 0
    return {
        "mrr_estimado": overview["stats"]["mrr"],
        "total_escritorios": total,
        "escritorios_ativos": active,
        "escritorios_inadimplentes": delinquent,
        "total_usuarios": overview["stats"]["total_users"],
        "total_clientes_finais": overview["stats"]["total_clients"],
    }


@router.get("/tenants")
def list_tenants(
    search: Optional[str] = Query(None, max_length=120),
    plan: Optional[
        Literal["free", "basico", "profissional", "escritorio", "business"]
    ] = None,
    payment_status: Optional[
        Literal[
            "ativo",
            "inadimplente",
            "aguardando_pagamento",
            "estornado",
            "cancelado",
            "chargeback",
        ]
    ] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=5, le=100),
    sort_by: Literal["created_at", "name", "users", "clients", "last_activity"] = "created_at",
    sort_order: Literal["asc", "desc"] = "desc",
    db: Session = Depends(get_db),
    _admin_user: dict = Depends(get_super_admin),
):
    query, columns = _tenant_aggregate_query(db)
    query = _apply_filters(query, columns, search, plan, payment_status)
    total = query.count()
    sort_columns = {
        "created_at": models.Tenant.created_at,
        "name": models.Tenant.razao_social,
        "users": func.coalesce(columns["user_count"], 0),
        "clients": func.coalesce(columns["client_count"], 0),
        "last_activity": columns["last_activity"],
    }
    sort_column = sort_columns[sort_by]
    query = query.order_by(sort_column.asc() if sort_order == "asc" else sort_column.desc())
    rows = query.offset((page - 1) * page_size).limit(page_size).all()
    return {
        "items": [_serialize_tenant(row) for row in rows],
        "page": page,
        "page_size": page_size,
        "total": total,
        "pages": max(1, (total + page_size - 1) // page_size),
    }


@router.get("/tenants/export")
def export_tenants(
    search: Optional[str] = Query(None, max_length=120),
    plan: Optional[
        Literal["free", "basico", "profissional", "escritorio", "business"]
    ] = None,
    payment_status: Optional[
        Literal[
            "ativo",
            "inadimplente",
            "aguardando_pagamento",
            "estornado",
            "cancelado",
            "chargeback",
        ]
    ] = None,
    db: Session = Depends(get_db),
    _admin_user: dict = Depends(get_super_admin),
):
    query, columns = _tenant_aggregate_query(db)
    rows = (
        _apply_filters(query, columns, search, plan, payment_status)
        .order_by(models.Tenant.created_at.desc())
        .yield_per(250)
    )
    return StreamingResponse(
        _stream_tenant_export(rows),
        media_type="text/csv; charset=utf-8",
        headers={
            "Content-Disposition": 'attachment; filename="escritorios-contablytask.csv"',
            "Cache-Control": "private, no-store",
            "X-Accel-Buffering": "no",
            "X-Content-Type-Options": "nosniff",
        },
    )


@router.get("/tenants/{tenant_id}")
def get_tenant_detail(
    tenant_id: UUID,
    db: Session = Depends(get_db),
    _admin_user: dict = Depends(get_super_admin),
):
    tenant = db.query(models.Tenant).filter(models.Tenant.id == tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="Escritório não encontrado.")
    members = db.query(models.Profile).filter(models.Profile.tenant_id == tenant_id).order_by(models.Profile.created_at).all()
    clients = db.query(func.count(models.Client.id)).filter(models.Client.tenant_id == tenant_id, models.Client.ativo.is_(True)).scalar() or 0
    tasks = db.query(func.count(models.Task.id)).filter(models.Task.tenant_id == tenant_id).scalar() or 0
    last_activity = _latest_activity(
        db.query(func.max(models.Profile.created_at)).filter(models.Profile.tenant_id == tenant_id).scalar(),
        db.query(func.max(models.Task.created_at)).filter(models.Task.tenant_id == tenant_id).scalar(),
        db.query(func.max(models.Document.created_at)).filter(models.Document.tenant_id == tenant_id).scalar(),
        db.query(func.max(models.Comment.created_at)).filter(models.Comment.tenant_id == tenant_id).scalar(),
    )
    payments = db.query(models.PaymentRecord).filter(models.PaymentRecord.tenant_id == tenant_id).order_by(models.PaymentRecord.updated_at.desc()).limit(10).all()
    actor = aliased(models.Profile)
    audits = db.query(models.AdminAuditLog, actor.name).outerjoin(actor, models.AdminAuditLog.actor_profile_id == actor.id).filter(models.AdminAuditLog.tenant_id == tenant_id).order_by(models.AdminAuditLog.created_at.desc()).limit(15).all()
    config = PLAN_CONFIG.get(tenant.plano, PLAN_CONFIG["free"])
    return {
        "id": tenant.id,
        "razao_social": tenant.razao_social,
        "cnpj": tenant.cnpj,
        "plano": tenant.plano,
        "billing_cycle": tenant.billing_cycle,
        "status_pagamento": tenant.status_pagamento,
        "created_at": tenant.created_at,
        "last_activity_at": last_activity,
        "usage": {"users": len(members), "user_limit": config["members"], "clients": clients, "client_limit": config["clients"], "tasks": tasks},
        "provider": {"customer_id": _mask_provider_id(tenant.asaas_customer_id), "subscription_id": _mask_provider_id(tenant.asaas_subscription_id)},
        "members": [{"id": member.id, "name": member.name, "email": member.email, "role": member.role} for member in members],
        "payments": [{"id": payment.id, "value": float(payment.value), "status": payment.status, "due_date": payment.due_date, "paid_at": payment.paid_at, "invoice_url": payment.invoice_url} for payment in payments],
        "audit": [{"id": log.id, "action": log.action, "reason": log.reason, "old_value": log.old_value, "new_value": log.new_value, "actor_name": actor_name or "Automação Asaas", "created_at": log.created_at} for log, actor_name in audits],
    }


@router.patch("/tenants/{tenant_id}/status")
def update_tenant_status(
    tenant_id: UUID,
    payload: AdminStatusUpdate,
    db: Session = Depends(get_db),
    admin_user: dict = Depends(get_super_admin),
):
    tenant = db.query(models.Tenant).filter(models.Tenant.id == tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="Escritório não encontrado.")
    if tenant.status_pagamento == payload.status:
        raise HTTPException(status_code=409, detail="O escritório já possui esse status.")
    old_status = tenant.status_pagamento
    tenant.status_pagamento = payload.status
    tenant.subscription_status = {
        "ativo": "active",
        "inadimplente": "overdue",
        "aguardando_pagamento": "pending",
    }[payload.status]
    tenant.billing_status_updated_at = datetime.now(timezone.utc)
    db.add(
        models.AdminAuditLog(
            tenant_id=tenant.id,
            actor_profile_id=admin_user["user_id"],
            action="manual_status_change",
            reason=payload.reason.strip(),
            old_value=old_status,
            new_value=payload.status,
        )
    )
    db.commit()
    return {"status": "success", "new_status": payload.status}
