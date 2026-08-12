import json
import hmac
import logging
import os
import re
from datetime import date, timedelta

import httpx
import models
from database import get_db
from dotenv import load_dotenv
from fastapi import APIRouter, Depends, HTTPException, Request, status
from security import get_current_user
from sqlalchemy import update
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


@router.post("/criar-assinatura/{plano}")
def criar_assinatura(
    plano: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    tenant_id = current_user.get("tenant_id")
    tenant = db.query(models.Tenant).filter(models.Tenant.id == tenant_id).first()

    if not tenant:
        raise HTTPException(status_code=404, detail="Escritório não encontrado.")
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Apenas administradores podem contratar planos.")
    if tenant.status_pagamento == "aguardando_pagamento" and tenant.asaas_subscription_id:
        raise HTTPException(status_code=409, detail="Já existe uma assinatura aguardando pagamento.")

    # 1. Criação ou recuperação do Cliente no Asaas
    if not tenant.asaas_customer_id:
        cliente_payload = {"name": tenant.razao_social}

        # Em produção, o Asaas exige o CNPJ/CPF. No sandbox, ignoramos para não dar erro de dígito inválido.
        if os.getenv("ASAAS_ENV") == "production" and tenant.cnpj:
            cnpj_limpo = re.sub(r"\D", "", tenant.cnpj or "")
            if len(cnpj_limpo) == 14:
                cliente_payload["cpfCnpj"] = cnpj_limpo
            else:
                logger.warning(
                    f"CNPJ inválido para o tenant {tenant_id} na criação do cliente."
                )
        elif os.getenv("ASAAS_ENV") == "production" and not tenant.cnpj:
            # Proteção extra: se em produção e não tiver CNPJ, o Asaas pode barrar a cobrança.
            logger.warning(f"Tenant {tenant_id} tentou assinar sem CNPJ em produção.")

        with httpx.Client(timeout=HTTP_TIMEOUT) as client:
            response = client.post(
                f"{BASE_URL}/customers", json=cliente_payload, headers=headers
            )

        if response.status_code in [200, 201]:
            tenant.asaas_customer_id = response.json().get("id")
            db.commit()
            logger.info(f"Cliente criado no Asaas: {tenant.asaas_customer_id}")
        else:
            erro_detalhe = response.text
            logger.error(
                f"[ASAAS CLIENTE ERRO] Payload: {cliente_payload} | Resposta: {erro_detalhe}"
            )
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Falha ao registrar cliente no gateway.",
            )

    # 2. Definições do Plano (Removido o Starter, pois agora é Free)
    valores = {
        "basico": 79.90,
        "profissional": 149.90,
        "business": 449.00,
    }
    nomes_planos = {
        "basico": "Essencial",
        "profissional": "Profissional",
        "business": "Empresarial",
    }

    if plano not in valores:
        raise HTTPException(status_code=400, detail="Plano inválido ou gratuito.")

    # 3. Cria a Assinatura no Asaas
    vencimento_amanha = (date.today() + timedelta(days=1)).strftime("%Y-%m-%d")
    assinatura_payload = {
        "customer": tenant.asaas_customer_id,
        "billingType": "UNDEFINED",
        "value": valores[plano],
        "cycle": "MONTHLY",
        "description": f"Plano {nomes_planos[plano]} - ContablyTask",
        "nextDueDate": vencimento_amanha,
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
    """
    Rota pública que o Asaas chama quando um pagamento muda de status.
    """
    # 1. Segurança: Validação do Token do Webhook
    incoming_token = request.headers.get("asaas-access-token")
    if not ASAAS_WEBHOOK_TOKEN:
        logger.error("[WEBHOOK] ASAAS_WEBHOOK_TOKEN não configurado.")
        raise HTTPException(status_code=503, detail="Webhook indisponível.")
    if not incoming_token or not hmac.compare_digest(incoming_token, ASAAS_WEBHOOK_TOKEN):
        logger.warning("[WEBHOOK] Tentativa de acesso não autorizada ao webhook.")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido."
        )

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
        if db.query(models.AsaasWebhookEvent).filter(models.AsaasWebhookEvent.id == event_id).first():
            return {"status": "already_processed"}
        logger.info(f"[WEBHOOK RECEBIDO] Evento: {event}")

        # 2. Liberação de Acesso (Pagamento Confirmado)
        if event in ["PAYMENT_RECEIVED", "PAYMENT_CONFIRMED"]:
            payment_data = payload.get("payment", payload)
            customer_id = payment_data.get("customer") or payload.get("customer")

            # Pega o valor que o cliente pagou
            payment_value = payment_data.get("value")
            subscription_id = payment_data.get("subscription")

            if customer_id:
                tenant = db.query(models.Tenant).filter(models.Tenant.asaas_customer_id == customer_id).first()

                if tenant:
                    if tenant.asaas_subscription_id and subscription_id != tenant.asaas_subscription_id:
                        raise HTTPException(status_code=400, detail="Assinatura não corresponde ao cliente.")
                    # Descobre qual plano ele pagou baseado no valor
                    plano_ativado = None
                    payment_value = round(float(payment_value or 0), 2)
                    if payment_value == 79.90:
                        plano_ativado = "basico"
                    elif payment_value == 149.90:
                        plano_ativado = "profissional"
                    elif payment_value == 449.00:
                        plano_ativado = "business"

                    if plano_ativado:
                        # SÓ AQUI O PLANO É ALTERADO NO BANCO DE DADOS!
                        db.execute(
                            update(models.Tenant)
                            .where(models.Tenant.id == tenant.id)
                            .values(status_pagamento="ativo", plano=plano_ativado)
                        )
                        db.commit()
                        logger.info(f"[WEBHOOK SUCESSO] Pagamento de R${payment_value} confirmado! Plano {plano_ativado} liberado para {tenant.razao_social}.")
                    else:
                        logger.warning(f"[WEBHOOK AVISO] Pagamento recebido de R${payment_value}, mas não bate com nenhum plano.")
                else:
                    logger.warning(f"[WEBHOOK AVISO] Cliente do Asaas {customer_id} não encontrado no banco.")

        # 3. Bloqueio Automático (Inadimplência, Estorno ou Cancelamento)
        elif event in [
            "PAYMENT_OVERDUE",
            "PAYMENT_REFUNDED",
            "PAYMENT_DELETED",
            "SUBSCRIPTION_DELETED",
        ]:
            # O Asaas pode mandar o objeto em "payment" ou "subscription"
            data = payload.get("payment", payload.get("subscription", payload))
            customer_id = data.get("customer") or payload.get("customer")
            subscription_id = data.get("subscription") or data.get("id")

            if customer_id:
                tenant = (
                    db.query(models.Tenant)
                    .filter(models.Tenant.asaas_customer_id == customer_id)
                    .first()
                )
                if tenant:
                    if tenant.asaas_subscription_id and subscription_id != tenant.asaas_subscription_id:
                        raise HTTPException(status_code=400, detail="Assinatura não corresponde ao cliente.")
                    db.execute(
                        update(models.Tenant)
                        .where(models.Tenant.id == tenant.id)
                        .values(status_pagamento="inadimplente")
                    )
                    db.commit()
                    logger.warning(
                        f"[WEBHOOK AVISO] Evento {event}. Escritório {tenant.razao_social} bloqueado."
                    )

        db.add(models.AsaasWebhookEvent(id=event_id, event_type=event))
        db.commit()
        return {"status": "received"}

    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"[ERRO WEBHOOK] {str(e)}")
        raise HTTPException(status_code=500, detail="Falha ao processar webhook.")
