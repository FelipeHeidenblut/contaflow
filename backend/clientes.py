import csv
import io
import uuid
from typing import List
from uuid import UUID

import models
import schemas
import re
from access_control import (
    apply_client_scope,
    require_management_access,
    validate_responsible_profile,
)
from database import get_db
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from pydantic import BaseModel, ConfigDict
from plan_config import PLAN_CONFIG
from security import get_active_user, get_current_user
from sqlalchemy.exc import IntegrityError
from sqlalchemy import func
from sqlalchemy.orm import Session

router = APIRouter(prefix="/api/v1/clientes", tags=["Clientes"])
MAX_CSV_SIZE = 2 * 1024 * 1024

# Limites de clientes por plano (Plano: Limite de Clientes)
LIMITES_CLIENTES = {
    plan_id: config["clients"] if config["clients"] is not None else float("inf")
    for plan_id, config in PLAN_CONFIG.items()
}
NOMES_PLANOS = {plan_id: config["name"] for plan_id, config in PLAN_CONFIG.items()}


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
    tenant_id = current_user.get("tenant_id")
    require_management_access(current_user)
    validate_responsible_profile(db, tenant_id, cliente.responsible_profile_id)

    tenant = db.query(models.Tenant).filter(models.Tenant.id == tenant_id).first()
    limite = LIMITES_CLIENTES.get(tenant.plano, 5)  # Padrão é Free se não achar o plano

    # Conta quantos clientes ativos o escritório já tem
    total_clientes = (
        db.query(models.Client)
        .filter(models.Client.tenant_id == tenant_id, models.Client.ativo == True)
        .count()
    )

    if total_clientes >= limite:
        raise HTTPException(
            status_code=403,
            detail=f"Você atingiu o limite de {limite} clientes do plano {NOMES_PLANOS.get(tenant.plano, tenant.plano)}. Faça upgrade para adicionar mais!",
        )

    # LÓGICA DE DUPLICIDADE INTELIGENTE
    if cliente.tipo_pessoa == "PJ" and cliente.cnpj:
        cnpj_existente = (
            db.query(models.Client)
            .filter(
                models.Client.tenant_id == tenant_id,
                func.upper(
                    func.regexp_replace(models.Client.cnpj, "[^A-Za-z0-9]", "", "g")
                )
                == cliente.cnpj,
            )
            .first()
        )
        if cnpj_existente:
            raise HTTPException(
                status_code=400,
                detail="Este CNPJ já está cadastrado no seu escritório.",
            )

    elif cliente.tipo_pessoa == "PF" and cliente.cpf:
        cpf_existente = (
            db.query(models.Client)
            .filter(
                models.Client.tenant_id == tenant_id,
                func.regexp_replace(models.Client.cpf, "[^0-9]", "", "g") == cliente.cpf,
            )
            .first()
        )
        if cpf_existente:
            raise HTTPException(
                status_code=400, detail="Este CPF já está cadastrado no seu escritório."
            )

    # CRIAÇÃO DO CLIENTE COM TODOS OS CAMPOS
    novo_cliente = models.Client(
        tenant_id=tenant_id,
        tipo_pessoa=cliente.tipo_pessoa,  # Novo
        nome=cliente.nome,  # Novo
        cpf=cliente.cpf,  # Novo
        razao_social=cliente.razao_social,
        cnpj=cliente.cnpj,
        regime_tributario=cliente.regime_tributario,
        natureza_operacao=cliente.natureza_operacao,
        email=str(cliente.email) if cliente.email else None,
        responsible_profile_id=cliente.responsible_profile_id,
    )

    db.add(novo_cliente)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="CPF/CNPJ já cadastrado neste escritório.")
    db.refresh(novo_cliente)

    return novo_cliente


@router.get("", response_model=list[schemas.ClientResponse])
def listar_clientes(
    db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)
):
    tenant_id = current_user.get("tenant_id")

    # MUDANÇA AQUI: Filtra apenas clientes onde ativo == True
    query = (
        db.query(models.Client)
        .filter(models.Client.tenant_id == tenant_id, models.Client.ativo == True)
    )
    clientes = apply_client_scope(query, current_user).all()

    return clientes


# ROTA DE DESATIVAÇÃO (Substitui o DELETE)
@router.patch("/{cliente_id}/desativar", response_model=schemas.ClientResponse)
def desativar_cliente(
    cliente_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_active_user),
):
    tenant_id = current_user.get("tenant_id")

    # NOVA REGRA RBAC: Apenas admin pode arquivar
    require_management_access(current_user)

    cliente = (
        db.query(models.Client)
        .filter(models.Client.id == cliente_id, models.Client.tenant_id == tenant_id)
        .first()
    )

    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado.")

    cliente.ativo = False
    db.commit()
    db.refresh(cliente)

    return cliente


