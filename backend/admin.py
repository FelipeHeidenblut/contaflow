from typing import List, Optional
from uuid import UUID

import models
from database import get_db
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from security import get_current_user, get_super_admin
from sqlalchemy import func
from sqlalchemy.orm import Session

router = APIRouter(prefix="/api/v1/admin", tags=["Super Admin Backoffice"])


# ==========================================
# SCHEMAS (Pydantic)
# ==========================================
class AdminDashboardStats(BaseModel):
    mrr_estimado: float
    total_escritorios: int
    escritorios_ativos: int
    escritorios_inadimplentes: int
    total_usuarios: int
    total_clientes_finais: int


class TenantListResponse(BaseModel):
    id: UUID
    razao_social: str
    plano: str
    status_pagamento: str
    admin_email: Optional[str] = None


# ==========================================
# ROTA DE ESTATÍSTICAS DO SAAS
# ==========================================
@router.get("/dashboard-stats", response_model=AdminDashboardStats)
def get_saas_metrics(
    db: Session = Depends(get_db),
    admin_user: dict = Depends(get_super_admin),
):
    # 1. Agregações de Tenants (Escritórios)
    total_escritorios = db.query(func.count(models.Tenant.id)).scalar() or 0

    escritorios_ativos = (
        db.query(func.count(models.Tenant.id))
        .filter(models.Tenant.status_pagamento == "ativo")
        .scalar()
        or 0
    )

    escritorios_inadimplentes = (
        db.query(func.count(models.Tenant.id))
        .filter(models.Tenant.status_pagamento == "inadimplente")
        .scalar()
        or 0
    )

    # 2. Agregações de Escala
    total_usuarios = db.query(func.count(models.Profile.id)).scalar() or 0
    total_clientes_finais = db.query(func.count(models.Client.id)).scalar() or 0

    # 3. Cálculo de MRR (Removido o Starter, adicionado o Free como R$ 0)
    planos_ativos = (
        db.query(models.Tenant.plano, func.count(models.Tenant.id))
        .filter(models.Tenant.status_pagamento == "ativo")
        .group_by(models.Tenant.plano)
        .all()
    )

    valores_planos = {
        "free": 0.00,
        "basico": 79.90,
        "profissional": 149.90,
        "business": 449.00,
    }

    mrr_estimado = 0.0
    for plano, quantidade in planos_ativos:
        if plano in valores_planos:
            mrr_estimado += valores_planos[plano] * quantidade

    return {
        "mrr_estimado": mrr_estimado,
        "total_escritorios": total_escritorios,
        "escritorios_ativos": escritorios_ativos,
        "escritorios_inadimplentes": escritorios_inadimplentes,
        "total_usuarios": total_usuarios,
        "total_clientes_finais": total_clientes_finais,
    }


# ==========================================
# GESTÃO DE ESCRITÓRIOS
# ==========================================
@router.get("/tenants", response_model=List[TenantListResponse])
def list_tenants(
    db: Session = Depends(get_db), admin_user: dict = Depends(get_super_admin)
):
    tenants = db.query(models.Tenant).order_by(models.Tenant.created_at.desc()).all()
    result = []
    for t in tenants:
        # Busca o e-mail do admin daquele escritório
        admin_profile = (
            db.query(models.Profile)
            .filter(models.Profile.tenant_id == t.id, models.Profile.role == "admin")
            .first()
        )

        result.append(
            TenantListResponse(
                id=t.id,
                razao_social=t.razao_social,
                plano=t.plano,
                status_pagamento=t.status_pagamento,
                admin_email=admin_profile.email if admin_profile else "N/A",
            )
        )
    return result


@router.patch("/tenants/{tenant_id}/status")
def update_tenant_status(
    tenant_id: UUID,
    novo_status: str,  # "ativo" ou "inadimplente"
    db: Session = Depends(get_db),
    admin_user: dict = Depends(get_super_admin),
):
    tenant = db.query(models.Tenant).filter(models.Tenant.id == tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="Escritório não encontrado.")

    tenant.status_pagamento = novo_status  # type: ignore
    db.commit()
    return {
        "status": "success",
        "message": f"Escritório {tenant.razao_social} atualizado para {novo_status}.",
    }
