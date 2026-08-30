import hmac
import logging
import os
import time
import uuid
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal, InvalidOperation

import httpx
import models
from fastapi import HTTPException, status
from plan_config import BILLING_CYCLES, PAID_PLAN_IDS
from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

logger = logging.getLogger("ContablyTask.Billing")

MAX_WEBHOOK_ATTEMPTS = 8
PROCESSING_LEASE = timedelta(minutes=5)
TRANSIENT_HTTP_STATUSES = {408, 425, 429, 500, 502, 503, 504}
OPEN_SUBSCRIPTION_STATUSES = {
    "creating",
    "pending",
    "active",
    "overdue",
    "refunded",
    "chargeback",
}

PAYMENT_STATUS_BY_EVENT = {
    "PAYMENT_CREATED": "pending",
    "PAYMENT_UPDATED": "pending",
    "PAYMENT_RESTORED": "pending",
    "PAYMENT_CONFIRMED": "confirmed",
    "PAYMENT_RECEIVED": "received",
    "PAYMENT_OVERDUE": "overdue",
    "PAYMENT_REFUNDED": "refunded",
    "PAYMENT_PARTIALLY_REFUNDED": "partially_refunded",
    "PAYMENT_REFUND_IN_PROGRESS": "refund_pending",
    "PAYMENT_DELETED": "canceled",
    "PAYMENT_RECEIVED_IN_CASH_UNDONE": "canceled",
    "PAYMENT_CHARGEBACK_REQUESTED": "chargeback",
    "PAYMENT_CHARGEBACK_DISPUTE": "chargeback",
    "PAYMENT_AWAITING_CHARGEBACK_REVERSAL": "chargeback",
}

PROVIDER_PAYMENT_EVENT = {
    "PENDING": "PAYMENT_CREATED",
    "CONFIRMED": "PAYMENT_CONFIRMED",
    "RECEIVED": "PAYMENT_RECEIVED",
    "OVERDUE": "PAYMENT_OVERDUE",
    "REFUNDED": "PAYMENT_REFUNDED",
    "PARTIALLY_REFUNDED": "PAYMENT_PARTIALLY_REFUNDED",
    "REFUND_REQUESTED": "PAYMENT_REFUND_IN_PROGRESS",
    "DELETED": "PAYMENT_DELETED",
}

ALLOWED_PAYMENT_TRANSITIONS = {
    "pending": {"pending", "confirmed", "received", "overdue", "canceled"},
    "overdue": {"overdue", "confirmed", "received", "refunded", "chargeback", "canceled"},
    "confirmed": {"confirmed", "received", "refunded", "partially_refunded", "refund_pending", "chargeback"},
    "received": {"received", "refunded", "partially_refunded", "refund_pending", "chargeback", "canceled"},
    "refund_pending": {"refund_pending", "refunded", "partially_refunded", "received"},
    "partially_refunded": {"partially_refunded", "refunded", "received", "chargeback"},
    "chargeback": {"chargeback", "confirmed", "received", "refunded"},
    "refunded": {"refunded"},
    "canceled": {"canceled", "pending"},
}


class BillingProcessingError(RuntimeError):
    """Falha transitória que deve voltar para a fila."""


class PermanentBillingError(RuntimeError):
    """Payload inconsistente que não deve ser retentado automaticamente."""


class AsaasUnavailableError(RuntimeError):
    pass


@dataclass(frozen=True)
class SubscriptionReference:
    tenant_id: uuid.UUID
    plan_code: str
    billing_cycle: str
    local_subscription_id: uuid.UUID | None = None


def build_subscription_reference(
    local_subscription_id: uuid.UUID,
    tenant_id: uuid.UUID,
    plan_code: str,
    billing_cycle: str,
) -> str:
    if plan_code not in PAID_PLAN_IDS or billing_cycle not in BILLING_CYCLES:
        raise ValueError("Plano ou ciclo inválido para referência de cobrança.")
    return f"ct:v1:{local_subscription_id}:{tenant_id}:{plan_code}:{billing_cycle}"


