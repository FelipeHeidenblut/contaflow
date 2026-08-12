import calendar
from datetime import date, timedelta
from typing import List, Optional
from uuid import UUID

import models
import schemas
from database import get_db
from enums import TaskStatus  # Importando o Enum
from fastapi import APIRouter, Depends, HTTPException, status
from security import get_active_user, get_current_user
from sqlalchemy.orm import Session

router = APIRouter(prefix="/api/v1/obrigacoes", tags=["Obrigações e Prazos"])


def validar_relacionamentos(db: Session, tenant_id: str, tarefa: schemas.TaskCreate):
    cliente = db.query(models.Client).filter(
        models.Client.id == tarefa.client_id,
        models.Client.tenant_id == tenant_id,
    ).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado neste escritório.")
    if tarefa.assigned_to:
        membro = db.query(models.Profile).filter(
            models.Profile.id == tarefa.assigned_to,
            models.Profile.tenant_id == tenant_id,
        ).first()
        if not membro:
            raise HTTPException(status_code=404, detail="Responsável não encontrado neste escritório.")


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
    current_user: dict = Depends(get_active_user),
):
    tenant_id = current_user.get("tenant_id")

    validar_relacionamentos(db, tenant_id, tarefa_in)

    # 🇧🇷 REGRA DE NEGÓCIO: Ajusta a data para o próximo dia útil se cair no fim de semana
    data_ajustada = ajustar_para_dia_util(tarefa_in.due_date)

    nova_tarefa = models.Task(
        tenant_id=tenant_id,
        client_id=tarefa_in.client_id,
        title=tarefa_in.title,
        description=tarefa_in.description,
        due_date=data_ajustada,
        status=tarefa_in.status.value
        if isinstance(tarefa_in.status, TaskStatus)
        else tarefa_in.status,
        assigned_to=tarefa_in.assigned_to,
        grau_importancia=tarefa_in.grau_importancia,
        is_recurring=tarefa_in.is_recurring,  # <--- ADICIONADO
        recurrence_day=tarefa_in.recurrence_day,  # <--- ADICIONADO
    )

    db.add(nova_tarefa)
    db.commit()
    db.refresh(nova_tarefa)

    return nova_tarefa


@router.patch("/{tarefa_id}/concluir", response_model=schemas.TaskResponse)
def concluir_obrigacao(
    tarefa_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_active_user),
):
    tenant_id = current_user.get("tenant_id")

    tarefa = (
        db.query(models.Task)
        .filter(models.Task.id == tarefa_id, models.Task.tenant_id == tenant_id)
        .first()
    )

    if not tarefa:
        raise HTTPException(status_code=404, detail="Tarefa não encontrada.")

    # Marca a tarefa atual como concluída
    tarefa.status = TaskStatus.CONCLUIDA.value

    # ==========================================
    # MOTOR DE RECORRÊNCIA AUTOMÁTICA
    # ==========================================
    if tarefa.is_recurring and tarefa.recurrence_day:
        today = date.today()

        # Calcula o mês e ano do próximo vencimento
        if today.month == 12:
            next_month = 1
            next_year = today.year + 1
        else:
            next_month = today.month + 1
            next_year = today.year

        # Descobre o último dia daquele mês (para não dar erro se o dia for 31 e o mês tiver 30 dias)
        last_day_of_month = calendar.monthrange(next_year, next_month)[1]
        day_to_use = min(tarefa.recurrence_day, last_day_of_month)

        # Cria a data do próximo mês
        next_due_date = date(next_year, next_month, day_to_use)

        # Usa sua função existente para empurrar para o próximo dia útil se cair no fim de semana
        next_due_date = ajustar_para_dia_util(next_due_date)

        # Cria a nova tarefa do próximo mês
        nova_tarefa = models.Task(
            tenant_id=tenant_id,
            client_id=tarefa.client_id,
            title=tarefa.title,
            description=tarefa.description,
            due_date=next_due_date,
            status=TaskStatus.PENDENTE.value,
            assigned_to=tarefa.assigned_to,
            grau_importancia=tarefa.grau_importancia,
            is_recurring=True,  # Mantém a recorrência ativa
            recurrence_day=tarefa.recurrence_day,
        )
        db.add(nova_tarefa)
        # ==========================================

    db.commit()
    db.refresh(tarefa)

    return tarefa


@router.delete("/{tarefa_id}", status_code=status.HTTP_204_NO_CONTENT)
def excluir_obrigacao(
    tarefa_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_active_user),
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


@router.put("/{tarefa_id}", response_model=schemas.TaskResponse)
def atualizar_obrigacao(
    tarefa_id: UUID,
    tarefa_update: schemas.TaskCreate,  # Reaproveitamos o schema de validação para garantir a consistência
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_active_user),
):
    tenant_id = current_user.get("tenant_id")

    # 1. Busca a tarefa existente no banco
    tarefa = (
        db.query(models.Task)
        .filter(models.Task.id == tarefa_id, models.Task.tenant_id == tenant_id)
        .first()
    )

    if not tarefa:
        raise HTTPException(status_code=404, detail="Tarefa não encontrada.")

    validar_relacionamentos(db, tenant_id, tarefa_update)

    # 🇧🇷 REGRA DE NEGÓCIO: Se a data foi alterada, ajustamos novamente para o próximo dia útil
    data_ajustada = ajustar_para_dia_util(tarefa_update.due_date)

    # 2. Atualiza os campos dinamicamente
    tarefa.title = tarefa_update.title
    tarefa.description = tarefa_update.description
    tarefa.client_id = tarefa_update.client_id
    tarefa.due_date = data_ajustada
    tarefa.grau_importancia = tarefa_update.grau_importancia

    # Tratamento seguro para o Enum do Status
    tarefa.status = (
        tarefa_update.status.value
        if hasattr(tarefa_update.status, "value")
        else tarefa_update.status
    )

    tarefa.assigned_to = tarefa_update.assigned_to

    # ADICIONE ESTAS DUAS LINHAS:
    tarefa.is_recurring = tarefa_update.is_recurring
    tarefa.recurrence_day = tarefa_update.recurrence_day

    # 3. Salva no Supabase
    db.commit()
    db.refresh(tarefa)

    return tarefa
