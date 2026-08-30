from uuid import UUID

import schemas
from access_control import Permission, require_permission
from client_service import (
    ClientListFilters,
    assign_responsible,
    create_client,
    deactivate_client,
    import_clients_from_csv,
    list_clients,
)
from database import get_db
from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from pagination import PaginatedResponse
from pydantic import BaseModel, ConfigDict
from security import get_active_user, get_current_user
from sqlalchemy.orm import Session

router = APIRouter(prefix="/api/v1/clientes", tags=["Clientes"])
MAX_CSV_SIZE = 2 * 1024 * 1024


class ClientResponsibleUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    responsible_profile_id: UUID | None = None


@router.post(
    "", response_model=schemas.ClientResponse, status_code=status.HTTP_201_CREATED
)
def criar_cliente(
    cliente: schemas.ClientCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_active_user),
):
    return create_client(db, current_user, cliente)


@router.get("", response_model=PaginatedResponse[schemas.ClientResponse])
def listar_clientes(
    search: str | None = Query(None, max_length=120),
    natureza: str | None = Query(None, max_length=80),
    responsible_profile_id: UUID | None = Query(None),
    unassigned: bool = Query(False),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    return list_clients(
        db,
        current_user,
        ClientListFilters(
            search=search,
            natureza=natureza,
            responsible_profile_id=responsible_profile_id,
            unassigned=unassigned,
            page=page,
            page_size=page_size,
        ),
    )


# ROTA DE DESATIVAÇÃO (Substitui o DELETE)
@router.patch("/{cliente_id}/desativar", response_model=schemas.ClientResponse)
def desativar_cliente(
    cliente_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_active_user),
):
    return deactivate_client(db, current_user, cliente_id)


@router.patch("/{cliente_id}/responsavel", response_model=schemas.ClientResponse)
def atribuir_responsavel(
    cliente_id: UUID,
    payload: ClientResponsibleUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_active_user),
):
    return assign_responsible(
        db,
        current_user,
        cliente_id,
        payload.responsible_profile_id,
    )


@router.post("/importar-csv")
async def importar_clientes_csv(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_active_user),
):
    require_permission(current_user, Permission.CLIENT_MANAGE)
    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="O arquivo deve ser .csv")
    contents = await file.read(MAX_CSV_SIZE + 1)
    if len(contents) > MAX_CSV_SIZE:
        raise HTTPException(status_code=413, detail="CSV excede o limite máximo de 2MB.")
    return import_clients_from_csv(db, current_user, contents)
