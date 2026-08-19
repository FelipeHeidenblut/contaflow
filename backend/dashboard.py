from datetime import date
from typing import List

import models
import schemas
from access_control import apply_client_scope, apply_task_scope
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
    tenant_id = current_user.get("tenant_id")
    hoje = date.today()

    # Busca o tenant para saber o plano
    tenant = db.query(models.Tenant).filter(models.Tenant.id == tenant_id).first()
    plano = tenant.plano if tenant else "free"
    billing_cycle = tenant.billing_cycle if tenant else "monthly"
    status_pagamento = tenant.status_pagamento if tenant else "ativo"

    client_query = db.query(models.Client).filter(
        models.Client.tenant_id == tenant_id,
        models.Client.ativo.is_(True),
    )
    total_clientes = apply_client_scope(client_query, current_user).count()
    open_query = (
        db.query(models.Task)
        .filter(
            models.Task.tenant_id == tenant_id,
            models.Task.status != TaskStatus.CONCLUIDA.value,
        )
    )
    tarefas_abertas = apply_task_scope(open_query, current_user).count()
    overdue_query = (
        db.query(models.Task)
        .filter(
            models.Task.tenant_id == tenant_id,
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
