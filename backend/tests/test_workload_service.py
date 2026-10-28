from datetime import datetime, timedelta
from types import SimpleNamespace
from uuid import uuid4
from zoneinfo import ZoneInfo

import models
import pytest
from sqlalchemy import Column, MetaData, Table, create_engine
from sqlalchemy.orm import Session
from workload_service import attach_task_counts


@pytest.fixture
def database():
    engine = create_engine("sqlite:///:memory:")
    metadata = MetaData()
    # Isolate aggregate behavior from PostgreSQL-only recurrence constraints.
    for model in (models.Client, models.Task, models.Profile):
        Table(model.__tablename__, metadata, *(
            Column(column.name, column.type, primary_key=column.primary_key)
            for column in model.__table__.columns
        ))
    metadata.create_all(engine)
    with Session(engine) as session:
        yield session
    engine.dispose()


def add_task(database, tenant_id, client_id, assigned_to, *, days=-1, status="pendente"):
    task = models.Task(
        id=uuid4(), tenant_id=tenant_id, client_id=client_id, assigned_to=assigned_to,
        title="Entrega mensal", status=status,
        due_date=datetime.now(ZoneInfo("America/Sao_Paulo")).date() + timedelta(days=days),
    )
    database.add(task)
    return task


@pytest.mark.parametrize("group_by", ["client_id", "assigned_to"])
def test_counts_include_all_visible_open_tasks_but_no_other_tenant(database, group_by):
    tenant_id = uuid4()
    client_id, member_id = uuid4(), uuid4()
    target_ids = [uuid4() for _ in range(3)]
    user = {"role": "admin", "tenant_id": str(tenant_id), "user_id": str(uuid4())}

    def add(target, **options):
        values = {"client_id": client_id, "assigned_to": member_id, group_by: target}
        add_task(database, options.pop("tenant_id", tenant_id), **values, **options)

    add(target_ids[0])
    add(target_ids[0], days=0, status="em_andamento")
    add(target_ids[0], days=1, status="aguardando_cliente")
    add(target_ids[0], status="concluida")
    add(target_ids[0], tenant_id=uuid4())
    add(target_ids[1], status="aguardando_cliente")
    add(uuid4())  # A resource outside the displayed page.
    database.commit()
    items = [SimpleNamespace(id=identifier) for identifier in target_ids]

    attach_task_counts(database, user, items, group_by=group_by)

    assert [(item.open_tasks_count, item.overdue_tasks_count) for item in items] == [
        (3, 1), (1, 1), (0, 0),
    ]


def test_collaborator_counts_do_not_reveal_another_portfolio(database):
    tenant_id, user_id, member_id = uuid4(), uuid4(), uuid4()
    visible_id, private_id = uuid4(), uuid4()
    database.add_all([
        models.Client(id=visible_id, tenant_id=tenant_id, responsible_profile_id=user_id),
        models.Client(id=private_id, tenant_id=tenant_id, responsible_profile_id=uuid4()),
    ])
    add_task(database, tenant_id, visible_id, member_id)
    add_task(database, tenant_id, private_id, member_id)
    database.commit()
    user = {"role": "colaborador", "tenant_id": str(tenant_id), "user_id": str(user_id)}
    member = SimpleNamespace(id=member_id)

    attach_task_counts(database, user, [member], group_by="assigned_to")

    assert member.open_tasks_count == 1
    assert member.overdue_tasks_count == 1


def test_empty_page_does_not_query_task_counts():
    attach_task_counts(object(), {}, [], group_by="client_id")


def test_client_and_member_pages_serialize_the_requested_counts(database):
    from client_service import ClientListFilters, list_clients
    from membros import ProfileResponse, listar_membros
    from schemas import ClientResponse

    tenant_id, member_id, client_id = uuid4(), uuid4(), uuid4()
    user = {"role": "admin", "tenant_id": str(tenant_id), "user_id": str(member_id)}
    database.add_all([
        models.Client(
            id=client_id, tenant_id=tenant_id, tipo_pessoa="PJ",
            razao_social="Escritório Exemplo", regime_tributario="Simples Nacional",
            natureza_operacao="Serviços", ativo=True,
        ),
        models.Profile(
            id=member_id, tenant_id=tenant_id, name="Ana Silva",
            email="ana@example.com", role="admin",
        ),
    ])
    add_task(database, tenant_id, client_id, member_id)
    database.commit()

    clients = list_clients(database, user, ClientListFilters(include_workload=True))
    client = ClientResponse.model_validate(clients["items"][0])
    assert (client.open_tasks_count, client.overdue_tasks_count) == (1, 1)

    members = listar_membros(
        search=None, role=None, include_workload=True, page=1, page_size=20,
        db=database, current_user=user,
    )
    member = ProfileResponse.model_validate(members["items"][0])
    assert (member.open_tasks_count, member.overdue_tasks_count) == (1, 1)
