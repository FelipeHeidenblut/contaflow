from uuid import UUID

import schemas
from database import get_db
from enums import TaskStatus  # Importando o Enum
from fastapi import APIRouter, Depends, Header, HTTPException, Query, status
from pagination import PaginatedResponse
from recurrence import (
    run_recurrence_reconciliation,
    verify_recurrence_cron_secret,
)
from security import get_active_user, get_current_user
from sqlalchemy.orm import Session
from task_service import (
    TaskListFilters,
    complete_task,
    create_task,
    delete_task,
    list_tasks,
    update_task,
)

router = APIRouter(prefix="/api/v1/obrigacoes", tags=["Obrigações e Prazos"])


@router.get("", response_model=PaginatedResponse[schemas.TaskResponse])
def listar_obrigacoes(
    search: str | None = Query(None, max_length=120),
    client_id: UUID | None = Query(None),
    assigned_to: UUID | None = Query(None),
    task_status: TaskStatus | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    return list_tasks(
        db,
        current_user,
        TaskListFilters(
            search=search,
            client_id=client_id,
            assigned_to=assigned_to,
            task_status=task_status,
            page=page,
            page_size=page_size,
        ),
    )


@router.post(
    "", response_model=schemas.TaskResponse, status_code=status.HTTP_201_CREATED
)
def criar_obrigacao(
    tarefa_in: schemas.TaskCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_active_user),
):
    return create_task(db, current_user, tarefa_in)


@router.post("/recorrencias/processar")
def processar_recorrencias(
    x_cron_secret: str | None = Header(default=None, alias="X-Cron-Secret"),
    db: Session = Depends(get_db),
):
    verify_recurrence_cron_secret(x_cron_secret)
    try:
        return run_recurrence_reconciliation(db)
    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Não foi possível processar as recorrências.",
        ) from error


@router.patch("/{tarefa_id}/concluir", response_model=schemas.TaskResponse)
def concluir_obrigacao(
    tarefa_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_active_user),
):
    return complete_task(db, current_user, tarefa_id)


@router.delete("/{tarefa_id}", status_code=status.HTTP_204_NO_CONTENT)
def excluir_obrigacao(
    tarefa_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_active_user),
):
    return delete_task(db, current_user, tarefa_id)


@router.put("/{tarefa_id}", response_model=schemas.TaskResponse)
def atualizar_obrigacao(
    tarefa_id: UUID,
    tarefa_update: schemas.TaskCreate,  # Reaproveitamos o schema de validação para garantir a consistência
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_active_user),
):
    return update_task(db, current_user, tarefa_id, tarefa_update)
