import os
import sys
import asyncio
from types import SimpleNamespace

import pytest
from pydantic import ValidationError

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import contact
from contact import ContactMessage


def test_contact_message_accepts_known_subject():
    message = ContactMessage(
        nome="Cliente Teste",
        email="cliente@example.com",
        empresa="Escritório Teste",
        assunto="Quero conhecer a plataforma",
        mensagem="Gostaria de receber mais informações sobre o produto.",
        captcha_token="token-seguro-de-teste",
    )
    assert message.nome == "Cliente Teste"


def test_contact_message_rejects_unknown_subject():
    with pytest.raises(ValidationError):
        ContactMessage(
            nome="Cliente Teste",
            email="cliente@example.com",
            assunto="Assunto injetado",
            mensagem="Mensagem com tamanho suficiente para validação.",
            captcha_token="token-seguro-de-teste",
        )


def test_contact_endpoint_accepts_valid_message(monkeypatch):
    async def fake_verify_turnstile(token: str, client_ip: str):
        return None

    monkeypatch.setattr(contact, "verify_turnstile", fake_verify_turnstile)
    monkeypatch.setattr(contact, "send_email", lambda payload: None)
    async def fake_run_in_threadpool(function, *args):
        return function(*args)

    monkeypatch.setattr(contact, "run_in_threadpool", fake_run_in_threadpool)
    contact._attempts.clear()

    payload = ContactMessage(
        nome="Cliente Teste",
        email="cliente@example.com",
        empresa="Escritório Teste",
        assunto="Dúvida sobre planos",
        mensagem="Gostaria de entender qual plano atende meu escritório.",
        captcha_token="token-seguro-de-teste",
    )
    request = SimpleNamespace(client=SimpleNamespace(host="testclient"))
    response = asyncio.run(contact.submit_contact(payload, request))

    assert "Mensagem recebida" in response["message"]
