from types import SimpleNamespace
from uuid import UUID, uuid4

import client_service
import models
import pytest
from fastapi import HTTPException
from sqlalchemy import Column, MetaData, Table, UniqueConstraint, create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from schemas import ClientCreate


class ClientDb:
    def __init__(self):
        self.added = []
        self.commits = 0
        self.rollbacks = 0
        self.refreshed = []

    def add(self, value):
        self.added.append(value)

    def commit(self):
        self.commits += 1

    def rollback(self):
        self.rollbacks += 1

    def refresh(self, value):
        self.refreshed.append(value)


def make_user(role="admin"):
    return {
        "tenant_id": str(uuid4()),
        "user_id": str(uuid4()),
        "role": role,
    }


def test_list_clients_returns_summary_from_authorized_scope(monkeypatch):
    class ClientQuery:
        def filter(self, *_values):
            return self

        def with_entities(self, *_values):
            return self

        def one(self):
            return (12, 8, 4)

        def order_by(self, *_values):
            return self

    query = ClientQuery()
    repository = SimpleNamespace(query=lambda _model: query)
    monkeypatch.setattr(client_service, "tenant_repository", lambda *_args: repository)
    monkeypatch.setattr(client_service, "apply_client_scope", lambda value, _user: value)
    monkeypatch.setattr(
        client_service,
        "paginate",
        lambda value, **options: {"query": value, **options},
    )

    result = client_service.list_clients(
        object(),
        make_user(),
        client_service.ClientListFilters(page=2, page_size=20),
    )

    assert result["query"] is query
    assert result["page"] == 2
    assert result["page_size"] == 20
    assert result["summary"] == {"total": 12, "pj": 8, "pf": 4}


def test_create_client_uses_authorized_tenant_and_validates_responsible(monkeypatch):
    database = ClientDb()
    current_user = make_user()
    responsible_id = uuid4()
    payload = ClientCreate(
        tipo_pessoa="PJ",
        razao_social="Empresa Teste",
        cnpj="12.345.678/0001-90",
        regime_tributario="Simples Nacional",
        responsible_profile_id=responsible_id,
    )
    repository = SimpleNamespace(
        context=SimpleNamespace(tenant_id=UUID(current_user["tenant_id"])),
        query=lambda _model: SimpleNamespace(filter=lambda *_args: SimpleNamespace(first=lambda: None)),
    )
    validated = []
    monkeypatch.setattr(client_service, "tenant_repository", lambda *_args: repository)
    monkeypatch.setattr(
        client_service,
        "validate_responsible_profile",
        lambda _db, _user, profile_id: validated.append(profile_id),
    )
    monkeypatch.setattr(
        client_service,
        "_lock_tenant_and_get_client_capacity",
        lambda *_args: (SimpleNamespace(plano="free"), 5, 0),
    )

    client = client_service.create_client(database, current_user, payload)

    assert client.tenant_id == UUID(current_user["tenant_id"])
    assert client.cnpj == "12345678000190"
    assert validated == [responsible_id]
    assert database.added == [client]
    assert database.commits == 1
    assert database.refreshed == [client]


@pytest.mark.parametrize("person_type", ["PJ", "PF"])
def test_create_multiple_clients_with_empty_inapplicable_document(monkeypatch, person_type):
    engine = create_engine("sqlite:///:memory:")
    metadata = MetaData()
    Table(
        "clients", metadata,
        *(Column(column.name, column.type, primary_key=column.primary_key)
          for column in models.Client.__table__.columns),
        UniqueConstraint("tenant_id", "cpf"),
        UniqueConstraint("tenant_id", "cnpj"),
    )
    metadata.create_all(engine)
    user = make_user()
    monkeypatch.setattr(client_service, "validate_responsible_profile", lambda *_args: None)
    monkeypatch.setattr(client_service, "_find_client_by_document", lambda *_args, **_kw: None)
    monkeypatch.setattr(client_service, "_lock_tenant_and_get_client_capacity",
                        lambda *_args: (SimpleNamespace(plano="free"), 5, 0))
    try:
        with Session(engine) as database:
            for index in range(2):
                payload = ClientCreate(
                    tipo_pessoa=person_type,
                    razao_social="Empresa" if person_type == "PJ" else "",
                    nome="Pessoa" if person_type == "PF" else "",
                    cnpj=f"1234567800019{index}" if person_type == "PJ" else "",
                    cpf=f"1234567890{index}" if person_type == "PF" else "",
                    regime_tributario="Simples Nacional",
                )
                client = client_service.create_client(database, user, payload)
                assert (client.cpf if person_type == "PJ" else client.cnpj) is None
            assert database.query(models.Client).count() == 2
    finally:
        engine.dispose()


@pytest.mark.parametrize("constraint, expected_status", [
    ("uq_clients_tenant_cpf", 409),
    ("uq_clients_tenant_cnpj", 409),
    ("uq_tenant_cnpj", 409),
    ("fk_clients_tenant_id", 500),
    (None, 500),
])
def test_create_client_only_reports_known_document_conflicts(monkeypatch, constraint, expected_status):
    database = ClientDb()
    user = make_user()
    repository = SimpleNamespace(context=SimpleNamespace(tenant_id=UUID(user["tenant_id"])))
    monkeypatch.setattr(client_service, "tenant_repository", lambda *_args: repository)
    monkeypatch.setattr(client_service, "validate_responsible_profile", lambda *_args: None)
    monkeypatch.setattr(client_service, "_find_client_by_document", lambda *_args, **_kw: None)
    monkeypatch.setattr(client_service, "_lock_tenant_and_get_client_capacity",
                        lambda *_args: (SimpleNamespace(plano="free"), 5, 0))
    original = Exception("private database details")
    original.diag = SimpleNamespace(constraint_name=constraint)

    def fail_commit():
        raise IntegrityError("INSERT", {"private": "data"}, original)

    database.commit = fail_commit
    with pytest.raises(HTTPException) as caught:
        client_service.create_client(database, user, ClientCreate(
            razao_social="Empresa", cnpj="12345678000195", regime_tributario="Simples Nacional",
        ))
    assert caught.value.status_code == expected_status
    assert ("já cadastrado" in caught.value.detail) == (expected_status == 409)
    assert "private" not in caught.value.detail
    assert database.rollbacks == 1


def test_assign_responsible_validates_profile_and_persists(monkeypatch):
    database = ClientDb()
    current_user = make_user("gerente")
    responsible_id = uuid4()
    client = SimpleNamespace(id=uuid4(), responsible_profile_id=None)
    repository = SimpleNamespace(get=lambda *_args, **_kwargs: client)
    validated = []
    monkeypatch.setattr(client_service, "tenant_repository", lambda *_args: repository)
    monkeypatch.setattr(
        client_service,
        "validate_responsible_profile",
        lambda _db, _user, profile_id: validated.append(profile_id),
    )

    result = client_service.assign_responsible(
        database, current_user, client.id, responsible_id
    )

    assert result is client
    assert client.responsible_profile_id == responsible_id
    assert validated == [responsible_id]
    assert database.commits == 1
    assert database.refreshed == [client]


def test_deactivate_client_uses_tenant_scoped_resource(monkeypatch):
    database = ClientDb()
    current_user = make_user()
    client = SimpleNamespace(id=uuid4(), ativo=True)
    repository = SimpleNamespace(get=lambda *_args, **_kwargs: client)
    monkeypatch.setattr(client_service, "tenant_repository", lambda *_args: repository)

    result = client_service.deactivate_client(database, current_user, client.id)

    assert result is client
    assert client.ativo is False
    assert database.commits == 1
    assert database.refreshed == [client]
