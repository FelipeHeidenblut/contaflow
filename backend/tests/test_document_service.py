import asyncio
from types import SimpleNamespace
from uuid import UUID, uuid4

import document_service
import pytest
from fastapi import HTTPException


class DocumentDb:
    def __init__(self):
        self.added = []
        self.deleted = []
        self.commits = 0
        self.rollbacks = 0
        self.refreshed = []
        self.commit_error = None
        self.add_error = None

    def add(self, value):
        if self.add_error:
            raise self.add_error
        self.added.append(value)

    def delete(self, value):
        self.deleted.append(value)

    def commit(self):
        self.commits += 1
        if self.commit_error:
            raise self.commit_error

    def rollback(self):
        self.rollbacks += 1

    def refresh(self, value):
        self.refreshed.append(value)


class FakeUpload:
    def __init__(self, contents=b"%PDF-documento", filename="relatorio.pdf"):
        self.filename = filename
        self.contents = contents
        self.read_count = 0

    async def read(self, _size):
        self.read_count += 1
        if self.read_count == 1:
            return self.contents
        return b""


class FakeBucket:
    def __init__(self):
        self.uploaded = []
        self.removed = []
        self.remove_error = None
        self.signed_response = {"signedURL": "https://storage.example/documento"}

    def upload(self, path, source, file_options):
        self.uploaded.append((path, source.read(), file_options))

    def remove(self, paths):
        if self.remove_error:
            raise self.remove_error
        self.removed.extend(paths)

    def create_signed_url(self, path, expires_in):
        return self.signed_response | {"path": path, "expires_in": expires_in}


class FakeStorageClient:
    def __init__(self, bucket):
        self.bucket = bucket
        self.requested_buckets = []
        self.storage = self

    def from_(self, bucket_name):
        self.requested_buckets.append(bucket_name)
        return self.bucket


def make_user(role="admin"):
    return {
        "tenant_id": str(uuid4()),
        "user_id": str(uuid4()),
        "role": role,
    }


def authorized_repository(current_user, document=None):
    return SimpleNamespace(
        context=SimpleNamespace(
            tenant_id=UUID(current_user["tenant_id"]),
            user_id=UUID(current_user["user_id"]),
        ),
        get=lambda *_args, **_kwargs: document,
    )


def test_list_documents_returns_summary_from_authorized_scope(monkeypatch):
    class DocumentQuery:
        def join(self, *_values):
            return self

        def with_entities(self, *_values):
            return self

        def one(self):
            return (9, 3, 2, 4)

        def order_by(self, *_values):
            return self

    query = DocumentQuery()
    repository = SimpleNamespace(query=lambda _model: query)
    monkeypatch.setattr(document_service, "tenant_repository", lambda *_args: repository)
    monkeypatch.setattr(document_service, "apply_client_scope", lambda value, _user: value)
    monkeypatch.setattr(
        document_service,
        "paginate",
        lambda value, **options: {"query": value, **options},
    )

    result = document_service.list_documents(
        object(),
        make_user(),
        document_service.DocumentListFilters(page=2, page_size=20),
    )

    assert result["query"] is query
    assert result["summary"] == {
        "total": 9,
        "fiscal": 3,
        "contabil": 2,
        "geral": 4,
    }


def test_upload_persists_document_with_tenant_scoped_random_path(monkeypatch):
    database = DocumentDb()
    bucket = FakeBucket()
    storage = FakeStorageClient(bucket)
    current_user = make_user()
    client_id = uuid4()
    repository = authorized_repository(current_user)
    monkeypatch.setattr(document_service, "tenant_repository", lambda *_args: repository)
    monkeypatch.setattr(
        document_service,
        "get_accessible_client",
        lambda *_args, **_kwargs: object(),
    )

    document = asyncio.run(
        document_service.upload_document(
            database,
            current_user,
            storage,
            "documents-test",
            client_id=client_id,
            task_id=None,
            category="Fiscal",
            upload=FakeUpload(filename="../relatorio.pdf"),
        )
    )

    assert document.nome_arquivo == "relatorio.pdf"
    assert document.tenant_id == UUID(current_user["tenant_id"])
    assert document.storage_path.startswith(
        f"{current_user['tenant_id']}/{client_id}/"
    )
    assert bucket.uploaded[0][0] == document.storage_path
    assert database.added == [document]
    assert database.commits == 1


def test_upload_removes_object_when_database_commit_fails(monkeypatch):
    database = DocumentDb()
    database.commit_error = RuntimeError("database unavailable")
    bucket = FakeBucket()
    storage = FakeStorageClient(bucket)
    current_user = make_user()
    repository = authorized_repository(current_user)
    monkeypatch.setattr(document_service, "tenant_repository", lambda *_args: repository)
    monkeypatch.setattr(
        document_service,
        "get_accessible_client",
        lambda *_args, **_kwargs: object(),
    )

    with pytest.raises(HTTPException) as error:
        asyncio.run(
            document_service.upload_document(
                database,
                current_user,
                storage,
                "documents-test",
                client_id=uuid4(),
                task_id=None,
                category="Geral",
                upload=FakeUpload(),
            )
        )

    assert error.value.status_code == 500
    assert database.rollbacks == 1
    assert bucket.removed == [bucket.uploaded[0][0]]


