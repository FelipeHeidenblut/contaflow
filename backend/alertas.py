import html
import logging
import os
import secrets
import smtplib
import ssl
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from email.message import EmailMessage
from typing import Literal
from zoneinfo import ZoneInfo

import models
from database import get_db
from enums import TaskStatus
from fastapi import APIRouter, Depends, Header, HTTPException, status
from pydantic import BaseModel, ConfigDict
from security import get_active_user
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/alertas", tags=["Alertas de vencimento"])

ALLOWED_LEAD_HOURS = {48, 72, 168}
MAX_SEND_ATTEMPTS = 5
BUSINESS_TIMEZONE = ZoneInfo("America/Sao_Paulo")


@dataclass(frozen=True)
class DeadlineEmail:
    recipient: str
    recipient_name: str
    client_name: str
    task_title: str
    due_date: date
    lead_hours: int


class AlertPreferences(BaseModel):
    model_config = ConfigDict(extra="forbid")
    deadline_alerts_enabled: bool = False
    alert_advance_hours: Literal[48, 72, 168] = 72


def is_due_for_alert(task_due_date: date, lead_hours: int, reference_date: date) -> bool:
    if lead_hours not in ALLOWED_LEAD_HOURS:
        return False
    return task_due_date == reference_date + timedelta(hours=lead_hours)


def lead_time_label(lead_hours: int) -> str:
    return {48: "2 dias", 72: "3 dias", 168: "1 semana"}.get(
        lead_hours, f"{lead_hours} horas"
    )


def _get_current_profile(db: Session, current_user: dict) -> models.Profile:
    profile = (
        db.query(models.Profile)
        .filter(
            models.Profile.id == current_user["user_id"],
            models.Profile.tenant_id == current_user["tenant_id"],
        )
        .first()
    )
    if not profile:
        raise HTTPException(status_code=404, detail="Perfil não encontrado.")
    return profile


@router.get("/preferencias")
def get_alert_preferences(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_active_user),
):
    profile = _get_current_profile(db, current_user)
    return {
        "email": profile.email,
        "deadline_alerts_enabled": profile.deadline_alerts_enabled,
        "alert_advance_hours": profile.alert_advance_hours,
    }


@router.put("/preferencias")
def update_alert_preferences(
    preferences: AlertPreferences,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_active_user),
):
    profile = _get_current_profile(db, current_user)
    if preferences.deadline_alerts_enabled and not profile.email:
        raise HTTPException(
            status_code=422,
            detail="Seu perfil precisa ter um e-mail para ativar os alertas.",
        )
    profile.deadline_alerts_enabled = preferences.deadline_alerts_enabled
    profile.alert_advance_hours = preferences.alert_advance_hours
    db.commit()
    db.refresh(profile)
    return {
        "email": profile.email,
        "deadline_alerts_enabled": profile.deadline_alerts_enabled,
        "alert_advance_hours": profile.alert_advance_hours,
    }


def send_deadline_email(payload: DeadlineEmail) -> None:
    host = os.getenv("SMTP_HOST")
    sender = os.getenv("ALERT_FROM_EMAIL") or os.getenv("CONTACT_FROM_EMAIL")
    if not host or not sender:
        raise RuntimeError("SMTP_HOST e ALERT_FROM_EMAIL não estão configurados.")

    port = int(os.getenv("SMTP_PORT", "587"))
    username = os.getenv("SMTP_USERNAME")
    password = os.getenv("SMTP_PASSWORD")
    use_ssl = os.getenv("SMTP_USE_SSL", "false").lower() == "true"
    use_tls = os.getenv("SMTP_USE_TLS", "true").lower() == "true"
    reply_to = os.getenv("ALERT_REPLY_TO")

    safe_title = " ".join(payload.task_title.splitlines()).strip()
    formatted_due_date = payload.due_date.strftime("%d/%m/%Y")
    advance = lead_time_label(payload.lead_hours)

    message = EmailMessage()
    message["Subject"] = f"Prazo próximo: {safe_title} vence em {advance}"
    message["From"] = sender
    message["To"] = payload.recipient
    if reply_to:
        message["Reply-To"] = reply_to
    message.set_content(
        "\n".join(
            [
                f"Olá, {payload.recipient_name}.",
                "",
                f"A tarefa “{safe_title}”, do cliente {payload.client_name}, vence em {advance}.",
                f"Data de vencimento: {formatted_due_date}.",
                "",
                "Acesse a ContablyTask para acompanhar ou atualizar o status da tarefa.",
                "",
                "Mensagem automática enviada pela ContablyTask.",
            ]
        )
    )
    message.add_alternative(
        f"""
        <!doctype html>
        <html lang="pt-BR">
          <body style="margin:0;background:#f4f7fb;font-family:Arial,sans-serif;color:#17213d">
            <div style="max-width:600px;margin:0 auto;padding:32px 16px">
              <div style="background:#fff;border:1px solid #e0e5ed;border-radius:14px;padding:28px">
                <p style="margin:0 0 8px;color:#2563eb;font-size:12px;font-weight:700;text-transform:uppercase;letter-spacing:.08em">Lembrete de prazo</p>
                <h1 style="margin:0 0 18px;font-size:24px;line-height:1.25">{html.escape(safe_title)}</h1>
                <p style="margin:0 0 18px;color:#52617a;line-height:1.6">Olá, {html.escape(payload.recipient_name)}. A tarefa do cliente <strong>{html.escape(payload.client_name)}</strong> está próxima do vencimento.</p>
                <div style="border-left:4px solid #2563eb;background:#eff6ff;border-radius:8px;padding:16px 18px">
                  <p style="margin:0;color:#52617a;font-size:13px">Vencimento</p>
                  <p style="margin:5px 0 0;font-size:18px;font-weight:700">{formatted_due_date} · em {advance}</p>
                </div>
                <p style="margin:20px 0 0;color:#6b7890;font-size:13px;line-height:1.6">Acesse a ContablyTask para acompanhar ou atualizar o status da tarefa.</p>
              </div>
              <p style="margin:14px 0 0;text-align:center;color:#94a3b8;font-size:11px">Mensagem automática enviada pela ContablyTask.</p>
            </div>
          </body>
        </html>
        """,
        subtype="html",
    )

    context = ssl.create_default_context()
    smtp_connection = (
        smtplib.SMTP_SSL(host, port, timeout=15, context=context)
        if use_ssl
        else smtplib.SMTP(host, port, timeout=15)
    )
    with smtp_connection as smtp:
        if use_tls and not use_ssl:
            smtp.starttls(context=context)
        if username and password:
            smtp.login(username, password)
        smtp.send_message(message)


