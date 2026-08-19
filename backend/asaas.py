import json
import hmac
import logging
import os
import re
from datetime import date, datetime, time, timedelta, timezone
from decimal import Decimal, InvalidOperation
from typing import Literal

import httpx
import models
from database import get_db
from dotenv import load_dotenv
from fastapi import APIRouter, Body, Depends, HTTPException, Request, status
from plan_config import PLAN_CONFIG, get_plan_price, identify_subscription_by_value
from security import get_current_user
from sqlalchemy.orm import Session

# ==========================================
# CONFIGURAÇÃO DE LOGS (Padrão SaaS)
# ==========================================
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("ContablyTask.Asaas")

load_dotenv()

router = APIRouter(prefix="/api/v1/asaas", tags=["Pagamentos e Assinaturas"])

ASAAS_API_KEY = os.getenv("ASAAS_API_KEY")
# NOVO: Token de segurança para validar que o Webhook realmente veio do Asaas
ASAAS_WEBHOOK_TOKEN = os.getenv("ASAAS_WEBHOOK_TOKEN")

# CORREÇÃO: A lógica estava invertida! Agora está correto.
BASE_URL = (
    "https://www.asaas.com/api/v3"
    if os.getenv("ASAAS_ENV") == "production"
    else "https://sandbox.asaas.com/api/v3"
)

headers = {"access_token": ASAAS_API_KEY, "Content-Type": "application/json"}
HTTP_TIMEOUT = 10.0


def _normalize_billing_document(value: str | None) -> str:
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


def _ensure_asaas_customer(db: Session, tenant: models.Tenant) -> str:
    """Cria ou sincroniza o cliente do Asaas antes de emitir uma assinatura."""
    document = _normalize_billing_document(tenant.cnpj)
    payload = {
        "name": tenant.razao_social,
        "cpfCnpj": document,
        "externalReference": str(tenant.id),
    }

    with httpx.Client(timeout=HTTP_TIMEOUT) as client:
        if tenant.asaas_customer_id:
            response = client.put(
                f"{BASE_URL}/customers/{tenant.asaas_customer_id}",
                json=payload,
                headers=headers,
            )
            operation = "atualizar"
        else:
            response = client.post(
                f"{BASE_URL}/customers", json=payload, headers=headers
            )
            operation = "criar"

    if response.status_code not in (200, 201):
        gateway_detail = _gateway_error_description(response)
        logger.error(
            "[ASAAS CLIENTE ERRO] Falha ao %s cliente do tenant %s. HTTP %s: %s",
            operation,
            tenant.id,
            response.status_code,
            gateway_detail or "resposta sem detalhe",
        )
        if response.status_code == 404 and tenant.asaas_customer_id:
            detail = (
                "O cadastro de cobrança não foi encontrado no ambiente atual do Asaas. "
                "Entre em contato com o suporte."
            )
        elif response.status_code == 400:
            detail = (
                "O Asaas recusou o CPF/CNPJ cadastrado. Confira o documento do "
                "responsável pelo escritório."
            )
        else:
            detail = "Não foi possível sincronizar o cadastro com o gateway de pagamento."
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=detail)

    if not tenant.asaas_customer_id:
        customer_id = response.json().get("id")
        if not customer_id:
            logger.error(
                "[ASAAS CLIENTE ERRO] Resposta sem ID ao criar cliente do tenant %s.",
                tenant.id,
            )
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="O gateway não retornou o identificador do cliente.",
            )
        tenant.asaas_customer_id = str(customer_id)
        db.commit()
        logger.info("Cliente criado no Asaas para o tenant %s.", tenant.id)

    return str(tenant.asaas_customer_id)


def _parse_date(value):
    if not value:
        return None
    try:
        return date.fromisoformat(str(value)[:10])
    except ValueError:
        return None


def _parse_paid_at(payment_data: dict, event: str):
    value = payment_data.get("paymentDate") or payment_data.get("clientPaymentDate")
    parsed = _parse_date(value)
    if parsed:
        return datetime.combine(parsed, time.min, tzinfo=timezone.utc)
    if event in {"PAYMENT_RECEIVED", "PAYMENT_CONFIRMED"}:
        return datetime.now(timezone.utc)
    return None


def _upsert_payment_record(
    db: Session, tenant: models.Tenant, payment_data: dict, event: str
) -> None:
    payment_id = payment_data.get("id")
    if not payment_id:
        return
    try:
        value = Decimal(str(payment_data.get("value") or "0")).quantize(Decimal("0.01"))
    except InvalidOperation:
        value = Decimal("0.00")
    status_by_event = {
        "PAYMENT_RECEIVED": "received",
        "PAYMENT_CONFIRMED": "received",
        "PAYMENT_OVERDUE": "overdue",
        "PAYMENT_REFUNDED": "refunded",
        "PAYMENT_DELETED": "deleted",
    }
    record = (
        db.query(models.PaymentRecord)
        .filter(models.PaymentRecord.provider_payment_id == str(payment_id))
        .first()
    )
    if not record:
        record = models.PaymentRecord(
            provider_payment_id=str(payment_id),
            tenant_id=tenant.id,
            value=value,
            status=status_by_event.get(event, str(payment_data.get("status") or event).lower()),
        )
        db.add(record)
    record.tenant_id = tenant.id
    record.subscription_id = payment_data.get("subscription")
    record.value = value
    record.status = status_by_event.get(event, str(payment_data.get("status") or event).lower())
    record.due_date = _parse_date(payment_data.get("dueDate"))
    record.paid_at = _parse_paid_at(payment_data, event) or record.paid_at
    record.invoice_url = payment_data.get("invoiceUrl")


