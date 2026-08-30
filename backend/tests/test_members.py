from types import SimpleNamespace
from uuid import uuid4

import pytest
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError

import membros


class FakeQuery:
    def __init__(self, db, model):
        self.db = db
        self.model = model

    def filter(self, *_args):
        return self

    def with_for_update(self):
        self.db.tenant_locked = True
        return self

    def first(self):
        if self.model is membros.models.Tenant:
            return self.db.tenant
        return self.db.profile_results.pop(0) if self.db.profile_results else None

    def count(self):
        if len(self.db.profile_counts) > 1:
            return self.db.profile_counts.pop(0)
        return self.db.profile_counts[0]


class FakeMemberDb:
    def __init__(self, *, fail_profile_commit=False, profile_counts=None):
        self.tenant = SimpleNamespace(id=uuid4(), plano="profissional")
        self.profile_counts = list(profile_counts or [1, 1])
        self.profile_results = [None, None]
        self.fail_profile_commit = fail_profile_commit
        self.tenant_locked = False
        self.added_profile = None
        self.rollbacks = 0

    def query(self, model):
        return FakeQuery(self, model)

    def add(self, entity):
        if isinstance(entity, membros.models.Profile):
            self.added_profile = entity

    def commit(self):
        if self.fail_profile_commit and self.added_profile is not None:
            raise IntegrityError("INSERT profiles", {}, RuntimeError("falha local"))

    def rollback(self):
        self.rollbacks += 1

    def refresh(self, _entity):
        return None

    def expire_all(self):
        return None


class FakeSupabaseClient:
    created_user_id = uuid4()
    deleted_urls = []
    post_calls = []

    def __init__(self, **_kwargs):
        pass

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return None

    def post(self, url, **kwargs):
        self.post_calls.append((url, kwargs))
        return SimpleNamespace(
            status_code=201,
            json=lambda: {"id": str(self.created_user_id)},
        )

    def delete(self, url, **_kwargs):
        self.deleted_urls.append(url)
        return SimpleNamespace(status_code=204)


def member_payload():
    return membros.ProfileCreate(
        name="Maria Contadora",
        email="maria@example.com",
        role="colaborador",
    )


def admin_user(tenant_id):
    return {
        "tenant_id": str(tenant_id),
        "user_id": str(uuid4()),
        "role": "admin",
        "is_superadmin": False,
    }


def test_falha_local_remove_usuario_criado_no_supabase(monkeypatch):
    db = FakeMemberDb(fail_profile_commit=True)
    FakeSupabaseClient.deleted_urls = []
    monkeypatch.setattr(membros.httpx, "Client", FakeSupabaseClient)

    with pytest.raises(HTTPException) as error:
        membros.adicionar_membro(member_payload(), db, admin_user(db.tenant.id))

    assert error.value.status_code == 500
    assert db.rollbacks >= 1
    assert FakeSupabaseClient.deleted_urls == [
        f"{membros.SUPABASE_URL.rstrip('/')}/auth/v1/admin/users/"
        f"{FakeSupabaseClient.created_user_id}"
    ]


def test_limite_de_membros_e_verificado_com_bloqueio_do_escritorio(monkeypatch):
    db = FakeMemberDb()
    FakeSupabaseClient.deleted_urls = []
    monkeypatch.setattr(membros.httpx, "Client", FakeSupabaseClient)

    created = membros.adicionar_membro(member_payload(), db, admin_user(db.tenant.id))

    assert db.tenant_locked is True
    assert created.id == FakeSupabaseClient.created_user_id


def test_novo_membro_recebe_convite_sem_senha_definida_pelo_admin(monkeypatch):
    db = FakeMemberDb()
    FakeSupabaseClient.post_calls = []
    monkeypatch.setattr(membros.httpx, "Client", FakeSupabaseClient)

    membros.adicionar_membro(member_payload(), db, admin_user(db.tenant.id))

    assert len(FakeSupabaseClient.post_calls) == 1
    url, request = FakeSupabaseClient.post_calls[0]
    assert url == f"{membros.SUPABASE_URL.rstrip('/')}/auth/v1/invite"
    assert request["params"] == {"redirect_to": membros.INVITE_REDIRECT_URL}
    assert request["json"] == {
        "email": "maria@example.com",
        "data": {
            "name": "Maria Contadora",
            "tenant_id": str(db.tenant.id),
        },
    }
    assert "password" not in request["json"]
    assert "email_confirm" not in request["json"]


def test_concorrencia_no_limite_compensa_usuario_excedente(monkeypatch):
    db = FakeMemberDb(profile_counts=[4, 6])
    db.tenant.plano = "basico"
    db.profile_results = [
        None,
        SimpleNamespace(
            id=FakeSupabaseClient.created_user_id,
            tenant_id=db.tenant.id,
            name="Maria Contadora",
            email="maria@example.com",
            role="colaborador",
        ),
    ]
    FakeSupabaseClient.deleted_urls = []
    monkeypatch.setattr(membros.httpx, "Client", FakeSupabaseClient)

    with pytest.raises(HTTPException) as error:
        membros.adicionar_membro(member_payload(), db, admin_user(db.tenant.id))

    assert error.value.status_code == 403
    assert FakeSupabaseClient.deleted_urls == [
        f"{membros.SUPABASE_URL.rstrip('/')}/auth/v1/admin/users/"
        f"{FakeSupabaseClient.created_user_id}"
    ]
