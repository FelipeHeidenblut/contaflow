from datetime import datetime, timedelta, timezone
from uuid import uuid4

import models
import pytest
from document_service import DocumentListFilters, list_document_folders
from schemas import DocumentFolderResponse
from sqlalchemy import Column, MetaData, Table, create_engine
from sqlalchemy.orm import Session


@pytest.fixture
def database():
    engine = create_engine("sqlite:///:memory:")
    metadata = MetaData()
    for model in (models.Client, models.Document):
        Table(model.__tablename__, metadata, *(
            Column(column.name, column.type, primary_key=column.primary_key)
            for column in model.__table__.columns
        ))
    metadata.create_all(engine)
    with Session(engine) as session:
        yield session
    engine.dispose()


def client(database, tenant_id, name, *, active=True, responsible=None):
    value = models.Client(
        id=uuid4(), tenant_id=tenant_id, razao_social=name, ativo=active,
        regime_tributario="Simples Nacional", responsible_profile_id=responsible,
    )
    database.add(value)
    return value


def document(database, owner, *, tenant_id=None, filename="balanco.pdf", category="Contábil", days=0):
    value = models.Document(
        id=uuid4(), tenant_id=tenant_id or owner.tenant_id, client_id=owner.id,
        nome_arquivo=filename, categoria=category, storage_path=f"test/{uuid4()}",
        created_at=datetime(2026, 1, 1, tzinfo=timezone.utc) + timedelta(days=days),
    )
    database.add(value)
    return value


def user(tenant_id, *, role="admin", user_id=None):
    return {"tenant_id": str(tenant_id), "user_id": str(user_id or uuid4()), "role": role}


def test_folders_count_all_documents_and_paginate_clients(database):
    tenant_id = uuid4()
    first = client(database, tenant_id, "A Principal")
    second = client(database, tenant_id, "B Secundário")
    empty = client(database, tenant_id, "C Sem arquivos")
    archived = client(database, tenant_id, "D Arquivado", active=False)
    client(database, tenant_id, "E Arquivado vazio", active=False)
    foreign = client(database, uuid4(), "A Outro escritório")
    for day in range(25):
        document(database, first, days=day)
    document(database, second)
    document(database, archived)
    document(database, foreign)
    database.commit()

    page = list_document_folders(database, user(tenant_id), DocumentListFilters(page_size=2))
    assert page["total"] == 4
    assert page["pages"] == 2
    folders = [DocumentFolderResponse.model_validate(item) for item in page["items"]]
    assert [folder.client_id for folder in folders] == [first.id, second.id]
    assert folders[0].document_count == 25
    assert folders[0].last_uploaded_at.date().isoformat() == "2026-01-25"

    page = list_document_folders(database, user(tenant_id), DocumentListFilters(page=2, page_size=2))
    folders = [DocumentFolderResponse.model_validate(item) for item in page["items"]]
    assert [folder.client_id for folder in folders] == [empty.id, archived.id]
    assert folders[0].document_count == 0
    assert folders[0].last_uploaded_at is None
    assert folders[1].client_active is False


def test_folder_search_and_category_count_only_matching_files(database):
    tenant_id = uuid4()
    target = client(database, tenant_id, "Cliente alvo")
    client(database, tenant_id, "Cliente sem arquivos")
    document(database, target, filename="relatorio_100%_literal.pdf", category="Fiscal")
    document(database, target, filename="relatorio_100XXliteral.pdf", category="Fiscal")
    document(database, target, filename="relatorio_100%_literal.pdf", category="Contábil")
    database.commit()
    result = list_document_folders(database, user(tenant_id), DocumentListFilters(
        search="100%_literal", category="Fiscal", client_id=target.id,
    ))
    assert result["total"] == 1
    folder = DocumentFolderResponse.model_validate(result["items"][0])
    assert folder.client_id == target.id
    assert folder.document_count == 1


def test_folder_access_and_counts_respect_portfolio_and_tenant(database):
    tenant_id, user_id = uuid4(), uuid4()
    own = client(database, tenant_id, "A Próprio", responsible=user_id)
    unassigned = client(database, tenant_id, "B Não atribuído")
    private = client(database, tenant_id, "C Carteira de outro", responsible=uuid4())
    foreign = client(database, uuid4(), "D Outro escritório")
    document(database, own)
    document(database, own, tenant_id=foreign.tenant_id)
    document(database, private)
    document(database, foreign)
    database.commit()
    current_user = user(tenant_id, role="colaborador", user_id=user_id)

    result = list_document_folders(database, current_user, DocumentListFilters())
    assert result["total"] == 2
    folders = [DocumentFolderResponse.model_validate(item) for item in result["items"]]
    assert [folder.client_id for folder in folders] == [own.id, unassigned.id]
    assert folders[0].document_count == 1
    assert folders[1].document_count == 0

    result = list_document_folders(database, current_user, DocumentListFilters(client_id=private.id))
    assert result["total"] == 0
