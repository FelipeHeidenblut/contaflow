from datetime import date, timedelta
from typing import List, Optional
from uuid import UUID

import models
import schemas
from database import get_db
from enums import TaskStatus  # Importando o Enum
from fastapi import APIRouter, Depends, HTTPException, status
from security import get_current_user
from sqlalchemy.orm import Session

router = APIRouter(prefix="/api/v1/obrigacoes", tags=["Obrigações e Prazos"])


# ==========================================
# REGRA DE NEGÓCIO: Prazo no Próximo Dia Útil
# ==========================================
def ajustar_para_dia_util(data_vencimento: date) -> date:
    """
    Realidade Brasileira: Se o prazo cai no sábado ou domingo,
    empurramos para a segunda-feira.
    """
    dia_da_semana = data_vencimento.weekday()  # 0=Seg, 5=Sab, 6=Dom

    if dia_da_semana == 5:  # Sábado -> Segunda
        return data_vencimento + timedelta(days=2)
    elif dia_da_semana == 6:  # Domingo -> Segunda
        return data_vencimento + timedelta(days=1)

    return data_vencimento  # Seg-Sex, mantém a data


@router.get("", response_model=List[schemas.TaskResponse])
def listar_obrigacoes(
    db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)
):
    tenant_id = current_user.get("tenant_id")
    tarefas = db.query(models.Task).filter(models.Task.tenant_id == tenant_id).all()
    return tarefas


@router.post(
    "", response_model=schemas.TaskResponse, status_code=status.HTTP_201_CREATED
)
def criar_obrigacao(
    tarefa_in: schemas.TaskCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    tenant_id = current_user.get("tenant_id")

    cliente_existe = (
        db.query(models.Client)
        .filter(
            models.Client.id == tarefa_in.client_id,
            models.Client.tenant_id == tenant_id,
        )
        .first()
    )

    if not cliente_existe:
        raise HTTPException(
            status_code=404, detail="Cliente não encontrado neste escritório."
        )

    # 🇧🇷 REGRA DE NEGÓCIO: Ajusta a data para o próximo dia útil se cair no fim de semana
    data_ajustada = ajustar_para_dia_util(tarefa_in.due_date)

    nova_tarefa = models.Task(
        tenant_id=tenant_id,
        client_id=tarefa_in.client_id,
        title=tarefa_in.title,
        description=tarefa_in.description,
        due_date=data_ajustada,  # <--- USA A DATA AJUSTADA AQUI!
        status=tarefa_in.status.value
        if isinstance(tarefa_in.status, TaskStatus)
        else tarefa_in.status,
        assigned_to=tarefa_in.assigned_to,
    )

    db.add(nova_tarefa)
    db.commit()
    db.refresh(nova_tarefa)

    return nova_tarefa


@router.patch("/{tarefa_id}/concluir", response_model=schemas.TaskResponse)
def concluir_obrigacao(
    tarefa_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    tenant_id = current_user.get("tenant_id")

    tarefa = (
        db.query(models.Task)
        .filter(models.Task.id == tarefa_id, models.Task.tenant_id == tenant_id)
        .first()
    )

    if not tarefa:
        raise HTTPException(status_code=404, detail="Tarefa não encontrada.")

    # Usando o Enum de forma segura
    tarefa.status = TaskStatus.CONCLUIDA.value
    db.commit()
    db.refresh(tarefa)

    return tarefa


@router.delete("/{tarefa_id}", status_code=status.HTTP_204_NO_CONTENT)
def excluir_obrigacao(
    tarefa_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    tenant_id = current_user.get("tenant_id")

    tarefa = (
        db.query(models.Task)
        .filter(models.Task.id == tarefa_id, models.Task.tenant_id == tenant_id)
        .first()
    )

    if not tarefa:
        raise HTTPException(status_code=404, detail="Tarefa não encontrada.")

    db.delete(tarefa)
    db.commit()

    return None
