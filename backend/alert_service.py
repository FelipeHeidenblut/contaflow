"""Business rules and delivery adapter for deadline alerts."""

import html
import logging
import os
import secrets
import smtplib
import ssl
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from email.message import EmailMessage
from zoneinfo import ZoneInfo

import models
from access_control import Permission, require_permission, tenant_repository
from enums import TaskStatus
from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session


logger = logging.getLogger(__name__)

ALLOWED_LEAD_HOURS = {48, 72, 168}
MAX_SEND_ATTEMPTS = 5
PROCESSING_LEASE = timedelta(minutes=15)
BUSINESS_TIMEZONE = ZoneInfo("America/Sao_Paulo")


@dataclass(frozen=True)
class DeadlineEmail:
    recipient: str
    recipient_name: str
    client_name: str
    task_title: str
    due_date: date
    lead_hours: int


@dataclass(frozen=True)
class SmtpSettings:
    host: str
    port: int
    sender: str
    username: str | None
    password: str | None
    use_ssl: bool
    use_tls: bool
    reply_to: str | None

    @classmethod
    def from_mapping(cls, values: Mapping[str, str]) -> "SmtpSettings":
        def clean(name: str) -> str:
            return (values.get(name) or "").strip()

        def parse_bool(name: str, default: bool) -> bool:
            raw = clean(name)
            if not raw:
                return default
            if raw.lower() not in {"true", "false"}:
                raise RuntimeError(f"{name} deve ser true ou false.")
            return raw.lower() == "true"

        try:
            port = int(clean("SMTP_PORT") or "587")
        except ValueError as error:
            raise RuntimeError("SMTP_PORT deve ser um número inteiro.") from error

        return cls(
            host=clean("SMTP_HOST"),
            port=port,
            sender=clean("ALERT_FROM_EMAIL") or clean("CONTACT_FROM_EMAIL"),
            username=clean("SMTP_USERNAME") or None,
            password=clean("SMTP_PASSWORD") or None,
            use_ssl=parse_bool("SMTP_USE_SSL", False),
            use_tls=parse_bool("SMTP_USE_TLS", True),
            reply_to=clean("ALERT_REPLY_TO") or None,
        )

    def validate(self) -> None:
        if not self.host or not self.sender:
            raise RuntimeError("SMTP_HOST e ALERT_FROM_EMAIL não estão configurados.")
        if not 1 <= self.port <= 65535:
            raise RuntimeError("SMTP_PORT deve estar entre 1 e 65535.")
        if self.use_ssl and self.use_tls:
            raise RuntimeError("Configure apenas um entre SMTP_USE_SSL e SMTP_USE_TLS.")
        if bool(self.username) != bool(self.password):
            raise RuntimeError(
                "SMTP_USERNAME e SMTP_PASSWORD devem ser configurados juntos."
            )
        if self.username and not (self.use_ssl or self.use_tls):
            raise RuntimeError("Credenciais SMTP exigem TLS ou SSL.")


def is_due_for_alert(task_due_date: date, lead_hours: int, reference_date: date) -> bool:
    if lead_hours not in ALLOWED_LEAD_HOURS:
        return False
    return task_due_date == reference_date + timedelta(hours=lead_hours)


def lead_time_label(lead_hours: int) -> str:
    return {48: "2 dias", 72: "3 dias", 168: "1 semana"}.get(
        lead_hours, f"{lead_hours} horas"
    )


def get_current_profile(db: Session, current_user: dict) -> models.Profile:
    require_permission(current_user, Permission.TASK_READ)
    repository = tenant_repository(db, current_user)
    profile = (
        repository.query(models.Profile)
        .filter(models.Profile.id == repository.context.user_id)
        .first()
    )
    if not profile:
        raise HTTPException(status_code=404, detail="Perfil não encontrado.")
    return profile


def get_alert_preferences(db: Session, current_user: dict) -> dict:
    profile = get_current_profile(db, current_user)
    return _serialize_preferences(profile)


