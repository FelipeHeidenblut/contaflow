import logging
import re
import uuid
from datetime import date, datetime, timedelta, timezone
from urllib.parse import quote

import httpx
import models
from app_config import get_settings
from access_control import Permission, require_permission
from billing import (
    OPEN_SUBSCRIPTION_STATUSES,
    PROVIDER_PAYMENT_EVENT,
    AsaasUnavailableError,
    PermanentBillingError,
    apply_payment_event,
    build_subscription_reference,
    parse_money,
    parse_provider_date,
    parse_subscription_reference,
    process_pending_webhooks,
    request_asaas,
)
from sqlalchemy.orm import Session

from fastapi import HTTPException, status

from plan_config import BILLING_CYCLES, PAID_PLAN_IDS, PLAN_CONFIG, get_plan_price

logger = logging.getLogger("ContablyTask.Subscription")

app_settings = get_settings()
ASAAS_API_KEY = app_settings.asaas_api_key
BASE_URL = (
    "https://api.asaas.com/v3"
    if app_settings.asaas_environment == "production"
    else "https://api-sandbox.asaas.com/v3"
)
HEADERS = {"access_token": ASAAS_API_KEY, "Content-Type": "application/json"}
HTTP_TIMEOUT = 10.0


def normalize_billing_document(value: str | None) -> str:
    """Normaliza CPF/CNPJ sem descartar letras do novo CNPJ alfanumérico."""
    document = re.sub(r"[^A-Za-z0-9]", "", value or "").upper()
    is_cpf = len(document) == 11 and document.isdigit()
    is_cnpj = (
        len(document) == 14
        and document[:12].isalnum()
        and document[-2:].isdigit()
    )
    if not (is_cpf or is_cnpj):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=(
                "O CPF/CNPJ do escritório está ausente ou possui formato inválido. "
                "Atualize o cadastro antes de contratar um plano."
            ),
        )
    return document


def _gateway_error_description(response: httpx.Response) -> str | None:
    try:
        errors = response.json().get("errors", [])
    except (ValueError, AttributeError):
        return None
    if not errors or not isinstance(errors[0], dict):
        return None
    description = errors[0].get("description")
    return str(description)[:300] if description else None


def _safe_gateway_response(response: httpx.Response, operation: str) -> None:
    if response.status_code in {200, 201}:
        return
    detail = _gateway_error_description(response)
    if detail:
        detail = detail.replace("CPF ou CNPJ", "CPF/CNPJ")
    logger.error(
        "Asaas recusou %s (HTTP %s): %s",
        operation,
        response.status_code,
        detail,
    )
    raise HTTPException(
        status_code=status.HTTP_502_BAD_GATEWAY,
        detail=detail or f"O gateway recusou a operação de {operation}.",
    )


def _find_remote_customer(external_reference: str) -> str | None:
    response = request_asaas(
        "GET",
        f"{BASE_URL}/customers?externalReference={quote(external_reference)}",
        HEADERS,
        timeout=HTTP_TIMEOUT,
    )
    if response.status_code != 200:
        return None
    customers = response.json().get("data", [])
    if not isinstance(customers, list) or not customers:
        return None
    customer = customers[0]
    if not isinstance(customer, dict) or not customer.get("id"):
        return None
    return str(customer["id"])


