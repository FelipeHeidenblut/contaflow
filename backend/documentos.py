from typing import Literal
from uuid import UUID

import schemas
from app_config import get_settings
from database import get_db
from document_service import (
    DocumentListFilters,
    create_download_url,
    delete_document,
    list_documents,
    upload_document,
)
from fastapi import APIRouter, Depends, File, Form, Query, UploadFile, status
from fastapi.responses import RedirectResponse
from pagination import PaginatedResponse
from security import get_active_user, get_current_user
from sqlalchemy.orm import Session

# Configurações do Supabase Storage
from supabase import Client, create_client

settings = get_settings()
SUPABASE_URL = settings.supabase_url
SUPABASE_SERVICE_KEY = settings.supabase_service_key
BUCKET_NAME = settings.supabase_storage_bucket

# Inicializa o cliente admin do Supabase
supabase_admin: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

router = APIRouter(prefix="/api/v1/documentos", tags=["Documentos e Repositório"])


@router.get("", response_model=PaginatedResponse[schemas.DocumentResponse])
def listar_documentos(
    search: str | None = Query(None, max_length=120),
    client_id: UUID | None = Query(None),
    categoria: str | None = Query(None, max_length=40),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    return list_documents(
        db,
        current_user,
        DocumentListFilters(
            search=search,
            client_id=client_id,
            category=categoria,
            page=page,
            page_size=page_size,
        ),
    )


@router.post(
    "", response_model=schemas.DocumentResponse, status_code=status.HTTP_201_CREATED
)
async def registrar_documento(
    client_id: UUID = Form(...),
    task_id: UUID | None = Form(None),
    categoria: Literal[
        "Fiscal", "Contábil", "Departamento Pessoal", "Societário", "Geral"
    ] = Form("Geral"),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_active_user),
):
    return await upload_document(
        db,
        current_user,
        supabase_admin,
        BUCKET_NAME,
        client_id=client_id,
        task_id=task_id,
        category=categoria,
        upload=file,
    )


# ROTA 3: DOWNLOAD DE DOCUMENTO (AGORA VIA LINK ASSINADO DO SUPABASE)
@router.get("/{doc_id}/download")
def baixar_documento(
    doc_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    download_url = create_download_url(
        db,
        current_user,
        supabase_admin,
        BUCKET_NAME,
        doc_id,
    )
    return RedirectResponse(url=download_url)


# ROTA 4: EXCLUIR DOCUMENTO
@router.delete("/{doc_id}", status_code=status.HTTP_204_NO_CONTENT)
def excluir_documento(
    doc_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_active_user),
):
    return delete_document(
        db,
        current_user,
        supabase_admin,
        BUCKET_NAME,
        doc_id,
    )