def parse_subscription_reference(value: str | None) -> SubscriptionReference | None:
    if not value:
        return None
    parts = str(value).split(":")
    try:
        if len(parts) == 6 and parts[:2] == ["ct", "v1"]:
            local_id = uuid.UUID(parts[2])
            tenant_id = uuid.UUID(parts[3])
            plan_code, billing_cycle = parts[4], parts[5]
        elif len(parts) == 3:
            # Compatibilidade com referências criadas pela versão anterior.
            local_id = None
            tenant_id = uuid.UUID(parts[0])
            plan_code, billing_cycle = parts[1], parts[2]
        else:
            return None
    except (ValueError, AttributeError):
        return None
    if plan_code not in PAID_PLAN_IDS or billing_cycle not in BILLING_CYCLES:
        return None
    return SubscriptionReference(tenant_id, plan_code, billing_cycle, local_id)


def parse_provider_datetime(value) -> datetime:
    if not value:
        return datetime.now(timezone.utc)
    normalized = str(value).strip().replace(" ", "T")
    try:
        parsed = datetime.fromisoformat(normalized.replace("Z", "+00:00"))
    except ValueError:
        return datetime.now(timezone.utc)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def parse_provider_date(value) -> date | None:
    if not value:
        return None
    try:
        return date.fromisoformat(str(value)[:10])
    except ValueError:
        return None


def parse_money(value) -> Decimal:
    try:
        return Decimal(str(value or "0")).quantize(Decimal("0.01"))
    except (InvalidOperation, ValueError):
        return Decimal("0.00")


def request_asaas(
    method: str,
    url: str,
    headers: dict,
    *,
    json_payload: dict | None = None,
    timeout: float = 10.0,
    max_attempts: int = 3,
) -> httpx.Response:
    last_error = None
    for attempt in range(max_attempts):
        try:
            with httpx.Client(timeout=timeout) as client:
                call = getattr(client, method.lower())
                kwargs = {"headers": headers}
                if json_payload is not None:
                    kwargs["json"] = json_payload
                response = call(url, **kwargs)
        except httpx.HTTPError as error:
            last_error = error
        else:
            if response.status_code not in TRANSIENT_HTTP_STATUSES:
                return response
            last_error = RuntimeError(f"Asaas respondeu HTTP {response.status_code}")
        if attempt < max_attempts - 1:
            time.sleep(0.2 * (2**attempt))
    raise AsaasUnavailableError(str(last_error or "Asaas indisponível"))


def enqueue_webhook_event(db: Session, payload: dict) -> tuple[models.AsaasWebhookEvent, bool]:
    event_id = str(payload.get("id") or "")
    event_type = str(payload.get("event") or "")
    if not event_id or len(event_id) > 100 or not event_type or len(event_type) > 80:
        raise HTTPException(status_code=400, detail="Evento inválido.")

    event = models.AsaasWebhookEvent(
        id=event_id,
        event_type=event_type,
        status="pending",
        payload=payload,
    )
    db.add(event)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        existing = (
            db.query(models.AsaasWebhookEvent)
            .filter(models.AsaasWebhookEvent.id == event_id)
            .first()
        )
        if not existing:
            raise
        return existing, False
    db.refresh(event)
    return event, True