def ensure_asaas_customer(db: Session, tenant: models.Tenant) -> str:
    """Sincroniza o pagador e recupera tentativas inconclusivas pela referência externa."""
    document = normalize_billing_document(tenant.cnpj)
    payload = {
        "name": tenant.razao_social,
        "cpfCnpj": document,
        "externalReference": str(tenant.id),
    }

    if tenant.asaas_customer_id:
        try:
            response = request_asaas(
                "PUT",
                f"{BASE_URL}/customers/{tenant.asaas_customer_id}",
                HEADERS,
                json_payload=payload,
                timeout=HTTP_TIMEOUT,
            )
        except AsaasUnavailableError as error:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Não foi possível sincronizar o cadastro com o gateway.",
            ) from error
        _safe_gateway_response(response, "atualização do cliente")
        return str(tenant.asaas_customer_id)

    try:
        recovered_id = _find_remote_customer(str(tenant.id))
    except AsaasUnavailableError:
        recovered_id = None
    if not recovered_id:
        try:
            response = request_asaas(
                "POST",
                f"{BASE_URL}/customers",
                HEADERS,
                json_payload=payload,
                timeout=HTTP_TIMEOUT,
                max_attempts=1,
            )
        except AsaasUnavailableError as error:
            try:
                recovered_id = _find_remote_customer(str(tenant.id))
            except AsaasUnavailableError:
                recovered_id = None
            if not recovered_id:
                raise HTTPException(
                    status_code=status.HTTP_502_BAD_GATEWAY,
                    detail="Não foi possível criar o cliente no gateway.",
                ) from error
        else:
            _safe_gateway_response(response, "criação do cliente")
            response_data = response.json()
            recovered_id = (
                response_data.get("id") if isinstance(response_data, dict) else None
            )

    if not recovered_id:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="O gateway não retornou o identificador do cliente.",
        )
    tenant.asaas_customer_id = str(recovered_id)
    db.flush()
    return str(recovered_id)


def _find_remote_subscription(external_reference: str) -> dict | None:
    response = request_asaas(
        "GET",
        f"{BASE_URL}/subscriptions?externalReference={quote(external_reference)}",
        HEADERS,
        timeout=HTTP_TIMEOUT,
    )
    if response.status_code != 200:
        return None
    response_data = response.json()
    subscriptions = (
        response_data.get("data", []) if isinstance(response_data, dict) else []
    )
    if not isinstance(subscriptions, list) or not subscriptions:
        return None
    return subscriptions[0] if isinstance(subscriptions[0], dict) else None


def _first_subscription_invoice(
    subscription_id: str,
) -> tuple[str | None, list[dict]]:
    try:
        response = request_asaas(
            "GET",
            f"{BASE_URL}/subscriptions/{subscription_id}/payments?limit=100",
            HEADERS,
            timeout=HTTP_TIMEOUT,
        )
    except AsaasUnavailableError:
        return None, []
    if response.status_code != 200:
        return None, []
    response_data = response.json()
    payments = response_data.get("data", []) if isinstance(response_data, dict) else []
    if not isinstance(payments, list):
        return None, []
    payments = [payment for payment in payments if isinstance(payment, dict)]
    invoice_url = payments[0].get("invoiceUrl") if payments else None
    return invoice_url, payments


def _get_locked_tenant(db: Session, current_user: dict) -> models.Tenant:
    tenant = (
        db.query(models.Tenant)
        .filter(models.Tenant.id == current_user.get("tenant_id"))
        .with_for_update()
        .first()
    )
    if not tenant:
        raise HTTPException(status_code=404, detail="Escritório não encontrado.")
    return tenant


def _get_open_subscription(
    db: Session,
    tenant: models.Tenant,
) -> models.BillingSubscription | None:
    return (
        db.query(models.BillingSubscription)
        .filter(
            models.BillingSubscription.tenant_id == tenant.id,
            models.BillingSubscription.status.in_(OPEN_SUBSCRIPTION_STATUSES),
        )
        .order_by(models.BillingSubscription.created_at.desc())
        .first()
    )


def _validate_open_subscription(
    subscription: models.BillingSubscription | None,
    plan_code: str,
    billing_cycle: str,
) -> None:
    if subscription and (
        subscription.plan_code != plan_code
        or subscription.billing_cycle != billing_cycle
        or subscription.provider_subscription_id
    ):
        raise HTTPException(
            status_code=409,
            detail=(
                "Já existe uma assinatura vinculada a este escritório. "
                "Solicite ao suporte a alteração de plano ou ciclo."
            ),
        )


def _prepare_local_subscription(
    db: Session,
    tenant: models.Tenant,
    customer_id: str,
    plan_code: str,
    billing_cycle: str,
    subscription: models.BillingSubscription | None,
) -> models.BillingSubscription:
    if subscription:
        return subscription

    local_id = uuid.uuid4()
    subscription = models.BillingSubscription(
        id=local_id,
        tenant_id=tenant.id,
        provider_customer_id=customer_id,
        external_reference=build_subscription_reference(
            local_id,
            tenant.id,
            plan_code,
            billing_cycle,
        ),
        plan_code=plan_code,
        billing_cycle=billing_cycle,
        status="creating",
        value=get_plan_price(plan_code, billing_cycle),
    )
    db.add(subscription)
    return subscription