@router.patch("/{cliente_id}/responsavel", response_model=schemas.ClientResponse)
def atribuir_responsavel(
    cliente_id: UUID,
    payload: ClientResponsibleUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_active_user),
):
    require_management_access(current_user)
    tenant_id = current_user["tenant_id"]
    cliente = (
        db.query(models.Client)
        .filter(
            models.Client.id == cliente_id,
            models.Client.tenant_id == tenant_id,
        )
        .first()
    )
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado.")
    validate_responsible_profile(db, tenant_id, payload.responsible_profile_id)
    cliente.responsible_profile_id = payload.responsible_profile_id
    db.commit()
    db.refresh(cliente)
    return cliente


@router.post("/importar-csv")
async def importar_clientes_csv(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_active_user)
):
    require_management_access(current_user)
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="O arquivo deve ser .csv")

    # Pega o tenant_id do usuário logado e busca o plano dele
    tenant_id = current_user.get("tenant_id")
    tenant = db.query(models.Tenant).filter(models.Tenant.id == tenant_id).first()
    
    if not tenant:
        raise HTTPException(status_code=404, detail="Escritório não encontrado.")

    # Checa o limite do plano antes de começar a importação
    limite = LIMITES_CLIENTES.get(tenant.plano, 5)
    total_clientes_atuais = db.query(models.Client).filter(
        models.Client.tenant_id == tenant_id, 
        models.Client.ativo == True
    ).count()

    try:
        contents = await file.read(MAX_CSV_SIZE + 1)
        if len(contents) > MAX_CSV_SIZE:
            raise HTTPException(status_code=413, detail="CSV excede o limite máximo de 2MB.")
        try:
            decoded_content = contents.decode("utf-8")
        except UnicodeDecodeError:
            decoded_content = contents.decode("iso-8859-1")

        csv_reader = csv.DictReader(io.StringIO(decoded_content), delimiter=";")

        if not csv_reader.fieldnames or len(csv_reader.fieldnames) < 3:
            csv_reader = csv.DictReader(io.StringIO(decoded_content), delimiter=",")

        clientes_importados = 0
        linhas_com_erro = 0

        for row in csv_reader:
            if not any(row.values()):
                continue

            # BLOQUEIO: Se atingiu o limite, salva os que já passaram e avisa o usuário
            if total_clientes_atuais >= limite:
                db.commit() # Salva os clientes que já foram adicionados antes do limite
                raise HTTPException(
                    status_code=403,
                    detail=f"A importação foi interrompida. Você atingiu o limite de {limite} clientes do plano {NOMES_PLANOS.get(tenant.plano, tenant.plano)}. Foram importados {clientes_importados} clientes antes do bloqueio."
                )

            tipo_pessoa = str(row.get("TIPO (PF/PJ)", "")).strip().upper()
            nome_razao = str(row.get("NOME_OU_RAZAO", "")).strip()
            documento = str(row.get("CPF_OU_CNPJ", "")).strip()
            regime = str(row.get("REGIME_TRIBUTARIO", "Simples Nacional")).strip()

            if not nome_razao or not documento:
                linhas_com_erro += 1
                continue

            # Limpa a pontuação, mas MANTÉM letras e números (para o novo CNPJ alfanumérico)
            documento_limpo = re.sub(r'[^a-zA-Z0-9]', '', documento)
            if tipo_pessoa == "PF" and (not documento_limpo.isdigit() or len(documento_limpo) != 11):
                linhas_com_erro += 1
                continue
            if tipo_pessoa != "PF" and len(documento_limpo) != 14:
                linhas_com_erro += 1
                continue

            duplicado = db.query(models.Client.id).filter(
                models.Client.tenant_id == tenant_id,
                (models.Client.cpf == documento_limpo) if tipo_pessoa == "PF" else (models.Client.cnpj == documento_limpo),
            ).first()
            if duplicado:
                linhas_com_erro += 1
                continue

            # Usa o tenant_id do usuário logado!
            novo_cliente = models.Client(
                tenant_id=tenant_id, 
                tipo_pessoa=tipo_pessoa if tipo_pessoa in ["PF", "PJ"] else "PJ",
                regime_tributario=regime,
                natureza_operacao=str(row.get("NATUREZA_OPERACAO", "Serviços")).strip(),
            )

            if novo_cliente.tipo_pessoa == "PF":
                novo_cliente.nome = nome_razao
                novo_cliente.cpf = documento_limpo
            else:
                novo_cliente.razao_social = nome_razao
                novo_cliente.cnpj = documento_limpo

            db.add(novo_cliente)
            clientes_importados += 1
            total_clientes_atuais += 1 # Atualiza o contador para a checagem do limite

        db.commit()
        return {
            "message": "Importação concluída",
            "importados": clientes_importados,
            "erros": linhas_com_erro,
        }

    except HTTPException:
        # Já fizemos o commit dos válidos acima antes de levantar o erro.
        # Apenas repassamos a exceção para o frontend.
        raise
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="Erro interno ao processar o CSV.")
