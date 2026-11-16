import asyncio
import os
import sys
from types import SimpleNamespace
from uuid import uuid4

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import clientes
import models
import pytest
from fastapi import HTTPException
from schemas import ClientCreate
from sqlalchemy.exc import IntegrityError


class FakeQuery:
    def __init__(self, db, model):
        self.db = db
        self.model = model
        self.selected_entities = False

    def filter(self, *_args):
        return self

    def with_for_update(self):
        if self.model is models.Tenant:
            self.db.tenant_locked = True
        return self

    def with_entities(self, *_args):
        self.selected_entities = True
        return self

    def all(self):
        if self.model is models.Client and self.selected_entities:
            self.db.document_batch_queries += 1
        return []

    def first(self):
        if self.model is models.Tenant:
            return self.db.tenant
        return None

    def count(self):
        assert self.db.tenant_locked, "clientes foram contados antes do bloqueio do escritório"
        return self.db.active_clients


class FakeClientDb:
    def __init__(self):
        self.tenant = SimpleNamespace(id=uuid4(), plano="free")
        self.tenant_locked = False
        self.active_clients = 0
        self.pending = []
        self.persisted = []
        self.commits = 0
        self.rollbacks = 0
        self.commit_error = None
        self.document_batch_queries = 0

    def query(self, model):
        return FakeQuery(self, model)

    def add(self, entity):
        self.pending.append(entity)

    def commit(self):
        self.commits += 1
        if self.commit_error:
            raise self.commit_error
        self.persisted.extend(self.pending)
        self.pending = []

    def rollback(self):
        self.rollbacks += 1
        self.pending = []

    def refresh(self, entity):
        entity.id = uuid4()


class FakeUpload:
    def __init__(self, contents=None, filename="clientes.csv"):
        self.filename = filename
        self.read_count = 0
        self.contents = contents if contents is not None else (
            b"TIPO (PF/PJ);NOME_OU_RAZAO;CPF_OU_CNPJ;REGIME_TRIBUTARIO\n"
            b"PJ;Empresa Teste;12345678000190;Simples Nacional\n"
        )

    async def read(self, _size):
        self.read_count += 1
        return self.contents


def admin_user(tenant_id):
    return {
        "tenant_id": str(tenant_id),
        "user_id": str(uuid4()),
        "role": "admin",
        "is_superadmin": False,
    }


def collaborator_user(tenant_id):
    user = admin_user(tenant_id)
    user["role"] = "colaborador"
    return user


def test_importacao_rejeita_usuario_sem_permissao_antes_de_ler_arquivo():
    db = FakeClientDb()
    upload = FakeUpload()

    with pytest.raises(HTTPException) as error:
        asyncio.run(
            clientes.importar_clientes_csv(
                upload,
                db,
                collaborator_user(db.tenant.id),
            )
        )

    assert error.value.status_code == 403
    assert upload.read_count == 0


def test_criacao_serializa_limite_antes_de_contar_clientes():
    db = FakeClientDb()
    payload = ClientCreate(
        tipo_pessoa="PJ",
        razao_social="Empresa Teste",
        cnpj="12.345.678/0001-90",
        regime_tributario="Simples Nacional",
    )

    created = clientes.criar_cliente(payload, db, admin_user(db.tenant.id))

    assert db.tenant_locked is True
    assert created in db.persisted


def test_importacao_csv_serializa_limite_antes_de_contar_clientes():
    db = FakeClientDb()

    result = asyncio.run(
        clientes.importar_clientes_csv(
            FakeUpload(), db, admin_user(db.tenant.id)
        )
    )

    assert db.tenant_locked is True
    assert result["importados"] == 1