def _claim_alert(
    db: Session,
    task: models.Task,
    client: models.Client,
    recipient: models.Profile,
) -> models.DeadlineAlert | None:
    existing = (
        db.query(models.DeadlineAlert)
        .filter(
            models.DeadlineAlert.task_id == task.id,
            models.DeadlineAlert.due_date == task.due_date,
            models.DeadlineAlert.lead_hours == recipient.alert_advance_hours,
            models.DeadlineAlert.recipient_profile_id == recipient.id,
        )
        .first()
    )
    if existing:
        if existing.status in {"sent", "processing"} or existing.attempts >= MAX_SEND_ATTEMPTS:
            return None
        existing.status = "processing"
        existing.attempts += 1
        existing.last_error = None
        existing.recipient_email = recipient.email
        db.commit()
        db.refresh(existing)
        return existing

    alert = models.DeadlineAlert(
        tenant_id=task.tenant_id,
        client_id=client.id,
        task_id=task.id,
        recipient_profile_id=recipient.id,
        due_date=task.due_date,
        lead_hours=recipient.alert_advance_hours,
        recipient_email=recipient.email,
    )
    db.add(alert)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        return None
    db.refresh(alert)
    return alert


def process_due_alerts(db: Session, reference_date: date | None = None) -> dict[str, int]:
    today = reference_date or datetime.now(BUSINESS_TIMEZONE).date()
    candidates = (
        db.query(models.Task, models.Client, models.Profile)
        .join(
            models.Client,
            (models.Task.client_id == models.Client.id)
            & (models.Task.tenant_id == models.Client.tenant_id),
        )
        .join(
            models.Profile,
            (models.Task.assigned_to == models.Profile.id)
            & (models.Task.tenant_id == models.Profile.tenant_id),
        )
        .filter(
            models.Client.ativo.is_(True),
            models.Profile.deadline_alerts_enabled.is_(True),
            models.Profile.email.isnot(None),
            models.Task.status != TaskStatus.CONCLUIDA.value,
            models.Task.due_date >= today,
            models.Task.due_date <= today + timedelta(days=7),
        )
        .all()
    )

    result = {"candidates": 0, "sent": 0, "failed": 0, "skipped": 0}
    for task, client, recipient in candidates:
        if not is_due_for_alert(task.due_date, recipient.alert_advance_hours, today):
            continue
        result["candidates"] += 1
        alert = _claim_alert(db, task, client, recipient)
        if not alert:
            result["skipped"] += 1
            continue

        client_name = client.razao_social or client.nome or "cliente"
        try:
            send_deadline_email(
                DeadlineEmail(
                    recipient=recipient.email,
                    recipient_name=recipient.name,
                    client_name=client_name,
                    task_title=task.title,
                    due_date=task.due_date,
                    lead_hours=recipient.alert_advance_hours,
                )
            )
        except (OSError, smtplib.SMTPException, RuntimeError, ValueError) as error:
            logger.exception("Falha ao enviar alerta de vencimento %s", alert.id)
            alert.status = "failed"
            alert.last_error = str(error)[:1000]
            result["failed"] += 1
        else:
            alert.status = "sent"
            alert.sent_at = datetime.now(timezone.utc)
            result["sent"] += 1
        db.commit()

    return result


def verify_cron_secret(received_secret: str | None) -> None:
    configured_secret = os.getenv("ALERT_CRON_SECRET")
    if not configured_secret or len(configured_secret) < 32:
        logger.error("ALERT_CRON_SECRET não configurado.")
        raise HTTPException(status_code=503, detail="Processador de alertas não configurado.")
    if not received_secret or not secrets.compare_digest(received_secret, configured_secret):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credencial inválida.")


@router.post("/processar")
def process_alerts_endpoint(
    x_cron_secret: str | None = Header(default=None, alias="X-Cron-Secret"),
    db: Session = Depends(get_db),
):
    verify_cron_secret(x_cron_secret)
    result = process_due_alerts(db)
    if result["failed"]:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"{result['failed']} alerta(s) não puderam ser enviados.",
        )
    return result