def _find_subscription(
    db: Session,
    provider_subscription_id: str,
    entity: dict,
) -> tuple[models.BillingSubscription, models.Tenant]:
    subscription = (
        db.query(models.BillingSubscription)
        .filter(
            models.BillingSubscription.provider_subscription_id
            == provider_subscription_id
        )
        .first()
    )
    reference = parse_subscription_reference(entity.get("externalReference"))

    if subscription:
        tenant = (
            db.query(models.Tenant)
            .filter(models.Tenant.id == subscription.tenant_id)
            .first()
        )
        if not tenant:
            raise PermanentBillingError("Escritório da assinatura não encontrado.")
        if reference and reference.tenant_id != tenant.id:
            raise PermanentBillingError("Referência externa não corresponde ao escritório.")
        if not subscription.plan_code and reference:
            subscription.plan_code = reference.plan_code
            subscription.billing_cycle = reference.billing_cycle
            subscription.external_reference = str(entity.get("externalReference"))
        return subscription, tenant

    if reference:
        if reference.local_subscription_id:
            subscription = (
                db.query(models.BillingSubscription)
                .filter(models.BillingSubscription.id == reference.local_subscription_id)
                .first()
            )
            if subscription:
                tenant = (
                    db.query(models.Tenant)
                    .filter(models.Tenant.id == subscription.tenant_id)
                    .first()
                )
                if not tenant or tenant.id != reference.tenant_id:
                    raise PermanentBillingError(
                        "Identidade local da assinatura não corresponde ao escritório."
                    )
                if subscription.plan_code != reference.plan_code:
                    raise PermanentBillingError(
                        "Código de plano não corresponde à assinatura local."
                    )
                subscription.provider_subscription_id = provider_subscription_id
                return subscription, tenant
        tenant = db.query(models.Tenant).filter(models.Tenant.id == reference.tenant_id).first()
        if not tenant:
            raise PermanentBillingError("Referência aponta para escritório inexistente.")
        local_id = reference.local_subscription_id or uuid.uuid4()
        subscription = models.BillingSubscription(
            id=local_id,
            tenant_id=tenant.id,
            provider_customer_id=str(entity.get("customer") or tenant.asaas_customer_id or ""),
            provider_subscription_id=provider_subscription_id,
            external_reference=str(entity.get("externalReference")),
            plan_code=reference.plan_code,
            billing_cycle=reference.billing_cycle,
            status="pending",
        )
        db.add(subscription)
        db.flush()
        return subscription, tenant

    customer_id = entity.get("customer")
    tenant = None
    if customer_id:
        tenant = (
            db.query(models.Tenant)
            .filter(models.Tenant.asaas_customer_id == str(customer_id))
            .first()
        )
    if tenant and tenant.asaas_subscription_id == provider_subscription_id:
        subscription = models.BillingSubscription(
            tenant_id=tenant.id,
            provider_customer_id=str(customer_id),
            provider_subscription_id=provider_subscription_id,
            external_reference=f"legacy:{tenant.id}:{provider_subscription_id}",
            plan_code=tenant.plano if tenant.plano in PAID_PLAN_IDS else None,
            billing_cycle=(
                tenant.billing_cycle if tenant.billing_cycle in BILLING_CYCLES else "monthly"
            ),
            status="pending",
        )
        db.add(subscription)
        db.flush()
        return subscription, tenant
    raise BillingProcessingError("Assinatura ainda não foi conciliada.")


def _validate_subscription_identity(
    subscription: models.BillingSubscription,
    tenant: models.Tenant,
    entity: dict,
) -> None:
    customer_id = entity.get("customer")
    if customer_id and subscription.provider_customer_id != str(customer_id):
        raise PermanentBillingError("Cliente não corresponde à assinatura.")
    if tenant.asaas_customer_id and customer_id and tenant.asaas_customer_id != str(customer_id):
        raise PermanentBillingError("Cliente não corresponde ao escritório.")
    if not subscription.plan_code or subscription.plan_code not in PAID_PLAN_IDS:
        raise BillingProcessingError("Código imutável do plano ainda não foi conciliado.")


def _audit_billing_change(
    db: Session,
    tenant: models.Tenant,
    action: str,
    reason: str,
    old_value: str,
    new_value: str,
) -> None:
    if old_value == new_value:
        return
    db.add(
        models.AdminAuditLog(
            tenant_id=tenant.id,
            action=action,
            reason=reason[:500],
            old_value=old_value[:100],
            new_value=new_value[:100],
        )
    )


def _apply_tenant_status(
    db: Session,
    tenant: models.Tenant,
    subscription: models.BillingSubscription,
    payment_status: str,
    event_type: str,
    event_time: datetime,
) -> None:
    if tenant.billing_status_updated_at and event_time < tenant.billing_status_updated_at:
        return
    status_map = {
        "confirmed": ("ativo", "active"),
        "received": ("ativo", "active"),
        "overdue": ("inadimplente", "overdue"),
        "refunded": ("estornado", "refunded"),
        "chargeback": ("chargeback", "chargeback"),
    }
    target = status_map.get(payment_status)
    if not target:
        return
    old_value = f"{tenant.status_pagamento}:{tenant.plano}:{tenant.billing_cycle}"
    tenant.status_pagamento, tenant.subscription_status = target
    if payment_status in {"confirmed", "received"}:
        tenant.plano = subscription.plan_code
        tenant.billing_cycle = subscription.billing_cycle
    tenant.billing_status_updated_at = event_time
    subscription.status = target[1]
    new_value = f"{tenant.status_pagamento}:{tenant.plano}:{tenant.billing_cycle}"
    _audit_billing_change(
        db,
        tenant,
        "billing_status_changed",
        f"Estado atualizado pelo evento Asaas {event_type}.",
        old_value,
        new_value,
    )