def _create_or_recover_remote_subscription(
    subscription: models.BillingSubscription,
    customer_id: str,
) -> dict:
    remote_subscription = _find_remote_subscription(
        subscription.external_reference
    )
    if remote_subscription:
        return remote_subscription

    payload = {
        "customer": customer_id,
        "billingType": "UNDEFINED",
        "value": float(
            get_plan_price(subscription.plan_code, subscription.billing_cycle)
        ),
        "cycle": (
            "YEARLY" if subscription.billing_cycle == "annual" else "MONTHLY"
        ),
        "description": (
            f"Plano {PLAN_CONFIG[subscription.plan_code]['name']} "
            f"({'Anual' if subscription.billing_cycle == 'annual' else 'Mensal'}) "
            "- ContablyTask"
        ),
        "nextDueDate": (date.today() + timedelta(days=1)).isoformat(),
        "externalReference": subscription.external_reference,
    }
    try:
        response = request_asaas(
            "POST",
            f"{BASE_URL}/subscriptions",
            HEADERS,
            json_payload=payload,
            timeout=HTTP_TIMEOUT,
            max_attempts=1,
        )
    except AsaasUnavailableError:
        recovered = _find_remote_subscription(subscription.external_reference)
        if not recovered:
            raise
        return recovered

    _safe_gateway_response(response, "criação da assinatura")
    response_data = response.json()
    if not isinstance(response_data, dict):
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="O gateway retornou uma assinatura inválida.",
        )
    return response_data


def _record_creation_failure(
    db: Session,
    tenant: models.Tenant,
    subscription: models.BillingSubscription,
    current_user: dict,
) -> None:
    subscription.status = "failed"
    db.add(
        models.AdminAuditLog(
            tenant_id=tenant.id,
            actor_profile_id=current_user.get("user_id"),
            action="subscription_creation_failed",
            reason="Falha ao criar ou recuperar assinatura no Asaas.",
            old_value="creating",
            new_value="failed",
        )
    )
    db.commit()


def _finalize_pending_subscription(
    db: Session,
    tenant: models.Tenant,
    subscription: models.BillingSubscription,
    current_user: dict,
    remote_subscription: dict,
) -> str:
    provider_subscription_id = str(remote_subscription.get("id") or "")
    if not provider_subscription_id:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="O gateway não retornou o identificador da assinatura.",
        )

    now = datetime.now(timezone.utc)
    subscription.provider_subscription_id = provider_subscription_id
    subscription.status = "pending"
    subscription.next_due_date = parse_provider_date(
        remote_subscription.get("nextDueDate")
    )
    subscription.last_synced_at = now
    tenant.asaas_subscription_id = provider_subscription_id
    tenant.status_pagamento = "aguardando_pagamento"
    tenant.subscription_status = "pending"
    tenant.billing_cycle = subscription.billing_cycle
    tenant.billing_status_updated_at = now
    db.add(
        models.AdminAuditLog(
            tenant_id=tenant.id,
            actor_profile_id=current_user.get("user_id"),
            action="subscription_created",
            reason=(
                f"Assinatura {subscription.plan_code}/"
                f"{subscription.billing_cycle} criada no Asaas."
            ),
            old_value="none",
            new_value=(
                f"pending:{subscription.plan_code}:"
                f"{subscription.billing_cycle}"
            ),
        )
    )
    db.commit()
    return provider_subscription_id


def _sync_initial_payments(
    db: Session,
    provider_subscription_id: str,
) -> str | None:
    invoice_url, payments = _first_subscription_invoice(provider_subscription_id)
    for payment in payments:
        provider_status = str(payment.get("status") or "PENDING").upper()
        event_type = PROVIDER_PAYMENT_EVENT.get(
            provider_status,
            "PAYMENT_CREATED",
        )
        apply_payment_event(
            db,
            payment,
            event_type,
            f"subscription-create:{payment.get('id')}:{provider_status}",
            datetime.now(timezone.utc),
        )
    if payments:
        db.commit()
    return invoice_url


