from types import SimpleNamespace
from uuid import UUID, uuid4

import client_service
import models
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