def apply_payment_event(
    db: Session,
    payment_data: dict,
    event_type: str,
    event_id: str,
    event_time: datetime,
    *,
    update_tenant_status: bool = True,
) -> models.Tenant | None:
    payment_id = str(payment_data.get("id") or "")
    provider_subscription_id = str(payment_data.get("subscription") or "")
    if not payment_id or not provider_subscription_id:
        return None
    target_status = PAYMENT_STATUS_BY_EVENT.get(event_type)
    if not target_status:
        return None

    subscription, tenant = _find_subscription(
        db,
        provider_subscription_id,
        payment_data,
    )
    _validate_subscription_identity(subscription, tenant, payment_data)
    record = (
        db.query(models.PaymentRecord)
        .filter(models.PaymentRecord.provider_payment_id == payment_id)
        .first()
    )
    if record and record.provider_updated_at and event_time < record.provider_updated_at:
        return tenant
    if record and target_status not in ALLOWED_PAYMENT_TRANSITIONS.get(record.status, {target_status}):
        logger.warning(
            "Transição de cobrança ignorada: %s -> %s (%s)",
            record.status,
            target_status,
            payment_id,
        )
        return tenant
    if not record:
        record = models.PaymentRecord(
            provider_payment_id=payment_id,
            tenant_id=tenant.id,
            value=parse_money(payment_data.get("value")),
            status=target_status,
        )
        db.add(record)

    record.tenant_id = tenant.id
    record.subscription_id = provider_subscription_id
    record.provider_customer_id = str(payment_data.get("customer") or "") or None
    record.external_reference = payment_data.get("externalReference")
    record.plan_code = subscription.plan_code
    record.billing_cycle = subscription.billing_cycle
    record.last_event_id = event_id
    record.provider_updated_at = event_time
    record.value = parse_money(payment_data.get("value"))
    record.status = target_status
    record.due_date = parse_provider_date(payment_data.get("dueDate"))
    record.invoice_url = payment_data.get("invoiceUrl")
    paid_date = parse_provider_date(
        payment_data.get("paymentDate") or payment_data.get("clientPaymentDate")
    )
    if paid_date:
        record.paid_at = datetime.combine(paid_date, datetime.min.time(), tzinfo=timezone.utc)
    elif target_status in {"confirmed", "received"} and not record.paid_at:
        record.paid_at = event_time

    if update_tenant_status:
        _apply_tenant_status(
            db,
            tenant,
            subscription,
            target_status,
            event_type,
            event_time,
        )
    return tenant


def apply_subscription_event(
    db: Session,
    subscription_data: dict,
    event_type: str,
    event_time: datetime,
) -> models.Tenant | None:
    provider_subscription_id = str(subscription_data.get("id") or "")
    if not provider_subscription_id:
        return None
    subscription, tenant = _find_subscription(db, provider_subscription_id, subscription_data)
    _validate_subscription_identity(subscription, tenant, subscription_data)
    subscription.value = parse_money(subscription_data.get("value"))
    subscription.next_due_date = parse_provider_date(subscription_data.get("nextDueDate"))
    subscription.last_synced_at = event_time

    provider_status = str(subscription_data.get("status") or "").upper()
    status_by_event = {
        "SUBSCRIPTION_CREATED": "pending",
        "SUBSCRIPTION_UPDATED": "active" if provider_status == "ACTIVE" else "pending",
        "SUBSCRIPTION_INACTIVATED": "inactive",
        "SUBSCRIPTION_DELETED": "canceled",
    }
    new_status = status_by_event.get(event_type)
    if not new_status:
        return tenant
    old_value = f"{tenant.status_pagamento}:{tenant.subscription_status}"
    subscription.status = new_status
    if new_status in {"inactive", "canceled"} and (
        not tenant.billing_status_updated_at or event_time >= tenant.billing_status_updated_at
    ):
        tenant.status_pagamento = "cancelado"
        tenant.subscription_status = new_status
        tenant.billing_status_updated_at = event_time
    new_value = f"{tenant.status_pagamento}:{tenant.subscription_status}"
    _audit_billing_change(
        db,
        tenant,
        "subscription_status_changed",
        f"Assinatura atualizada pelo evento Asaas {event_type}.",
        old_value,
        new_value,
    )
    return tenant


def apply_webhook_payload(db: Session, payload: dict, event_id: str) -> models.Tenant | None:
    event_type = str(payload.get("event") or "")
    event_time = parse_provider_datetime(payload.get("dateCreated"))
    if event_type.startswith("PAYMENT_"):
        payment_data = payload.get("payment")
        if not isinstance(payment_data, dict):
            raise PermanentBillingError("Evento de cobrança sem objeto payment.")
        return apply_payment_event(db, payment_data, event_type, event_id, event_time)
    if event_type.startswith("SUBSCRIPTION_"):
        subscription_data = payload.get("subscription")
        if not isinstance(subscription_data, dict):
            raise PermanentBillingError("Evento de assinatura sem objeto subscription.")
        return apply_subscription_event(db, subscription_data, event_type, event_time)
    return None


