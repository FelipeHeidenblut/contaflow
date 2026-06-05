from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import date
from typing import List

from database import get_db
from security import get_current_user
import models
import schemas
from enums import TaskStatus # Importando o Enum

router = APIRouter(
    prefix="/api/v1/dashboard",
    tags=["Dashboard e Resumo"]
)

@router.get("/", response_model=schemas.DashboardResponse)
def obter_resumo_dashboard(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    tenant_id = current_user.get("tenant_id")
    hoje = date.today()
    
    total_clientes = db.query(models.Client).filter(
        models.Client.tenant_id == tenant_id
    ).count()
    
    # Agora usa o valor do Enum ("concluida") ao invés de string solta
    tarefas_abertas = db.query(models.Task).filter(
        models.Task.tenant_id == tenant_id,
        models.Task.status != TaskStatus.CONCLUIDA.value
    ).count()
    
    tarefas_atrasadas = db.query(models.Task).filter(
        models.Task.tenant_id == tenant_id,
        models.Task.status != TaskStatus.CONCLUIDA.value,
        models.Task.due_date < hoje
    ).count()
    
    return {
        "total_clientes": total_clientes,
        "tarefas_abertas": tarefas_abertas,
        "tarefas_atrasadas": tarefas_atrasadas
    }