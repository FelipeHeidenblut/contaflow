import logging
import os
import tempfile
import uuid
import zipfile
from dataclasses import dataclass
from typing import Any
from urllib.parse import urlsplit
from uuid import UUID

import models
from access_control import (
    Permission,
    apply_client_scope,
    get_accessible_client,
    get_accessible_task,
    require_permission,
    tenant_repository,
)
from fastapi import HTTPException, UploadFile, status
from pagination import paginate
from sqlalchemy import func
from sqlalchemy.orm import Session


logger = logging.getLogger("ContablyTask.Documents")

MAX_FILE_SIZE = 5 * 1024 * 1024
CHUNK_SIZE = 1024 * 1024
SIGNED_URL_TTL_SECONDS = 3600


@dataclass(frozen=True, slots=True)
class FileRule:
    content_type: str
    signatures: tuple[bytes, ...]
    required_zip_members: frozenset[str] = frozenset()


ALLOWED_FILES = {
    ".pdf": FileRule("application/pdf", (b"%PDF-",)),
    ".png": FileRule("image/png", (b"\x89PNG\r\n\x1a\n",)),
    ".jpg": FileRule("image/jpeg", (b"\xff\xd8\xff",)),
    ".jpeg": FileRule("image/jpeg", (b"\xff\xd8\xff",)),
    ".docx": FileRule(
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        (b"PK\x03\x04",),
        frozenset({"[Content_Types].xml", "word/document.xml"}),
    ),
    ".xlsx": FileRule(
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        (b"PK\x03\x04",),
        frozenset({"[Content_Types].xml", "xl/workbook.xml"}),
    ),
}


@dataclass(frozen=True, slots=True)
class DocumentListFilters:
    search: str | None = None
    client_id: UUID | None = None
    category: str | None = None
    page: int = 1
    page_size: int = 20


def list_documents(
    db: Session,
    current_user: dict,
    filters: DocumentListFilters,
) -> dict:
    require_permission(current_user, Permission.DOCUMENT_READ)
    repository = tenant_repository(db, current_user)
    base_query = repository.query(models.Document).join(
        models.Client,
        (models.Document.client_id == models.Client.id)
        & (models.Document.tenant_id == models.Client.tenant_id),
    )
    base_query = apply_client_scope(base_query, current_user)
    total, fiscal, contabil, geral = base_query.with_entities(
        func.count(models.Document.id),
        func.count(models.Document.id).filter(models.Document.categoria == "Fiscal"),
        func.count(models.Document.id).filter(
            models.Document.categoria == "Contábil"
        ),
        func.count(models.Document.id).filter(models.Document.categoria == "Geral"),
    ).one()

    query = base_query
    if filters.search:
        query = query.filter(
            models.Document.nome_arquivo.icontains(
                filters.search.strip(),
                autoescape=True,
            )
        )
    if filters.client_id:
        query = query.filter(models.Document.client_id == filters.client_id)
    if filters.category:
        query = query.filter(models.Document.categoria == filters.category)
    query = query.order_by(
        models.Document.created_at.desc(),
        models.Document.id.asc(),
    )
    return paginate(
        query,
        page=filters.page,
        page_size=filters.page_size,
        summary={
            "total": total,
            "fiscal": fiscal,
            "contabil": contabil,
            "geral": geral,
        },
    )


def _safe_original_name(filename: str | None) -> tuple[str, str]:
    raw_name = (filename or "documento").replace("\\", "/")
    basename = os.path.basename(raw_name)
    printable_name = "".join(
        character
        for character in basename
        if character.isprintable() and character not in {"\r", "\n", "\x00"}
    ).strip()
    extension = os.path.splitext(printable_name)[1].lower()
    if extension not in ALLOWED_FILES:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Tipo de arquivo não permitido.",
        )

    stem = os.path.splitext(printable_name)[0]
    max_stem_length = 255 - len(extension)
    safe_name = f"{stem[:max_stem_length]}{extension}"
    return safe_name, extension


def _validate_office_archive(path: str, rule: FileRule) -> None:
    if not rule.required_zip_members:
        return
    try:
        with zipfile.ZipFile(path) as archive:
            members = set(archive.namelist())
    except (OSError, zipfile.BadZipFile) as error:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Conteúdo do arquivo não corresponde à extensão.",
        ) from error
    if not rule.required_zip_members.issubset(members):
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Conteúdo do arquivo não corresponde à extensão.",
        )


async def _write_validated_temp_file(
    upload: UploadFile,
    extension: str,
    rule: FileRule,
) -> str:
    temp_path: str | None = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=extension) as temp_file:
            temp_path = temp_file.name
            total_size = 0
            first_chunk = True
            while chunk := await upload.read(CHUNK_SIZE):
                total_size += len(chunk)
                if total_size > MAX_FILE_SIZE:
                    raise HTTPException(
                        status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                        detail="Arquivo excede o limite máximo de 5MB.",
                    )
                if first_chunk:
                    if not any(
                        chunk.startswith(signature)
                        for signature in rule.signatures
                    ):
                        raise HTTPException(
                            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                            detail=(
                                "Conteúdo do arquivo não corresponde à extensão."
                            ),
                        )
                    first_chunk = False
                temp_file.write(chunk)
            if first_chunk:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Arquivo vazio.",
                )
        _validate_office_archive(temp_path, rule)
        return temp_path
    except Exception:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)
        raise