def _save_webhook_event(
    db: Session,
    event_id: str,
    event_type: str,
    processing_status: str,
    tenant_id=None,
    error: str | None = None,
) -> None:
    webhook_event = (
        db.query(models.AsaasWebhookEvent)
        .filter(models.AsaasWebhookEvent.id == event_id)
        .first()
    )
    if not webhook_event:
        webhook_event = models.AsaasWebhookEvent(id=event_id, event_type=event_type)
        db.add(webhook_event)
    webhook_event.event_type = event_type
    webhook_event.tenant_id = tenant_id
    webhook_event.status = processing_status
    webhook_event.error = error[:1000] if error else None


@router.post("/criar-assinatura/{plano}")
def criar_assinatura(
    plano: str,
    billing_cycle: Literal["monthly", "annual"] = Body("monthly", embed=True),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    tenant_id = current_user.get("tenant_id")
    tenant = db.query(models.Tenant).filter(models.Tenant.id == tenant_id).first()

    if not tenant:
        raise HTTPException(status_code=404, detail="Escritório não encontrado.")
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Apenas administradores podem contratar planos.")
    if tenant.asaas_subscription_id:
        raise HTTPException(
            status_code=409,
            detail=(
                "Já existe uma assinatura vinculada a este escritório. "
                "Solicite ao suporte a alteração de plano ou ciclo."
            ),
        )

    # 1. Valida o plano antes de criar ou atualizar recursos externos.
    if plano not in PLAN_CONFIG or plano == "free":
        raise HTTPException(status_code=400, detail="Plano inválido ou gratuito.")
    if billing_cycle not in {"monthly", "annual"}:
        raise HTTPException(status_code=400, detail="Ciclo de cobrança inválido.")

    # 2. Garante que o CPF/CNPJ esteja sincronizado inclusive para clientes existentes.
    asaas_customer_id = _ensure_asaas_customer(db, tenant)

    # 3. Cria a Assinatura no Asaas
    vencimento_amanha = (date.today() + timedelta(days=1)).strftime("%Y-%m-%d")
    assinatura_payload = {
        "customer": asaas_customer_id,
        "billingType": "UNDEFINED",
        "value": float(get_plan_price(plano, billing_cycle)),
        "cycle": "YEARLY" if billing_cycle == "annual" else "MONTHLY",
        "description": (
            f"Plano {PLAN_CONFIG[plano]['name']} "
            f"({'Anual' if billing_cycle == 'annual' else 'Mensal'}) - ContablyTask"
        ),
        "nextDueDate": vencimento_amanha,
        "externalReference": f"{tenant.id}:{plano}:{billing_cycle}",
    }

    with httpx.Client(timeout=HTTP_TIMEOUT) as client:
        response = client.post(
            f"{BASE_URL}/subscriptions", json=assinatura_payload, headers=headers
        )

    if response.status_code in [200, 201]:
        dados = response.json()
        subscription_id = dados.get("id")

        invoice_url = None
        with httpx.Client(timeout=HTTP_TIMEOUT) as client:
            resp_faturas = client.get(
                f"{BASE_URL}/payments?subscription={subscription_id}", headers=headers
            )
            if resp_faturas.status_code == 200:
                faturas = resp_faturas.json().get("data", [])
                if faturas:
                    invoice_url = faturas[0].get("invoiceUrl")

        tenant.status_pagamento = "aguardando_pagamento"
        tenant.asaas_subscription_id = subscription_id
        tenant.billing_cycle = billing_cycle
        db.commit()
        logger.info(f"Assinatura gerada para o tenant {tenant_id}. Aguardando pagamento.")

        return {
            "invoice_url": invoice_url,
            "message": "Assinatura criada! Redirecionando...",
        }
    else:
        erro_detalhe = response.text
        logger.error(f"[ASAAS ASSINATURA ERRO] Resposta: {erro_detalhe}")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY, detail="Falha ao gerar cobrança."
        )