def _mark_reconciled_subscription_unavailable(
    db: Session,
    tenant: models.Tenant,
    subscription: models.BillingSubscription,
    subscription_status: str,
    reason: str,
) -> None:
    old_value = f"{tenant.status_pagamento}:{tenant.subscription_status}"
    subscription.status = subscription_status
    if tenant.asaas_subscription_id == subscription.provider_subscription_id:
        tenant.subscription_status = subscription_status
        tenant.status_pagamento = "cancelado"
        tenant.billing_status_updated_at = datetime.now(timezone.utc)
    new_value = f"{tenant.status_pagamento}:{tenant.subscription_status}"
    if old_value != new_value:
        db.add(
            models.AdminAuditLog(
                tenant_id=tenant.id,
                action="subscription_reconciled",
                reason=reason,
                old_value=old_value,
                new_value=new_value,
            )
        )


def _validate_reconciled_identity(
    subscription: models.BillingSubscription,
    tenant: models.Tenant,
    remote: dict,
) -> None:
    reference = parse_subscription_reference(remote.get("externalReference"))
    if reference:
        if reference.tenant_id != subscription.tenant_id:
            raise PermanentBillingError(
                "Referência externa divergente na reconciliação."
            )
        if (
            reference.local_subscription_id
            and reference.local_subscription_id != subscription.id
        ):
            raise PermanentBillingError(
                "Identidade local divergente na reconciliação."
            )
        if (
            subscription.plan_code
            and subscription.plan_code != reference.plan_code
        ):
            raise PermanentBillingError(
                "Código de plano divergente na reconciliação."
            )
        if subscription.billing_cycle != reference.billing_cycle:
            raise PermanentBillingError(
                "Ciclo de cobrança divergente na reconciliação."
            )
        subscription.plan_code = reference.plan_code
        subscription.billing_cycle = reference.billing_cycle
        subscription.external_reference = remote.get("externalReference")

    remote_customer_id = str(remote.get("customer") or "")
    if (
        not remote_customer_id
        or remote_customer_id != subscription.provider_customer_id
    ):
        raise PermanentBillingError(
            "Cliente do Asaas não corresponde à assinatura local."
        )
    if tenant.asaas_customer_id and tenant.asaas_customer_id != remote_customer_id:
        raise PermanentBillingError(
            "Cliente do Asaas não corresponde ao escritório local."
        )


def _apply_reconciled_subscription(
    db: Session,
    tenant: models.Tenant,
    subscription: models.BillingSubscription,
    remote: dict,
) -> int:
    _validate_reconciled_identity(subscription, tenant, remote)
    subscription.value = parse_money(remote.get("value"))
    subscription.next_due_date = parse_provider_date(remote.get("nextDueDate"))
    provider_status = str(remote.get("status") or "").upper()
    subscription.status = {
        "ACTIVE": "active",
        "INACTIVE": "inactive",
        "EXPIRED": "expired",
    }.get(provider_status, subscription.status)
    subscription.last_synced_at = datetime.now(timezone.utc)
    if subscription.status in {"inactive", "expired"}:
        _mark_reconciled_subscription_unavailable(
            db,
            tenant,
            subscription,
            subscription.status,
            "Assinatura inativa ou expirada detectada na reconciliação com o Asaas.",
        )

    _, payments = _first_subscription_invoice(subscription.provider_subscription_id)
    processed_payments = 0
    for payment in payments:
        event_type = PROVIDER_PAYMENT_EVENT.get(
            str(payment.get("status") or "").upper()
        )
        if not event_type:
            continue
        apply_payment_event(
            db,
            payment,
            event_type,
            f"reconcile:{payment.get('id')}:{payment.get('status')}",
            datetime.now(timezone.utc),
            update_tenant_status=subscription.status
            not in {"inactive", "expired"},
        )
        processed_payments += 1
    return processed_payments


