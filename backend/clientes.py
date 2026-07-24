import csv
import io
import uuid
from typing import List
from uuid import UUID

import models
import schemas
import re
from database import get_db
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from security import get_current_user
from sqlalchemy.orm import Session

router = APIRouter(prefix="/api/v1/clientes", tags=["Clientes"])

# Limites de clientes por plano (Plano: Limite de Clientes)
LIMITES_CLIENTES = {
    "free": 5,
    "basico": 40,
    "profissional": 100,
    "business": float("inf"),  # Infinito
}


@router.post(
    "", response_model=schemas.ClientResponse, status_code=status.HTTP_201_CREATED
)
def criar_cliente(
    cliente: schemas.ClientCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    tenant_id = current_user.get("tenant_id")

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
            detail=f"Você atingiu o limite de {limite} clientes do plano {tenant.plano.capitalize()}. Faça upgrade para adicionar mais!",
        )

    # LÓGICA DE DUPLICIDADE INTELIGENTE
    if cliente.tipo_pessoa == "PJ" and cliente.cnpj:
        cnpj_existente = (
            db.query(models.Client)
            .filter(
                models.Client.tenant_id == tenant_id, models.Client.cnpj == cliente.cnpj
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
                models.Client.tenant_id == tenant_id, models.Client.cpf == cliente.cpf
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

    # NOVA REGRA RBAC: Apenas admin pode arquivar
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas administradores podem arquivar clientes.",
        )

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


@router.post("/importar-csv")
async def importar_clientes_csv(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user) # Autenticação reativada!
):
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
        contents = await file.read()
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
                    detail=f"A importação foi interrompida. Você atingiu o limite de {limite} clientes do plano {tenant.plano.capitalize()}. Foram importados {clientes_importados} clientes antes do bloqueio."
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
    except Exception as e:
        db.rollback()
        print(f"[ERRO CSV] {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Erro ao processar arquivo: {str(e)}"
        )
