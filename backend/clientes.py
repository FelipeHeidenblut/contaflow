from typing import List
import uuid

import models
import schemas
from database import get_db
from security import get_current_user
from sqlalchemy.orm import Session
import csv
import io
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status

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

@router.post("/importar-csv")
async def importar_clientes_csv(
    file: UploadFile = File(...), 
    db: Session = Depends(get_db),
    # current_user = Depends(get_current_user) # Descomente se já tiver o sistema de login
):
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="O arquivo deve ser .csv")

    try:
        contents = await file.read()
        try:
            decoded_content = contents.decode('utf-8')
        except UnicodeDecodeError:
            decoded_content = contents.decode('iso-8859-1')

        csv_reader = csv.DictReader(io.StringIO(decoded_content), delimiter=';')
        
        if not csv_reader.fieldnames or len(csv_reader.fieldnames) < 3:
            csv_reader = csv.DictReader(io.StringIO(decoded_content), delimiter=',')

        clientes_importados = 0
        linhas_com_erro = 0

        primeiro_tenant = db.query(models.Tenant).first() # Ajuste se a sua tabela de tenant tiver outro nome
        tenant_ativo = primeiro_tenant.id if primeiro_tenant else uuid.uuid4() 

        for row in csv_reader:
            if not any(row.values()):
                continue

            tipo_pessoa = str(row.get('TIPO (PF/PJ)', '')).strip().upper()
            nome_razao = str(row.get('NOME_OU_RAZAO', '')).strip()
            documento = str(row.get('CPF_OU_CNPJ', '')).strip()
            regime = str(row.get('REGIME_TRIBUTARIO', 'Simples Nacional')).strip()

            if not nome_razao or not documento:
                linhas_com_erro += 1
                continue

            # Usando models.Client e injetando o tenant_id!
            novo_cliente = models.Client(
                tenant_id=tenant_ativo, # O banco de dados agora vai aceitar!
                tipo_pessoa=tipo_pessoa if tipo_pessoa in ['PF', 'PJ'] else 'PJ',
                regime_tributario=regime
            )

            if novo_cliente.tipo_pessoa == 'PF':
                novo_cliente.nome = nome_razao
                novo_cliente.cpf = documento
            else:
                novo_cliente.razao_social = nome_razao
                novo_cliente.cnpj = documento

            db.add(novo_cliente)
            clientes_importados += 1

        db.commit()
        return {
            "message": "Importação concluída", 
            "importados": clientes_importados, 
            "erros": linhas_com_erro
        }

    except Exception as e:
        db.rollback()
        print(f"[ERRO CSV] {str(e)}") # Vai printar o erro exato no terminal se falhar de novo
        raise HTTPException(status_code=500, detail=f"Erro ao processar arquivo: {str(e)}")