def test_importacao_consulta_documentos_existentes_em_lote():
    db = FakeClientDb()
    upload = FakeUpload(
        b"TIPO (PF/PJ);NOME_OU_RAZAO;CPF_OU_CNPJ;REGIME_TRIBUTARIO\n"
        b"PJ;Empresa Um;12345678000190;Simples Nacional\n"
        b"PJ;Empresa Dois;12345678000191;Simples Nacional\n"
    )

    result = asyncio.run(
        clientes.importar_clientes_csv(upload, db, admin_user(db.tenant.id))
    )

    assert result["importados"] == 2
    assert db.document_batch_queries == 1


def test_importacao_acima_do_limite_nao_persiste_nenhuma_linha():
    db = FakeClientDb()
    db.active_clients = 4
    upload = FakeUpload(
        b"TIPO (PF/PJ);NOME_OU_RAZAO;CPF_OU_CNPJ;REGIME_TRIBUTARIO\n"
        b"PJ;Empresa Um;12345678000190;Simples Nacional\n"
        b"PJ;Empresa Dois;12345678000191;Simples Nacional\n"
    )

    with pytest.raises(HTTPException) as error:
        asyncio.run(
            clientes.importar_clientes_csv(upload, db, admin_user(db.tenant.id))
        )

    assert error.value.status_code == 403
    assert "Nenhum cliente foi importado" in error.value.detail
    assert db.persisted == []
    assert db.pending == []
    assert db.commits == 0
    assert db.rollbacks == 1


@pytest.mark.parametrize("header", [
    b"TIPO;NOME;DOCUMENTO\n", b"TIPO (PF/PJ);NOME_OU_RAZAO;CPF_OU_CNPJ;CPF_OU_CNPJ\n", b"",
])
def test_invalid_csv_headers_never_write_clients(header):
    db = FakeClientDb()
    with pytest.raises(HTTPException) as caught:
        asyncio.run(clientes.importar_clientes_csv(FakeUpload(header), db, admin_user(db.tenant.id)))
    assert caught.value.status_code == 400
    assert db.persisted == []


def test_csv_rejects_extra_values_and_invalid_fields_without_losing_valid_rows():
    db = FakeClientDb()
    csv = (
        b"TIPO (PF/PJ);NOME_OU_RAZAO;CPF_OU_CNPJ;REGIME_TRIBUTARIO\n"
        b"PJ;Empresa;12345678000195;Simples Nacional\n"
        b"PF;Pessoa;12345678901;Simples Nacional\n"
        b"PJ;Empresa;94837261000104;X\n"
        b"PJ;Empresa;94837261000104;Simples Nacional;extra\n"
        b"PJ;Duplicado;12345678000195;Simples Nacional\n"
    )
    result = asyncio.run(clientes.importar_clientes_csv(FakeUpload(csv), db, admin_user(db.tenant.id)))
    assert result["importados"] == 2
    assert result["erros"] == 3
    assert db.persisted[0].cpf is None
    assert db.persisted[1].cnpj is None


def test_csv_unknown_database_error_is_not_reported_as_duplicate():
    db = FakeClientDb()
    db.commit_error = IntegrityError("INSERT", {}, RuntimeError("foreign key"))
    with pytest.raises(HTTPException) as caught:
        asyncio.run(clientes.importar_clientes_csv(FakeUpload(), db, admin_user(db.tenant.id)))
    assert caught.value.status_code == 500
    assert "Nenhum cliente foi importado" in caught.value.detail
    assert db.persisted == []
    assert db.rollbacks == 1


def test_falha_no_commit_reverte_toda_a_importacao():
    db = FakeClientDb()
    original = RuntimeError("documento duplicado")
    original.diag = SimpleNamespace(constraint_name="uq_clients_tenant_cnpj")
    db.commit_error = IntegrityError(
        "INSERT clients", {}, original
    )

    with pytest.raises(HTTPException) as error:
        asyncio.run(
            clientes.importar_clientes_csv(
                FakeUpload(), db, admin_user(db.tenant.id)
            )
        )

    assert error.value.status_code == 409
    assert "Nenhum cliente foi importado" in error.value.detail
    assert db.persisted == []
    assert db.pending == []
    assert db.rollbacks == 1
