import json
import hmac
import logging
from typing import Literal

from app_config import get_settings
from billing import (
    enqueue_webhook_event,
    process_webhook_event,
    verify_reconciliation_secret,
)
from database import get_db
from fastapi import APIRouter, Body, Depends, Header, HTTPException, Request, status
from security import get_current_user
from sqlalchemy.orm import Session
from subscription_service import create_subscription, reconcile_asaas

logger = logging.getLogger("ContablyTask.Asaas")
router = APIRouter(prefix="/api/v1/asaas", tags=["Pagamentos e Assinaturas"])

app_settings = get_settings()
ASAAS_WEBHOOK_TOKEN = app_settings.asaas_webhook_token
MAX_WEBHOOK_BYTES = 256 * 1024


@router.post("/criar-assinatura/{plano}")
def criar_assinatura(
    plano: str,
    billing_cycle: Literal["monthly", "annual"] = Body("monthly", embed=True),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    return create_subscription(
        db,
        current_user,
        plano,
        billing_cycle,
    )


@router.post("/webhook")
async def asaas_webhook(request: Request, db: Session = Depends(get_db)):
    incoming_token = request.headers.get("asaas-access-token")
    if not ASAAS_WEBHOOK_TOKEN:
        logger.error("ASAAS_WEBHOOK_TOKEN não configurado.")
        raise HTTPException(status_code=503, detail="Webhook indisponível.")
    if not incoming_token or not hmac.compare_digest(incoming_token, ASAAS_WEBHOOK_TOKEN):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido.")

    body = await request.body()
    if len(body) > MAX_WEBHOOK_BYTES:
        raise HTTPException(status_code=413, detail="Payload do webhook muito grande.")
    try:
        payload = json.loads(body)
    except (json.JSONDecodeError, UnicodeDecodeError) as error:
        raise HTTPException(status_code=400, detail="JSON inválido.") from error
    if not isinstance(payload, dict):
        raise HTTPException(status_code=400, detail="Evento inválido.")

    event, created = enqueue_webhook_event(db, payload)
    outcome = process_webhook_event(db, event.id, force=created)
    return {
        "status": "accepted" if created else "already_received",
        "processing_status": outcome,
    }


@router.post("/reconciliar")
def reconcile_asaas_endpoint(
    x_cron_secret: str | None = Header(default=None, alias="X-Cron-Secret"),
    db: Session = Depends(get_db),
):
    verify_reconciliation_secret(x_cron_secret)
    return reconcile_asaas(db)
