from typing import List

import models
import schemas
from database import get_db
from fastapi import APIRouter, Depends, HTTPException, status
from security import get_current_user
from sqlalchemy.orm import Session

router = APIRouter(prefix="/api/v1/clientes", tags=["Clientes"])


@router.post(
    "", response_model=schemas.ClientResponse, status_code=status.HTTP_201_CREATED
)
def criar_cliente(
    cliente: schemas.ClientCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    tenant_id = current_user.get("tenant_id")

    cnpj_existente = (
        db.query(models.Client)
        .filter(
            models.Client.tenant_id == tenant_id, models.Client.cnpj == cliente.cnpj
        )
        .first()
    )

    if cnpj_existente:
        raise HTTPException(
            status_code=400, detail="Este CNPJ já está cadastrado no seu escritório."
        )

    novo_cliente = models.Client(
        tenant_id=tenant_id,
        razao_social=cliente.razao_social,
        cnpj=cliente.cnpj,
        regime_tributario=cliente.regime_tributario,
    )

    db.add(novo_cliente)
    db.commit()
    db.refresh(novo_cliente)

    return novo_cliente


@router.get("", response_model=list[schemas.ClientResponse])
def listar_clientes(
    db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)
):
    tenant_id = current_user.get("tenant_id")

    # MUDANÇA AQUI: Filtra apenas clientes onde ativo == True
    clientes = (
        db.query(models.Client)
        .filter(models.Client.tenant_id == tenant_id, models.Client.ativo == True)
        .all()
    )

    return clientes


# ROTA DE DESATIVAÇÃO (Substitui o DELETE)
@router.patch("/{cliente_id}/desativar", response_model=schemas.ClientResponse)
def desativar_cliente(
    cliente_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    tenant_id = current_user.get("tenant_id")

    cliente = (
        db.query(models.Client)
        .filter(models.Client.id == cliente_id, models.Client.tenant_id == tenant_id)
        .first()
    )

    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado.")

    # Soft Delete: Apenas marca como inativo
    cliente.ativo = False
    db.commit()
    db.refresh(cliente)

    return cliente