def test_upload_removes_object_when_database_add_fails(monkeypatch):
    database = DocumentDb()
    database.add_error = RuntimeError("session unavailable")
    bucket = FakeBucket()
    storage = FakeStorageClient(bucket)
    current_user = make_user()
    repository = authorized_repository(current_user)
    monkeypatch.setattr(document_service, "tenant_repository", lambda *_args: repository)
    monkeypatch.setattr(
        document_service,
        "get_accessible_client",
        lambda *_args, **_kwargs: object(),
    )

    with pytest.raises(HTTPException) as error:
        asyncio.run(
            document_service.upload_document(
                database,
                current_user,
                storage,
                "documents-test",
                client_id=uuid4(),
                task_id=None,
                category="Geral",
                upload=FakeUpload(),
            )
        )

    assert error.value.status_code == 500
    assert database.rollbacks == 1
    assert bucket.removed == [bucket.uploaded[0][0]]


def test_upload_rejects_generic_zip_disguised_as_docx(monkeypatch):
    database = DocumentDb()
    bucket = FakeBucket()
    storage = FakeStorageClient(bucket)
    current_user = make_user()
    repository = authorized_repository(current_user)
    monkeypatch.setattr(document_service, "tenant_repository", lambda *_args: repository)
    monkeypatch.setattr(
        document_service,
        "get_accessible_client",
        lambda *_args, **_kwargs: object(),
    )

    with pytest.raises(HTTPException) as error:
        asyncio.run(
            document_service.upload_document(
                database,
                current_user,
                storage,
                "documents-test",
                client_id=uuid4(),
                task_id=None,
                category="Geral",
                upload=FakeUpload(
                    contents=b"PK\x03\x04arquivo-zip-generico",
                    filename="arquivo.docx",
                ),
            )
        )

    assert error.value.status_code == 415
    assert bucket.uploaded == []
    assert database.added == []


def test_delete_keeps_database_record_when_storage_fails(monkeypatch):
    database = DocumentDb()
    bucket = FakeBucket()
    bucket.remove_error = RuntimeError("storage unavailable")
    storage = FakeStorageClient(bucket)
    current_user = make_user("gerente")
    client_id = uuid4()
    document = SimpleNamespace(
        id=uuid4(),
        tenant_id=UUID(current_user["tenant_id"]),
        client_id=client_id,
        storage_path=f"{current_user['tenant_id']}/{client_id}/documento.pdf",
    )
    repository = authorized_repository(current_user, document)
    monkeypatch.setattr(document_service, "tenant_repository", lambda *_args: repository)
    monkeypatch.setattr(
        document_service,
        "get_accessible_client",
        lambda *_args, **_kwargs: object(),
    )

    with pytest.raises(HTTPException) as error:
        document_service.delete_document(
            database,
            current_user,
            storage,
            "documents-test",
            document.id,
        )

    assert error.value.status_code == 503
    assert database.deleted == []
    assert database.commits == 0
    assert database.rollbacks == 1


def test_download_rejects_storage_path_outside_authorized_tenant(monkeypatch):
    database = DocumentDb()
    bucket = FakeBucket()
    storage = FakeStorageClient(bucket)
    current_user = make_user()
    document = SimpleNamespace(
        id=uuid4(),
        tenant_id=UUID(current_user["tenant_id"]),
        client_id=uuid4(),
        storage_path=f"{uuid4()}/{uuid4()}/documento.pdf",
    )
    repository = authorized_repository(current_user, document)
    monkeypatch.setattr(document_service, "tenant_repository", lambda *_args: repository)
    monkeypatch.setattr(
        document_service,
        "get_accessible_client",
        lambda *_args, **_kwargs: object(),
    )

    with pytest.raises(HTTPException) as error:
        document_service.create_download_url(
            database,
            current_user,
            storage,
            "documents-test",
            document.id,
        )

    assert error.value.status_code == 404
    assert storage.requested_buckets == []


def test_download_returns_short_lived_signed_url(monkeypatch):
    database = DocumentDb()
    bucket = FakeBucket()
    storage = FakeStorageClient(bucket)
    current_user = make_user()
    client_id = uuid4()
    document = SimpleNamespace(
        id=uuid4(),
        tenant_id=UUID(current_user["tenant_id"]),
        client_id=client_id,
        storage_path=f"{current_user['tenant_id']}/{client_id}/documento.pdf",
    )
    repository = authorized_repository(current_user, document)
    monkeypatch.setattr(document_service, "tenant_repository", lambda *_args: repository)
    monkeypatch.setattr(
        document_service,
        "get_accessible_client",
        lambda *_args, **_kwargs: object(),
    )

    result = document_service.create_download_url(
        database,
        current_user,
        storage,
        "documents-test",
        document.id,
    )

    assert result == "https://storage.example/documento"
    assert storage.requested_buckets == ["documents-test"]
