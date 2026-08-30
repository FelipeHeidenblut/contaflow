import logging
import os
import smtplib
import ssl
import threading
import time
from collections import defaultdict, deque
from email.message import EmailMessage
from typing import Literal

import httpx
from app_config import get_settings
from fastapi import APIRouter, HTTPException, Request, status
from fastapi.concurrency import run_in_threadpool
from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/contact", tags=["Contato"])
settings = get_settings()

CONTACT_SUBJECTS = Literal[
    "Dúvida sobre planos",
    "Quero conhecer a plataforma",
    "Suporte técnico",
    "Plano Empresarial",
    "Outro assunto",
]


class ContactMessage(BaseModel):
    model_config = ConfigDict(extra="forbid")
    nome: str = Field(..., min_length=2, max_length=120)
    email: EmailStr
    empresa: str = Field(default="", max_length=150)
    assunto: CONTACT_SUBJECTS
    mensagem: str = Field(..., min_length=10, max_length=4000)
    captcha_token: str = Field(..., min_length=10, max_length=4096)

    @field_validator("nome", "empresa", "mensagem")
    @classmethod
    def normalize_text(cls, value: str):
        return value.strip()


RATE_LIMIT_WINDOW = 15 * 60
RATE_LIMIT_MAX = 5
_attempts: dict[str, deque[float]] = defaultdict(deque)
_attempts_lock = threading.Lock()


def enforce_rate_limit(client_ip: str):
    now = time.monotonic()
    with _attempts_lock:
        attempts = _attempts[client_ip]
        while attempts and now - attempts[0] > RATE_LIMIT_WINDOW:
            attempts.popleft()
        if len(attempts) >= RATE_LIMIT_MAX:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Muitas mensagens enviadas. Aguarde alguns minutos e tente novamente.",
            )
        attempts.append(now)


async def verify_turnstile(token: str, client_ip: str):
    secret = os.getenv("TURNSTILE_SECRET_KEY")
    if not secret:
        if settings.is_production:
            logger.error("TURNSTILE_SECRET_KEY não configurada para o formulário de contato.")
            raise HTTPException(status_code=503, detail="Formulário temporariamente indisponível.")
        logger.warning("Validação Turnstile ignorada fora de produção por falta de configuração.")
        return

    try:
        async with httpx.AsyncClient(timeout=8.0) as client:
            response = await client.post(
                "https://challenges.cloudflare.com/turnstile/v0/siteverify",
                data={"secret": secret, "response": token, "remoteip": client_ip},
            )
            response.raise_for_status()
            verification = response.json()
    except (httpx.HTTPError, ValueError):
        logger.exception("Falha ao validar Turnstile no formulário de contato.")
        raise HTTPException(status_code=503, detail="Não foi possível validar o envio.")

    if verification.get("success") is not True:
        raise HTTPException(status_code=400, detail="Verificação de segurança inválida ou expirada.")


def send_email(payload: ContactMessage):
    host = os.getenv("SMTP_HOST")
    sender = os.getenv("CONTACT_FROM_EMAIL")
    recipient = os.getenv("CONTACT_TO_EMAIL", "contato@contablytask.com.br")
    if not host or not sender:
        logger.error("SMTP_HOST ou CONTACT_FROM_EMAIL não configurado.")
        raise RuntimeError("Serviço de e-mail não configurado.")

    port = int(os.getenv("SMTP_PORT", "587"))
    username = os.getenv("SMTP_USERNAME")
    password = os.getenv("SMTP_PASSWORD")
    use_ssl = os.getenv("SMTP_USE_SSL", "false").lower() == "true"
    use_tls = os.getenv("SMTP_USE_TLS", "true").lower() == "true"

    message = EmailMessage()
    message["Subject"] = f"[ContablyTask] {payload.assunto}"
    message["From"] = sender
    message["To"] = recipient
    message["Reply-To"] = str(payload.email)
    message.set_content(
        "\n".join(
            [
                f"Nome: {payload.nome}",
                f"E-mail: {payload.email}",
                f"Escritório: {payload.empresa or '-'}",
                f"Assunto: {payload.assunto}",
                "",
                payload.mensagem,
            ]
        )
    )

    context = ssl.create_default_context()
    smtp_connection = (
        smtplib.SMTP_SSL(host, port, timeout=10, context=context)
        if use_ssl
        else smtplib.SMTP(host, port, timeout=10)
    )
    with smtp_connection as smtp:
        if use_tls and not use_ssl:
            smtp.starttls(context=context)
        if username and password:
            smtp.login(username, password)
        smtp.send_message(message)


@router.post("", status_code=status.HTTP_202_ACCEPTED)
async def submit_contact(payload: ContactMessage, request: Request):
    client_ip = request.client.host if request.client else "unknown"
    enforce_rate_limit(client_ip)
    await verify_turnstile(payload.captcha_token, client_ip)
    try:
        await run_in_threadpool(send_email, payload)
    except (OSError, smtplib.SMTPException, RuntimeError, ValueError):
        logger.exception("Falha ao enviar mensagem do formulário de contato.")
        raise HTTPException(
            status_code=503,
            detail="Não foi possível enviar agora. Tente novamente ou use nosso e-mail de contato.",
        )
    return {"message": "Mensagem recebida. Responderemos normalmente em até um dia útil."}
