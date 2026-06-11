from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date
from pydantic import BaseModel

import models
from database import get_db

router = APIRouter(
    prefix="/api/v1/fiscal-deadlines",
    tags=["Prazos Fiscais"]
)

# Schema de validação de SAÍDA do Pydantic (v2)
class FiscalDeadlineResponse(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    deadline_date: date # O Pydantic v2 formata automatico para "YYYY-MM-DD"
    is_monthly: bool
    reference_link: Optional[str] = None

    class Config:
        from_attributes = True


@router.get("", response_model=List[FiscalDeadlineResponse])
def get_fiscal_deadlines(db: Session = Depends(get_db)):
    """
    Lista todos os prazos federais globais para alimentar o calendário do Dashboard.
    """
    try:
        deadlines = db.query(models.TaxDeadline).all()
        return deadlines
    except Exception as e:
        # Registra o erro no log do servidor
        print(f"[ERROR] Falha ao consultar tax_deadlines: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao buscar prazos fiscais federais."
        )