def update_alert_preferences(
    db: Session,
    current_user: dict,
    *,
    enabled: bool,
    advance_hours: int,
) -> dict:
    if advance_hours not in ALLOWED_LEAD_HOURS:
        raise HTTPException(status_code=422, detail="Antecedência de alerta inválida.")

    profile = get_current_profile(db, current_user)
    if enabled and not profile.email:
        raise HTTPException(
            status_code=422,
            detail="Seu perfil precisa ter um e-mail para ativar os alertas.",
        )
    profile.deadline_alerts_enabled = enabled
    profile.alert_advance_hours = advance_hours
    db.commit()
    db.refresh(profile)
    return _serialize_preferences(profile)


def _serialize_preferences(profile: models.Profile) -> dict:
    return {
        "email": profile.email,
        "deadline_alerts_enabled": profile.deadline_alerts_enabled,
        "alert_advance_hours": profile.alert_advance_hours,
    }


def send_deadline_email(payload: DeadlineEmail) -> None:
    settings = SmtpSettings.from_mapping(os.environ)
    settings.validate()

    safe_title = " ".join(payload.task_title.splitlines()).strip()
    formatted_due_date = payload.due_date.strftime("%d/%m/%Y")
    advance = lead_time_label(payload.lead_hours)

    message = EmailMessage()
    message["Subject"] = f"Prazo próximo: {safe_title} vence em {advance}"
    message["From"] = settings.sender
    message["To"] = payload.recipient
    if settings.reply_to:
        message["Reply-To"] = settings.reply_to
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
        smtplib.SMTP_SSL(
            settings.host,
            settings.port,
            timeout=15,
            context=context,
        )
        if settings.use_ssl
        else smtplib.SMTP(settings.host, settings.port, timeout=15)
    )
    with smtp_connection as smtp:
        if settings.use_tls and not settings.use_ssl:
            smtp.starttls(context=context)
        if settings.username and settings.password:
            smtp.login(settings.username, settings.password)
        smtp.send_message(message)


def _as_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def claim_alert(
    db: Session,
    task: models.Task,
    client: models.Client,
    recipient: models.Profile,
    *,
    now: datetime | None = None,
) -> models.DeadlineAlert | None:
    claimed_at = now or datetime.now(timezone.utc)
    existing = (
        db.query(models.DeadlineAlert)
        .filter(
            models.DeadlineAlert.task_id == task.id,
            models.DeadlineAlert.due_date == task.due_date,
            models.DeadlineAlert.lead_hours == recipient.alert_advance_hours,
            models.DeadlineAlert.recipient_profile_id == recipient.id,
        )
        .with_for_update(skip_locked=True)
        .first()
    )
    if existing:
        if existing.status == "sent" or existing.attempts >= MAX_SEND_ATTEMPTS:
            return None
        if existing.status == "processing" and existing.updated_at is not None:
            if claimed_at - _as_utc(existing.updated_at) < PROCESSING_LEASE:
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


def process_due_alerts(
    db: Session,
    reference_date: date | None = None,
    *,
    email_sender: Callable[[DeadlineEmail], None] | None = None,
) -> dict[str, int]:
    today = reference_date or datetime.now(BUSINESS_TIMEZONE).date()
    sender = email_sender or send_deadline_email
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
        alert = claim_alert(db, task, client, recipient)
        if not alert:
            result["skipped"] += 1
            continue

        client_name = client.razao_social or client.nome or "cliente"
        try:
            sender(
                DeadlineEmail(
                    recipient=recipient.email,
                    recipient_name=recipient.name or "usuário",
                    client_name=client_name,
                    task_title=task.title,
                    due_date=task.due_date,
                    lead_hours=recipient.alert_advance_hours,
                )
            )
        except Exception as error:
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


def verify_cron_secret(
    received_secret: str | None,
    *,
    configured_secret: str | None = None,
) -> None:
    expected = (
        configured_secret
        if configured_secret is not None
        else os.getenv("ALERT_CRON_SECRET")
    )
    if not expected or len(expected) < 32:
        logger.error("ALERT_CRON_SECRET não configurado.")
        raise HTTPException(
            status_code=503,
            detail="Processador de alertas não configurado.",
        )
    if not received_secret or not secrets.compare_digest(received_secret, expected):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credencial inválida.",
        )
