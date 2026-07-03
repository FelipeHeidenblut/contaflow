import models
from database import get_db
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from security import get_current_user, get_super_admin  # Importando do security.py
from sqlalchemy import func
from sqlalchemy.orm import Session

router = APIRouter(prefix="/api/v1/admin", tags=["Super Admin Backoffice"])


# ==========================================
# SCHEMA (Pydantic)
# ==========================================
class AdminDashboardStats(BaseModel):
    mrr_estimado: float
    total_escritorios: int
    escritorios_ativos: int
    escritorios_inadimplentes: int
    total_usuarios: int
    total_clientes_finais: int


# ==========================================
# ROTA DE ESTATÍSTICAS DO SAAS
# ==========================================
@router.get("/dashboard-stats", response_model=AdminDashboardStats)
def get_saas_metrics(
    db: Session = Depends(get_db),
    admin_user: dict = Depends(get_super_admin),  # Usando a dependência correta
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

    # 3. Cálculo de MRR
    planos_ativos = (
        db.query(models.Tenant.plano, func.count(models.Tenant.id))
        .filter(models.Tenant.status_pagamento == "ativo")
        .group_by(models.Tenant.plano)
        .all()
    )

    valores_planos = {
        "starter": 79.00,
        "basico": 149.00,
        "profissional": 197.00,
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
