from uuid import uuid4
from types import SimpleNamespace

import pytest
from fastapi import HTTPException
import models
from obrigacoes import obter_obrigacao
from test_access_control import InMemoryTenantDb, make_user


def test_direct_task_link_requires_same_office():
    office = uuid4()
    task = SimpleNamespace(id=uuid4(), tenant_id=office)
    db = InMemoryTenantDb({models.Task: [task]})
    assert obter_obrigacao(task.id, db, make_user('admin', office)) == task
    with pytest.raises(HTTPException) as error:
        obter_obrigacao(task.id, db, make_user('admin', uuid4()))
    assert error.value.status_code == 404


def test_direct_task_link_respects_collaborator_portfolio():
    user = make_user('colaborador')
    task = SimpleNamespace(id=uuid4(), tenant_id=user['tenant_id'])
    class Query:
        def __init__(self): self.scoped = False
        def filter(self, condition):
            # The portfolio predicate must include assigned and unassigned clients.
            if getattr(condition, 'clauses', None) is not None:
                assert 'responsible_profile_id' in str(condition)
                assert 'IS NULL' in str(condition)
                self.scoped = True
            return self
        def join(self, *_): return self
        def first(self):
            assert self.scoped
            return None
    class Db:
        def query(self, *_): return Query()
    with pytest.raises(HTTPException) as error:
        obter_obrigacao(task.id, Db(), user)
    assert error.value.status_code == 404
