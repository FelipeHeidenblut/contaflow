from datetime import date
from typing import List

import models
import schemas
from access_control import (
    Permission,
    apply_client_scope,
    apply_task_scope,
    require_permission,
    tenant_repository,
)
from database import get_db
from enums import TaskStatus  # Importando o Enum
from fastapi import APIRouter, Depends
from security import get_current_user
from sqlalchemy.orm import Session

router = APIRouter(prefix="/api/v1/dashboard", tags=["Dashboard e Resumo"])


@router.get("/", response_model=schemas.DashboardResponse)
def obter_resumo_dashboard(
    db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)
):
    require_permission(current_user, Permission.TASK_READ)
    require_permission(current_user, Permission.CLIENT_READ)
    repository = tenant_repository(db, current_user)
    hoje = date.today()

    plano = current_user["plan"]
    billing_cycle = current_user["billing_cycle"]
    status_pagamento = current_user["payment_status"]

    client_query = repository.query(models.Client).filter(
        models.Client.ativo.is_(True),
    )
    total_clientes = apply_client_scope(client_query, current_user).count()
    open_query = (
        repository.query(models.Task)
        .filter(
            models.Task.status != TaskStatus.CONCLUIDA.value,
        )
    )
    tarefas_abertas = apply_task_scope(open_query, current_user).count()
    overdue_query = (
        repository.query(models.Task)
        .filter(
            models.Task.status != TaskStatus.CONCLUIDA.value,
            models.Task.due_date < hoje,
        )
    )
    tarefas_atrasadas = apply_task_scope(overdue_query, current_user).count()

    return {
        "total_clientes": total_clientes,
        "tarefas_abertas": tarefas_abertas,
        "tarefas_atrasadas": tarefas_atrasadas,
        "plano": plano,
        "billing_cycle": billing_cycle,
        "status_pagamento": status_pagamento,
    }