# ==========================================
# WEBHOOK: Recebe o aviso do Asaas (Blindado para Produção)
# ==========================================
@router.post("/webhook")
async def asaas_webhook(request: Request, db: Session = Depends(get_db)):
    """Recebe eventos do Asaas, atualiza a assinatura e preserva o histórico local."""
    incoming_token = request.headers.get("asaas-access-token")
    if not ASAAS_WEBHOOK_TOKEN:
        logger.error("[WEBHOOK] ASAAS_WEBHOOK_TOKEN não configurado.")
        raise HTTPException(status_code=503, detail="Webhook indisponível.")
    if not incoming_token or not hmac.compare_digest(incoming_token, ASAAS_WEBHOOK_TOKEN):
        logger.warning("[WEBHOOK] Tentativa de acesso não autorizada ao webhook.")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido."
        )

    event_id = None
    event = "UNKNOWN"
    tenant = None
    try:
        body = await request.body()
        payload = json.loads(body)

        event = payload.get("event")
        event_id = payload.get("id")
        if not event or not event_id:
            raise HTTPException(status_code=400, detail="Evento inválido.")
        event_id = str(event_id)
        if len(event_id) > 100:
            raise HTTPException(status_code=400, detail="Identificador de evento inválido.")
        existing_event = (
            db.query(models.AsaasWebhookEvent)
            .filter(models.AsaasWebhookEvent.id == event_id)
            .first()
        )
        if existing_event and existing_event.status == "success":
            return {"status": "already_processed"}
        logger.info(f"[WEBHOOK RECEBIDO] Evento: {event}")

        payment_data = payload.get("payment", payload.get("subscription", payload))
        customer_id = payment_data.get("customer") or payload.get("customer")
        if customer_id:
            tenant = (
                db.query(models.Tenant)
                .filter(models.Tenant.asaas_customer_id == customer_id)
                .first()
            )

        if event in ["PAYMENT_RECEIVED", "PAYMENT_CONFIRMED"]:
            subscription_id = payment_data.get("subscription")
            if not tenant:
                raise HTTPException(status_code=404, detail="Cliente do gateway não encontrado.")
            if tenant.asaas_subscription_id and subscription_id != tenant.asaas_subscription_id:
                raise HTTPException(status_code=400, detail="Assinatura não corresponde ao cliente.")
            try:
                payment_value = Decimal(str(payment_data.get("value") or "0"))
            except InvalidOperation:
                payment_value = Decimal("0")
            subscription_match = identify_subscription_by_value(payment_value)
            if not subscription_match:
                raise HTTPException(
                    status_code=422,
                    detail="Valor recebido não corresponde a um plano ativo.",
                )
            activated_plan, activated_cycle = subscription_match
            old_status = tenant.status_pagamento
            tenant.status_pagamento = "ativo"
            tenant.plano = activated_plan
            tenant.billing_cycle = activated_cycle
            _upsert_payment_record(db, tenant, payment_data, event)
            db.add(
                models.AdminAuditLog(
                    tenant_id=tenant.id,
                    action="payment_confirmed",
                    reason=f"Pagamento confirmado pelo Asaas ({event}).",
                    old_value=old_status,
                    new_value=f"ativo:{activated_plan}:{activated_cycle}",
                )
            )
            logger.info(
                "[WEBHOOK SUCESSO] Pagamento confirmado para o tenant %s.", tenant.id
            )

        elif event in [
            "PAYMENT_OVERDUE",
            "PAYMENT_REFUNDED",
            "PAYMENT_DELETED",
            "SUBSCRIPTION_DELETED",
        ]:
            subscription_id = payment_data.get("subscription") or payment_data.get("id")
            if not tenant:
                raise HTTPException(status_code=404, detail="Cliente do gateway não encontrado.")
            if tenant.asaas_subscription_id and subscription_id != tenant.asaas_subscription_id:
                raise HTTPException(status_code=400, detail="Assinatura não corresponde ao cliente.")
            old_status = tenant.status_pagamento
            tenant.status_pagamento = "inadimplente"
            if event != "SUBSCRIPTION_DELETED":
                _upsert_payment_record(db, tenant, payment_data, event)
            db.add(
                models.AdminAuditLog(
                    tenant_id=tenant.id,
                    action="payment_issue",
                    reason=f"Status alterado automaticamente pelo evento {event}.",
                    old_value=old_status,
                    new_value="inadimplente",
                )
            )
            logger.warning("[WEBHOOK AVISO] Evento %s no tenant %s.", event, tenant.id)

        _save_webhook_event(
            db,
            event_id,
            event,
            "success",
            tenant.id if tenant else None,
        )
        db.commit()
        return {"status": "received"}

    except HTTPException as error:
        db.rollback()
        if event_id:
            _save_webhook_event(
                db,
                event_id,
                event,
                "failed",
                tenant.id if tenant else None,
                str(error.detail),
            )
            db.commit()
        raise
    except Exception as error:
        db.rollback()
        if event_id:
            _save_webhook_event(
                db,
                event_id,
                event,
                "failed",
                tenant.id if tenant else None,
                str(error),
            )
            db.commit()
        logger.exception("[ERRO WEBHOOK]")
        raise HTTPException(status_code=500, detail="Falha ao processar webhook.")
