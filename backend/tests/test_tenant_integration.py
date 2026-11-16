"""Exercise actual SQL scopes with two offices and all three access roles."""
from datetime import date, datetime, timezone
from uuid import uuid4

import pytest
from fastapi import HTTPException
from sqlalchemy import Column, MetaData, Table, create_engine
from sqlalchemy.orm import Session

import models
from access_control import get_accessible_client, get_accessible_task, validate_responsible_profile
from comentarios import CommentCreate, create_comment, list_comments
from document_service import DocumentListFilters, list_documents
from task_service import TaskListFilters, list_tasks, change_task_status
from enums import TaskStatus


@pytest.fixture
def offices():
    engine = create_engine("sqlite:///:memory:")
    metadata = MetaData()
    for model in (models.Client, models.Task, models.Document, models.Profile, models.Comment):
        Table(model.__tablename__, metadata, *(
            Column(column.name, column.type, primary_key=column.primary_key)
            for column in model.__table__.columns
        ))
    metadata.create_all(engine)
    with Session(engine) as db:
        tenant, other_tenant, user_id, colleague = uuid4(), uuid4(), uuid4(), uuid4()
        clients, tasks = [], []
        for owner, responsible in [(tenant, user_id), (tenant, colleague), (tenant, None), (other_tenant, None)]:
            client = models.Client(id=uuid4(), tenant_id=owner, razao_social="Empresa",
                                   regime_tributario="Simples Nacional", responsible_profile_id=responsible)
            task = models.Task(id=uuid4(), tenant_id=owner, client_id=client.id,
                               title="Entrega", due_date=date.today(), status="pendente")
            db.add_all([client, task, models.Document(
                id=uuid4(), tenant_id=owner, client_id=client.id, nome_arquivo="Arquivo.pdf",
                categoria="Geral", created_at=datetime.now(timezone.utc),
            )])
            clients.append(client)
            tasks.append(task)
        foreign_profile = models.Profile(id=uuid4(), tenant_id=other_tenant, role="admin")
        db.add(foreign_profile)
        db.commit()
        yield db, dict(tenant_id=str(tenant), user_id=str(user_id)), clients, tasks, foreign_profile
    engine.dispose()


@pytest.mark.parametrize("role, visible", [("admin", [0, 1, 2]), ("gerente", [0, 1, 2]), ("colaborador", [0, 2])])
def test_lists_and_direct_access_keep_office_and_portfolio_scope(offices, role, visible):
    db, identity, clients, tasks, foreign_profile = offices
    user = identity | {"role": role}
    listed = list_tasks(db, user, TaskListFilters())
    assert {item.id for item in listed["items"]} == {tasks[i].id for i in visible}
    assert listed["summary"]["total"] == len(visible)
    documents = list_documents(db, user, DocumentListFilters())
    assert {item.client_id for item in documents["items"]} == {clients[i].id for i in visible}
    for index in set(range(4)) - set(visible):
        for get_resource, resource in [(get_accessible_client, clients[index]), (get_accessible_task, tasks[index])]:
            with pytest.raises(HTTPException) as caught:
                get_resource(db, resource.id, user)
            assert caught.value.status_code == 404
        with pytest.raises(HTTPException) as caught:
            change_task_status(db, user, tasks[index].id, TaskStatus.CONCLUIDA)
        assert caught.value.status_code == 404
        with pytest.raises(HTTPException):
            create_comment(CommentCreate(client_id=clients[index].id, content="Não permitido"), db, user)
        with pytest.raises(HTTPException):
            list_comments(clients[index].id, None, db, user)
    with pytest.raises(HTTPException) as caught:
        validate_responsible_profile(db, user, foreign_profile.id)
    assert caught.value.status_code == 404
    assert db.query(models.Comment).count() == 0
