import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import pytest
from pydantic import ValidationError
from auth import SincronizarCadastroSchema
from schemas import ClientCreate, TaskCreate
from clientes import criar_cliente
import models
from datetime import date
from types import SimpleNamespace
from uuid import uuid4

def test_sincronizar_cadastro_rejeita_identidade_enviada_pelo_cliente():
    with pytest.raises(ValidationError):
        SincronizarCadastroSchema(
            supabase_user_id=str(uuid4()),
            nome_completo="Usuário Teste",
            nome_escritorio="Escritório Teste",
            documento="52998224725",
        )


def test_cpf_com_tamanho_invalido_e_rejeitado():
    with pytest.raises(ValidationError):
        ClientCreate(
            tipo_pessoa="PF",
            nome="Pessoa Teste",
            cpf="111.111.111-1",
            regime_tributario="Isento",
        )


def test_cpf_valido_e_normalizado():
    cliente = ClientCreate(
        tipo_pessoa="PF",
        nome="Pessoa Teste",
        cpf="529.982.247-25",
        regime_tributario="Isento",
    )
    assert cliente.cpf == "52998224725"


def test_cnpj_do_template_do_mvp_e_aceito_e_normalizado():
    cliente = ClientCreate(
        tipo_pessoa="PJ",
        razao_social="Transportes LTDA",
        cnpj="12.345.678/0001-90",
        regime_tributario="Simples Nacional",
    )
    assert cliente.cnpj == "12345678000190"


class FakeQuery:
    def __init__(self, entity):
        self.entity = entity

    def filter(self, *args):
        return self

    def first(self):
        if self.entity is models.Tenant:
            return SimpleNamespace(plano="free")
        return None

    def count(self):
        return 0


class FakeDb:
    def query(self, entity):
        return FakeQuery(entity)

    def add(self, entity):
        self.added = entity

    def commit(self):
        return None

    def rollback(self):
        return None

    def refresh(self, entity):
        entity.id = uuid4()


def test_fluxo_de_criacao_de_cliente_do_escritorio():
    payload = ClientCreate(
        tipo_pessoa="PJ",
        razao_social="Transportes LTDA",
        cnpj="12.345.678/0001-90",
        regime_tributario="Simples Nacional",
        natureza_operacao="Serviços",
    )
    tenant_id = str(uuid4())
    cliente = criar_cliente(payload, FakeDb(), {"tenant_id": tenant_id})
    assert cliente.cnpj == "12345678000190"
    assert str(cliente.tenant_id) == tenant_id


def test_tarefa_recorrente_exige_dia():
    with pytest.raises(ValidationError):
        TaskCreate(
            title="Enviar obrigação",
            due_date=date.today(),
            client_id=uuid4(),
            is_recurring=True,
        )


def test_modelo_de_tarefa_urgente_e_aceito():
    tarefa = TaskCreate(
        title="Folha de pagamento",
        due_date=date.today(),
        client_id=uuid4(),
        grau_importancia="Urgente",
    )
    assert tarefa.grau_importancia == "Urgente"
