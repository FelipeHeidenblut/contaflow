import os
import uuid
from datetime import datetime, timedelta, timezone
from typing import List

import auth
import clientes
import dashboard
import fiscal_deadlines
import documentos
import models
import obrigacoes
import schemas
from database import get_db
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from jose import jwt
from security import get_current_user
from sqlalchemy import text
from sqlalchemy.orm import Session

app = FastAPI(title="ContaFlow API")

# ==========================================
# CONFIGURAÇÃO DE SEGURANÇA DO CORS
# ==========================================
# Pega a URL do frontend do .env. Se não achar, usa o localhost como padrão.
frontend_url = os.getenv("FRONTEND_URL", "http://localhost:5173")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[frontend_url],  # <-- ALTERAÇÃO AQUI: Dinâmico!
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registrando os routers
app.include_router(clientes.router)
app.include_router(obrigacoes.router)
app.include_router(documentos.router)
app.include_router(dashboard.router)
app.include_router(auth.router)
app.include_router(fiscal_deadlines.router)


@app.get("/")
def read_root():
    return {"status": "A API do ContaFlow está no ar! 🚀"}


@app.get("/db-check")
def test_db_connection(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        return {"status": "Conexão com o Supabase realizada com sucesso! 🟢"}
    except Exception as e:
        return {"error": f"Falha na conexão: {str(e)}"}


# ==========================================
# ROTA DE DEV (BLINDADA PARA PRODUÇÃO)
# ==========================================


@app.post("/dev/login")
def dev_fake_login(db: Session = Depends(get_db)):
    # 🛡️ SEGURANÇA: Se a variável ENVIRONMENT não for "development", bloqueia o acesso!
    # Isso impede que hackers usem essa rota para gerar tokens quando o sistema estiver na nuvem.
    if os.getenv("ENVIRONMENT") != "development":
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

    SECRET = os.getenv("SUPABASE_JWT_SECRET")
    token = jwt.encode(payload, SECRET, algorithm="HS256")

    return {
        "access_token": token,
        "token_type": "bearer",
        "tenant_id": dev_tenant.id,
        "aviso": "Copie apenas o texto do access_token!",
    }
    
@app.get("/api/v1/fiscal-deadlines")
def get_fiscal_deadlines(db: Session = Depends(get_db)):
    # Busca todos os prazos fiscais (TaxDeadline) do banco
    deadlines = db.query(models.fiscal_deadlines).all()
    
    # Formata a resposta para o Vue entender
    resultados = []
    for d in deadlines:
        resultados.append({
            "id": d.id,
            "title": d.title,
            "description": d.description,
            # Garante que a data vá como string "YYYY-MM-DD"
            "deadline_date": d.deadline_date.isoformat() if d.deadline_date else None,
            "is_monthly": d.is_monthly,
            "reference_link": d.reference_link
        })
        
    return resultados
