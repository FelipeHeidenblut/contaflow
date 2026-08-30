import re
from uuid import UUID

from auth_service import RegistrationCommand, synchronize_registration
from database import get_db
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, ConfigDict, Field, field_validator
from security import get_current_user, verify_token
from sqlalchemy.orm import Session

router = APIRouter(prefix="/api/v1/auth", tags=["Autenticação e Sincronização"])


# Schema Refatorado: Incluída validação rigorosa de Documento (Shift-Left)
class SincronizarCadastroSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")
    nome_completo: str = Field(..., min_length=2, max_length=150)
    nome_escritorio: str = Field(..., min_length=2, max_length=150)
    documento: str = Field(..., description="CPF ou CNPJ contendo apenas números")

    @field_validator("documento")
    @classmethod
    def validar_documento(cls, v):
        # Limpa qualquer formatação residual que possa ter escapado do front-end
        v = re.sub(r"\D", "", v)

        if len(v) not in [11, 14]:
            raise ValueError(
                "Documento deve ser um CPF (11 dígitos) ou CNPJ (14 dígitos) válido."
            )
        return v


@router.post("/sincronizar-cadastro", status_code=status.HTTP_201_CREATED)
def sincronizar_cadastro(
    payload: SincronizarCadastroSchema,
    token_payload: dict = Depends(verify_token),
    db: Session = Depends(get_db),
):
    user_id = UUID(token_payload["sub"])
    email = token_payload.get("email")
    if not email:
        raise HTTPException(status_code=401, detail="Token sem e-mail.")
    return synchronize_registration(
        db,
        RegistrationCommand(
            user_id=user_id,
            email=email,
            full_name=payload.nome_completo,
            office_name=payload.nome_escritorio,
            document=payload.documento,
        ),
    )


@router.get("/me", tags=["Autenticação e Sincronização"])
def get_me(current_user: dict = Depends(get_current_user)):
    """Retorna os dados de permissão do usuário logado."""
    return {
        "user_id": current_user.get("user_id"),
        "role": current_user.get("role"),
        "is_superadmin": current_user.get("is_superadmin"),
        "tenant_id": current_user.get("tenant_id"),
        "plan": current_user["plan"],
        "billing_cycle": current_user["billing_cycle"],
        "payment_status": current_user["payment_status"],
    }
