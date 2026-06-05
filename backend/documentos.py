import os
import tempfile
import uuid
from typing import Optional
from uuid import UUID

import models
import schemas
from database import get_db
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from fastapi.responses import RedirectResponse
from security import get_current_user
from sqlalchemy.orm import Session

# Configurações do Supabase Storage
from supabase import Client, create_client

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")
BUCKET_NAME = "documentos-contaflow"

# Inicializa o cliente admin do Supabase
supabase_admin: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

router = APIRouter(prefix="/api/v1/documentos", tags=["Documentos e Repositório"])

MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB


@router.get("", response_model=list[schemas.DocumentResponse])
def listar_documentos(
    db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)
):
    tenant_id = current_user.get("tenant_id")
    documentos = (
        db.query(models.Document).filter(models.Document.tenant_id == tenant_id).all()
    )
    return documentos


@router.post(
    "", response_model=schemas.DocumentResponse, status_code=status.HTTP_201_CREATED
)
async def registrar_documento(
    client_id: UUID = Form(...),
    task_id: Optional[UUID] = Form(None),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    tenant_id = current_user.get("tenant_id")
    user_id = current_user.get("user_id")

    # 1. Validação de Segurança (Tenant)
    cliente = (
        db.query(models.Client)
        .filter(models.Client.id == client_id, models.Client.tenant_id == tenant_id)
        .first()
    )

    if not cliente:
        raise HTTPException(
            status_code=404, detail="Cliente não encontrado neste escritório."
        )

    # 2. Gerar nome seguro e caminho no Storage
    extensao = os.path.splitext(file.filename)[1]
    nome_seguro = f"{uuid.uuid4()}{extensao}"
    storage_path = f"{tenant_id}/{client_id}/{nome_seguro}"

    # 3. Upload para o Supabase Storage via Arquivo Temporário
    tmp_file_path = None  # Inicializa a variável para o bloco finally

    try:
        # Cria um arquivo temporário no disco
        with tempfile.NamedTemporaryFile(delete=False, suffix=extensao) as tmp_file:
            # Lê o arquivo que veio do Vue e escreve no arquivo temporário
            contents = await file.read()

            # Validação de tamanho
            if len(contents) > MAX_FILE_SIZE:
                raise HTTPException(
                    status_code=413, detail="Arquivo excede o limite máximo de 5MB."
                )

            tmp_file.write(contents)
            tmp_file_path = (
                tmp_file.name
            )  # Pega o caminho absoluto do arquivo temporário

        # O arquivo temporário já foi fechado pelo bloco 'with' acima.
        # Agora abrimos ele em modo de leitura binária ("rb") para o Supabase ler
        with open(tmp_file_path, "rb") as f:
            # 1º argumento: Caminho no bucket (destino)
            # 2º argumento: Objeto de arquivo aberto (origem)
            supabase_admin.storage.from_(BUCKET_NAME).upload(
                storage_path, f, file_options={"content-type": file.content_type}
            )

    except HTTPException:
        raise  # Repassa o erro de tamanho (413)
    except Exception as e:
        print(f"Erro ao subir para o Supabase Storage: {e}")
        raise HTTPException(
            status_code=500, detail="Erro ao salvar o arquivo na nuvem."
        )
    finally:
        # Segurança vital: Apaga o arquivo temporário do disco do servidor
        if tmp_file_path and os.path.exists(tmp_file_path):
            os.remove(tmp_file_path)

    # 4. Salva os dados no banco PostgreSQL local (Apenas 1 vez!)
    novo_doc = models.Document(
        tenant_id=tenant_id,
        client_id=client_id,
        task_id=task_id if task_id else None,
        nome_arquivo=file.filename,
        storage_path=storage_path,
        uploaded_by=user_id,
    )

    db.add(novo_doc)
    db.commit()
    db.refresh(novo_doc)

    return novo_doc


# ROTA 3: DOWNLOAD DE DOCUMENTO (AGORA VIA LINK ASSINADO DO SUPABASE)
@router.get("/{doc_id}/download")
def baixar_documento(
    doc_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    tenant_id = current_user.get("tenant_id")

    doc = (
        db.query(models.Document)
        .filter(models.Document.id == doc_id, models.Document.tenant_id == tenant_id)
        .first()
    )

    if not doc:
        raise HTTPException(
            status_code=404, detail="Registro do documento não encontrado."
        )

    # Gera uma URL assinada (válida por 1 hora) para o usuário baixar o arquivo
    try:
        signed_url = supabase_admin.storage.from_(BUCKET_NAME).create_signed_url(
            doc.storage_path,
            expires_in=3600,  # 3600 segundos = 1 hora
        )
        # O supabase-py retorna um dicionário, pegamos apenas a URL
        download_url = signed_url.get("signedURL") or signed_url.get("signedUrl")

        if not download_url:
            raise Exception("URL vazia")

    except Exception as e:
        print(f"Erro ao gerar URL assinada: {e}")
        raise HTTPException(status_code=500, detail="Erro ao gerar link de download.")

    # Redireciona o navegador do usuário direto para o link seguro do Supabase
    return RedirectResponse(url=download_url)


# ROTA 4: EXCLUIR DOCUMENTO
@router.delete("/{doc_id}", status_code=status.HTTP_204_NO_CONTENT)
def excluir_documento(
    doc_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    tenant_id = current_user.get("tenant_id")

    doc = (
        db.query(models.Document)
        .filter(models.Document.id == doc_id, models.Document.tenant_id == tenant_id)
        .first()
    )

    if not doc:
        raise HTTPException(status_code=404, detail="Documento não encontrado.")

    # Apaga o arquivo do Supabase Storage
    try:
        supabase_admin.storage.from_(BUCKET_NAME).remove([doc.storage_path])
    except Exception as e:
        print(f"Aviso: Não foi possível deletar o arquivo do Supabase Storage: {e}")

    # Apaga o registro do banco de dados local
    db.delete(doc)
    db.commit()

    return None
