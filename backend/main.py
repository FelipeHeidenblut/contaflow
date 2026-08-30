import uuid
from datetime import datetime, timedelta, timezone
from typing import List
from uuid import UUID

import admin
import alertas
import asaas
import auth
import clientes
import comentarios
import dashboard
import documentos
import fiscal_deadlines
import membros
import models
import obrigacoes
import relatorios
import schemas
import calendario
import contact
from app_config import get_settings
from database import get_db
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
import jwt
from security import get_current_user
from sqlalchemy import text
from sqlalchemy.orm import Session

settings = get_settings()

app = FastAPI(
    title="ContaFlow API",
    docs_url=None if settings.is_production else "/docs",
    redoc_url=None if settings.is_production else "/redoc",
    openapi_url=None if settings.is_production else "/openapi.json",
)

# ==========================================
# CONFIGURAÇÃO DE SEGURANÇA DO CORS
# ==========================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=list(settings.cors_allowed_origins),
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)

# Registrando os routers
app.include_router(clientes.router)
app.include_router(comentarios.router)
app.include_router(obrigacoes.router)
app.include_router(documentos.router)
app.include_router(dashboard.router)
app.include_router(auth.router)
app.include_router(fiscal_deadlines.router)
app.include_router(membros.router)
app.include_router(asaas.router)
app.include_router(admin.router)
app.include_router(calendario.router)
app.include_router(contact.router)
app.include_router(relatorios.router)
app.include_router(alertas.router)


@app.get("/")
def read_root():
    return {
        "status": "A API do ContaFlow está no ar! 🚀",
        "environment": settings.environment,
    }


@app.get("/db-check")
def test_db_connection(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        return {"status": "Conexão com o Supabase realizada com sucesso! 🟢"}
    except Exception:
        raise HTTPException(status_code=503, detail="Banco de dados indisponível.")


# ==========================================
# ROTA DE DEV (BLINDADA PARA PRODUÇÃO)
# ==========================================


@app.post("/dev/login")
def dev_fake_login(db: Session = Depends(get_db)):
    # 🛡️ SEGURANÇA: disponível exclusivamente no ambiente de desenvolvimento.
    # Isso impede que hackers usem essa rota para gerar tokens quando o sistema estiver na nuvem.
    if not settings.is_development:
        raise HTTPException(status_code=404, detail="Not Found")

    dev_tenant = (
        db.query(models.Tenant).filter(models.Tenant.cnpj == "00000000000000").first()
    )

    if not dev_tenant:
        dev_tenant = models.Tenant(
            razao_social="Escritório ContaFlow Dev", cnpj="00000000000000"
        )
        db.add(dev_tenant)
        db.commit()
        db.refresh(dev_tenant)

    payload = {
        "sub": str(uuid.uuid4()),
        "email": "dev@contaflow.com",
        "user_metadata": {"tenant_id": str(dev_tenant.id)},
        "exp": datetime.now(timezone.utc) + timedelta(days=1),
    }

    SECRET = settings.supabase_jwt_secret
    if not SECRET:
        raise HTTPException(status_code=503, detail="Login de desenvolvimento não configurado.")
    token = jwt.encode(payload, SECRET, algorithm="HS256")

    return {
        "access_token": token,
        "token_type": "bearer",
        "tenant_id": dev_tenant.id,
        "aviso": "Copie apenas o texto do access_token!",
    }