def _mark_event_failure(
    db: Session,
    event_id: str,
    error: Exception,
    *,
    permanent: bool,
) -> None:
    event = (
        db.query(models.AsaasWebhookEvent)
        .filter(models.AsaasWebhookEvent.id == event_id)
        .first()
    )
    if not event:
        return
    event.error = str(error)[:1000]
    event.processing_started_at = None
    if permanent or event.attempts >= MAX_WEBHOOK_ATTEMPTS:
        event.status = "dead"
        event.next_retry_at = None
    else:
        event.status = "failed"
        delay_seconds = min(60 * (2 ** max(event.attempts - 1, 0)), 21600)
        event.next_retry_at = datetime.now(timezone.utc) + timedelta(seconds=delay_seconds)
    db.commit()


def process_webhook_event(db: Session, event_id: str, *, force: bool = False) -> str:
    now = datetime.now(timezone.utc)
    event = (
        db.query(models.AsaasWebhookEvent)
        .filter(models.AsaasWebhookEvent.id == event_id)
        .with_for_update()
        .first()
    )
    if not event:
        return "missing"
    if event.status in {"success", "dead"}:
        return event.status
    if (
        event.status == "processing"
        and event.processing_started_at
        and event.processing_started_at > now - PROCESSING_LEASE
    ):
        return "processing"
    if not force and event.next_retry_at and event.next_retry_at > now:
        return "waiting"
    if event.attempts >= MAX_WEBHOOK_ATTEMPTS:
        event.status = "dead"
        db.commit()
        return "dead"

    payload = dict(event.payload or {})
    event.status = "processing"
    event.processing_started_at = now
    event.attempts += 1
    event.next_retry_at = None
    db.commit()

    try:
        tenant = apply_webhook_payload(db, payload, event_id)
        event = (
            db.query(models.AsaasWebhookEvent)
            .filter(models.AsaasWebhookEvent.id == event_id)
            .first()
        )
        event.tenant_id = tenant.id if tenant else None
        event.status = "success"
        event.error = None
        event.processed_at = datetime.now(timezone.utc)
        event.processing_started_at = None
        db.commit()
        return "success"
    except PermanentBillingError as error:
        db.rollback()
        _mark_event_failure(db, event_id, error, permanent=True)
        logger.warning("Evento Asaas %s descartado: %s", event_id, error)
        return "dead"
    except Exception as error:
        db.rollback()
        _mark_event_failure(db, event_id, error, permanent=False)
        logger.exception("Falha ao processar evento Asaas %s", event_id)
        return "failed"


def process_pending_webhooks(db: Session, batch_size: int = 100) -> dict[str, int]:
    now = datetime.now(timezone.utc)
    stale_before = now - PROCESSING_LEASE
    event_ids = [
        row[0]
        for row in (
            db.query(models.AsaasWebhookEvent.id)
            .filter(
                or_(
                    models.AsaasWebhookEvent.status == "pending",
                    (
                        (models.AsaasWebhookEvent.status == "failed")
                        & (
                            (models.AsaasWebhookEvent.next_retry_at.is_(None))
                            | (models.AsaasWebhookEvent.next_retry_at <= now)
                        )
                    ),
                    (
                        (models.AsaasWebhookEvent.status == "processing")
                        & (models.AsaasWebhookEvent.processing_started_at <= stale_before)
                    ),
                )
            )
            .order_by(models.AsaasWebhookEvent.created_at)
            .limit(batch_size)
            .all()
        )
    ]
    result = {"processed": 0, "failed": 0, "skipped": 0}
    for event_id in event_ids:
        outcome = process_webhook_event(db, event_id)
        if outcome == "success":
            result["processed"] += 1
        elif outcome in {"failed", "dead"}:
            result["failed"] += 1
        else:
            result["skipped"] += 1
    return result


def verify_reconciliation_secret(received_secret: str | None) -> None:
    configured_secret = os.getenv("ASAAS_RECONCILIATION_SECRET")
    if not configured_secret or len(configured_secret) < 32:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Reconciliação de cobrança não configurada.",
        )
    if not received_secret or not hmac.compare_digest(received_secret, configured_secret):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credencial inválida.",
        )