def reconcile_asaas(
    db: Session,
    batch_size: int = 100,
) -> dict[str, int | str]:
    run = models.BillingReconciliationRun(status="running")
    db.add(run)
    db.commit()
    db.refresh(run)
    run_id = run.id

    try:
        event_result = process_pending_webhooks(db, batch_size=batch_size)
    except Exception:
        db.rollback()
        logger.exception(
            "Falha ao processar a fila de webhooks durante a reconciliação."
        )
        event_result = {"processed": 0, "failed": 1, "skipped": 0}

    processed_subscriptions = 0
    processed_payments = 0
    failures = event_result["failed"]
    subscriptions = (
        db.query(models.BillingSubscription)
        .filter(models.BillingSubscription.provider_subscription_id.isnot(None))
        .order_by(models.BillingSubscription.updated_at)
        .limit(batch_size)
        .all()
    )

    for subscription in subscriptions:
        try:
            response = request_asaas(
                "GET",
                f"{BASE_URL}/subscriptions/{subscription.provider_subscription_id}",
                HEADERS,
                timeout=HTTP_TIMEOUT,
            )
            tenant = (
                db.query(models.Tenant)
                .filter(models.Tenant.id == subscription.tenant_id)
                .first()
            )
            if response.status_code == 404:
                if tenant:
                    _mark_reconciled_subscription_unavailable(
                        db,
                        tenant,
                        subscription,
                        "missing",
                        "A assinatura não foi encontrada durante a reconciliação com o Asaas.",
                    )
                else:
                    subscription.status = "missing"
                db.commit()
                processed_subscriptions += 1
                continue

            _safe_gateway_response(response, "reconciliação da assinatura")
            remote = response.json()
            if not isinstance(remote, dict):
                raise PermanentBillingError(
                    "Resposta inválida durante a reconciliação da assinatura."
                )
            if not tenant:
                raise PermanentBillingError(
                    "Escritório da assinatura não encontrado durante a reconciliação."
                )
            processed_payments += _apply_reconciled_subscription(
                db,
                tenant,
                subscription,
                remote,
            )
            db.commit()
            processed_subscriptions += 1
        except Exception:
            db.rollback()
            failures += 1
            logger.exception(
                "Falha ao reconciliar assinatura %s",
                subscription.provider_subscription_id,
            )

    run = (
        db.query(models.BillingReconciliationRun)
        .filter(models.BillingReconciliationRun.id == run_id)
        .first()
    )
    run.status = "partial" if failures else "success"
    run.finished_at = datetime.now(timezone.utc)
    run.processed_events = event_result["processed"]
    run.processed_subscriptions = processed_subscriptions
    run.processed_payments = processed_payments
    run.failures = failures
    db.commit()
    return {
        "run_id": str(run.id),
        "processed_events": event_result["processed"],
        "processed_subscriptions": processed_subscriptions,
        "processed_payments": processed_payments,
        "failures": failures,
    }


def create_subscription(
    db: Session,
    current_user: dict,
    plan_code: str,
    billing_cycle: str,
) -> dict[str, str | None]:
    if plan_code not in PAID_PLAN_IDS:
        raise HTTPException(status_code=400, detail="Plano inválido ou gratuito.")
    if billing_cycle not in BILLING_CYCLES:
        raise HTTPException(status_code=400, detail="Ciclo de cobrança inválido.")
    require_permission(
        current_user,
        Permission.BILLING_MANAGE,
        detail="Apenas administradores podem contratar planos.",
    )

    tenant = _get_locked_tenant(db, current_user)
    open_subscription = _get_open_subscription(db, tenant)
    _validate_open_subscription(open_subscription, plan_code, billing_cycle)
    customer_id = ensure_asaas_customer(db, tenant)
    subscription = _prepare_local_subscription(
        db,
        tenant,
        customer_id,
        plan_code,
        billing_cycle,
        open_subscription,
    )
    db.commit()

    try:
        remote_subscription = _create_or_recover_remote_subscription(
            subscription,
            customer_id,
        )
    except (AsaasUnavailableError, HTTPException) as error:
        _record_creation_failure(
            db,
            tenant,
            subscription,
            current_user,
        )
        if isinstance(error, HTTPException):
            raise
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Não foi possível gerar a assinatura no gateway.",
        ) from error

    provider_subscription_id = _finalize_pending_subscription(
        db,
        tenant,
        subscription,
        current_user,
        remote_subscription,
    )
    invoice_url = _sync_initial_payments(db, provider_subscription_id)
    return {
        "invoice_url": invoice_url,
        "message": "Assinatura criada! Redirecionando...",
    }