def _bucket(storage_client: Any, bucket_name: str):
    return storage_client.storage.from_(bucket_name)


def _remove_storage_object(
    storage_client: Any,
    bucket_name: str,
    storage_path: str,
) -> None:
    _bucket(storage_client, bucket_name).remove([storage_path])


def _assert_tenant_storage_path(document: models.Document, tenant_id: UUID) -> None:
    expected_prefix = f"{tenant_id}/{document.client_id}/"
    if not document.storage_path.startswith(expected_prefix):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Documento indisponível.",
        )


async def upload_document(
    db: Session,
    current_user: dict,
    storage_client: Any,
    bucket_name: str,
    *,
    client_id: UUID,
    task_id: UUID | None,
    category: str,
    upload: UploadFile,
) -> models.Document:
    require_permission(current_user, Permission.DOCUMENT_WRITE)
    repository = tenant_repository(db, current_user)
    get_accessible_client(db, client_id, current_user, active_only=True)
    if task_id:
        task = get_accessible_task(db, task_id, current_user)
        if task.client_id != client_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tarefa não encontrada para este cliente.",
            )

    original_name, extension = _safe_original_name(upload.filename)
    rule = ALLOWED_FILES[extension]
    safe_storage_name = f"{uuid.uuid4()}{extension}"
    storage_path = (
        f"{repository.context.tenant_id}/{client_id}/{safe_storage_name}"
    )
    temp_path = await _write_validated_temp_file(upload, extension, rule)
    try:
        with open(temp_path, "rb") as source:
            _bucket(storage_client, bucket_name).upload(
                storage_path,
                source,
                file_options={
                    "content-type": rule.content_type,
                    "content-disposition": (
                        f'attachment; filename="{safe_storage_name}"'
                    ),
                },
            )
    except Exception as error:
        logger.exception("Falha no upload do documento para o Storage.")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao salvar o arquivo na nuvem.",
        ) from error
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

    document = models.Document(
        tenant_id=repository.context.tenant_id,
        client_id=client_id,
        task_id=task_id,
        nome_arquivo=original_name,
        categoria=category,
        storage_path=storage_path,
        uploaded_by=repository.context.user_id,
    )
    try:
        db.add(document)
        db.commit()
    except Exception as error:
        db.rollback()
        try:
            _remove_storage_object(storage_client, bucket_name, storage_path)
        except Exception:
            logger.exception(
                "Falha ao compensar upload do documento após erro no banco."
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao registrar o documento.",
        ) from error
    db.refresh(document)
    return document


def create_download_url(
    db: Session,
    current_user: dict,
    storage_client: Any,
    bucket_name: str,
    document_id: UUID,
) -> str:
    require_permission(current_user, Permission.DOCUMENT_READ)
    repository = tenant_repository(db, current_user)
    document = repository.get(
        models.Document,
        document_id,
        detail="Registro do documento não encontrado.",
    )
    get_accessible_client(db, document.client_id, current_user)
    _assert_tenant_storage_path(document, repository.context.tenant_id)

    try:
        response = _bucket(storage_client, bucket_name).create_signed_url(
            document.storage_path,
            expires_in=SIGNED_URL_TTL_SECONDS,
        )
        download_url = (
            response.get("signedURL") or response.get("signedUrl")
            if isinstance(response, dict)
            else None
        )
        parsed_url = urlsplit(download_url or "")
        if parsed_url.scheme not in {"http", "https"} or not parsed_url.netloc:
            raise ValueError("URL assinada inválida")
    except Exception as error:
        logger.exception(
            "Falha ao gerar URL assinada para o documento %s.",
            document.id,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao gerar link de download.",
        ) from error
    return download_url


def delete_document(
    db: Session,
    current_user: dict,
    storage_client: Any,
    bucket_name: str,
    document_id: UUID,
) -> None:
    require_permission(current_user, Permission.DOCUMENT_DELETE)
    repository = tenant_repository(db, current_user)
    document = repository.get(
        models.Document,
        document_id,
        for_update=True,
        detail="Documento não encontrado.",
    )
    get_accessible_client(db, document.client_id, current_user)
    _assert_tenant_storage_path(document, repository.context.tenant_id)

    try:
        _remove_storage_object(storage_client, bucket_name, document.storage_path)
    except Exception as error:
        db.rollback()
        logger.exception(
            "Falha ao excluir objeto do Storage para o documento %s.",
            document.id,
        )
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Não foi possível excluir o arquivo da nuvem. Tente novamente.",
        ) from error

    db.delete(document)
    try:
        db.commit()
    except Exception as error:
        db.rollback()
        logger.exception(
            "Objeto removido do Storage, mas o registro %s não pôde ser excluído.",
            document.id,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="O arquivo foi removido, mas o registro não pôde ser atualizado.",
        ) from error
