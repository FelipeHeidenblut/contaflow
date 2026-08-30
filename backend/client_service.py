import csv
import io
import re
from dataclasses import dataclass
from uuid import UUID

import models
import schemas
from access_control import (
    Permission,
    TenantRepository,
    apply_client_scope,
    require_permission,
    tenant_repository,
    validate_responsible_profile,
)
from fastapi import HTTPException, status
from pagination import paginate
from plan_config import get_plan_limit, get_plan_name
from sqlalchemy import func, or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

DOCUMENT_LOOKUP_BATCH_SIZE = 1_000


@dataclass(frozen=True, slots=True)
class ClientListFilters:
    search: str | None = None
    natureza: str | None = None
    responsible_profile_id: UUID | None = None
    unassigned: bool = False
    page: int = 1
    page_size: int = 20


def _lock_tenant_and_get_client_capacity(
    db: Session,
    repository: TenantRepository,
) -> tuple[models.Tenant, int | None, int]:
    """Serializa alterações que consomem o limite de clientes do escritório."""
    tenant = (
        db.query(models.Tenant)
        .filter(models.Tenant.id == repository.context.tenant_id)
        .with_for_update()
        .first()
    )
    if not tenant:
        raise HTTPException(status_code=404, detail="Escritório não encontrado.")

    limit = get_plan_limit(tenant.plano, "clients")
    active_clients = (
        repository.query(models.Client)
        .filter(models.Client.ativo.is_(True))
        .count()
    )
    return tenant, limit, active_clients


def _find_client_by_document(
    repository: TenantRepository,
    *,
    person_type: str,
    document: str,
) -> models.Client | None:
    condition = _normalized_document_expression(person_type) == document
    return repository.query(models.Client).filter(condition).first()


def _normalized_document_expression(person_type: str):
    if person_type == "PF":
        return func.regexp_replace(models.Client.cpf, "[^0-9]", "", "g")
    return func.upper(
        func.regexp_replace(
            models.Client.cnpj,
            "[^A-Za-z0-9]",
            "",
            "g",
        )
    )


def _existing_document_keys(
    repository: TenantRepository,
    document_keys: set[tuple[str, str]],
) -> set[tuple[str, str]]:
    existing: set[tuple[str, str]] = set()
    for person_type in ("PF", "PJ"):
        documents = {
            document
            for key_type, document in document_keys
            if key_type == person_type
        }
        if not documents:
            continue
        expression = _normalized_document_expression(person_type)
        document_list = list(documents)
        for offset in range(0, len(document_list), DOCUMENT_LOOKUP_BATCH_SIZE):
            batch = document_list[offset : offset + DOCUMENT_LOOKUP_BATCH_SIZE]
            rows = (
                repository.query(models.Client)
                .with_entities(expression)
                .filter(expression.in_(batch))
                .all()
            )
            existing.update(
                (person_type, str(row[0]))
                for row in rows
                if row[0] is not None
            )
    return existing


def _plan_limit_error(tenant: models.Tenant, limit: int) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail=(
            f"Você atingiu o limite de {limit} clientes do plano "
            f"{get_plan_name(tenant.plano)}. Faça upgrade para adicionar mais!"
        ),
    )


def create_client(
    db: Session,
    current_user: dict,
    client_input: schemas.ClientCreate,
) -> models.Client:
    require_permission(current_user, Permission.CLIENT_MANAGE)
    repository = tenant_repository(db, current_user)
    validate_responsible_profile(
        db,
        current_user,
        client_input.responsible_profile_id,
    )
    tenant, limit, active_clients = _lock_tenant_and_get_client_capacity(
        db,
        repository,
    )
    if limit is not None and active_clients >= limit:
        raise _plan_limit_error(tenant, limit)

    document = (
        client_input.cpf
        if client_input.tipo_pessoa == "PF"
        else client_input.cnpj
    )
    if document and _find_client_by_document(
        repository,
        person_type=client_input.tipo_pessoa,
        document=document,
    ):
        document_name = "CPF" if client_input.tipo_pessoa == "PF" else "CNPJ"
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Este {document_name} já está cadastrado no seu escritório.",
        )

    client = models.Client(
        tenant_id=repository.context.tenant_id,
        tipo_pessoa=client_input.tipo_pessoa,
        nome=client_input.nome,
        cpf=client_input.cpf,
        razao_social=client_input.razao_social,
        cnpj=client_input.cnpj,
        regime_tributario=client_input.regime_tributario,
        natureza_operacao=client_input.natureza_operacao,
        email=str(client_input.email) if client_input.email else None,
        responsible_profile_id=client_input.responsible_profile_id,
    )
    db.add(client)
    try:
        db.commit()
    except IntegrityError as error:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="CPF/CNPJ já cadastrado neste escritório.",
        ) from error
    db.refresh(client)
    return client


def list_clients(
    db: Session,
    current_user: dict,
    filters: ClientListFilters,
) -> dict:
    require_permission(current_user, Permission.CLIENT_READ)
    repository = tenant_repository(db, current_user)
    base_query = apply_client_scope(
        repository.query(models.Client).filter(models.Client.ativo.is_(True)),
        current_user,
    )
    total, total_pj, total_pf = base_query.with_entities(
        func.count(models.Client.id),
        func.count(models.Client.id).filter(models.Client.tipo_pessoa == "PJ"),
        func.count(models.Client.id).filter(models.Client.tipo_pessoa == "PF"),
    ).one()

    query = base_query
    if filters.search:
        term = filters.search.strip()
        search_conditions = [
            models.Client.nome.icontains(term, autoescape=True),
            models.Client.razao_social.icontains(term, autoescape=True),
        ]
        normalized_document = re.sub(r"[^A-Za-z0-9]", "", term).upper()
        if normalized_document:
            search_conditions.extend(
                [
                    func.regexp_replace(
                        models.Client.cpf,
                        "[^0-9]",
                        "",
                        "g",
                    ).icontains(normalized_document, autoescape=True),
                    func.upper(
                        func.regexp_replace(
                            models.Client.cnpj,
                            "[^A-Za-z0-9]",
                            "",
                            "g",
                        )
                    ).icontains(normalized_document, autoescape=True),
                ]
            )
        query = query.filter(or_(*search_conditions))
    if filters.natureza:
        query = query.filter(models.Client.natureza_operacao == filters.natureza)
    if filters.unassigned:
        query = query.filter(models.Client.responsible_profile_id.is_(None))
    elif filters.responsible_profile_id:
        query = query.filter(
            models.Client.responsible_profile_id == filters.responsible_profile_id
        )

    query = query.order_by(
        func.coalesce(models.Client.razao_social, models.Client.nome).asc(),
        models.Client.id.asc(),
    )
    return paginate(
        query,
        page=filters.page,
        page_size=filters.page_size,
        summary={"total": total, "pj": total_pj, "pf": total_pf},
    )


def deactivate_client(
    db: Session,
    current_user: dict,
    client_id: UUID,
) -> models.Client:
    require_permission(current_user, Permission.CLIENT_MANAGE)
    client = tenant_repository(db, current_user).get(
        models.Client,
        client_id,
        for_update=True,
        detail="Cliente não encontrado.",
    )
    client.ativo = False
    db.commit()
    db.refresh(client)
    return client


def assign_responsible(
    db: Session,
    current_user: dict,
    client_id: UUID,
    responsible_profile_id: UUID | None,
) -> models.Client:
    require_permission(current_user, Permission.CLIENT_MANAGE)
    client = tenant_repository(db, current_user).get(
        models.Client,
        client_id,
        for_update=True,
        detail="Cliente não encontrado.",
    )
    validate_responsible_profile(db, current_user, responsible_profile_id)
    client.responsible_profile_id = responsible_profile_id
    db.commit()
    db.refresh(client)
    return client


def _decode_csv(contents: bytes) -> str:
    try:
        return contents.decode("utf-8-sig")
    except UnicodeDecodeError:
        return contents.decode("iso-8859-1")


def _csv_rows(decoded_content: str) -> csv.DictReader:
    reader = csv.DictReader(io.StringIO(decoded_content), delimiter=";")
    if not reader.fieldnames or len(reader.fieldnames) < 3:
        reader = csv.DictReader(io.StringIO(decoded_content), delimiter=",")
    return reader


def _client_from_csv_row(
    row: dict,
    *,
    tenant_id: UUID,
) -> tuple[models.Client | None, tuple[str, str] | None]:
    person_type = str(row.get("TIPO (PF/PJ)") or "").strip().upper()
    name = str(row.get("NOME_OU_RAZAO") or "").strip()
    document = re.sub(
        r"[^A-Za-z0-9]",
        "",
        str(row.get("CPF_OU_CNPJ") or ""),
    )
    if person_type not in {"PF", "PJ"} or not name or not document:
        return None, None
    if person_type == "PF" and (not document.isdigit() or len(document) != 11):
        return None, None
    if person_type == "PJ" and len(document) != 14:
        return None, None
    if person_type == "PJ":
        document = document.upper()

    client = models.Client(
        tenant_id=tenant_id,
        tipo_pessoa=person_type,
        regime_tributario=str(
            row.get("REGIME_TRIBUTARIO") or "Simples Nacional"
        ).strip(),
        natureza_operacao=str(row.get("NATUREZA_OPERACAO") or "Serviços").strip(),
    )
    if person_type == "PF":
        client.nome = name
        client.cpf = document
    else:
        client.razao_social = name
        client.cnpj = document
    return client, (person_type, document)


def import_clients_from_csv(
    db: Session,
    current_user: dict,
    contents: bytes,
) -> dict[str, int | str]:
    require_permission(current_user, Permission.CLIENT_MANAGE)
    repository = tenant_repository(db, current_user)

    try:
        reader = _csv_rows(_decode_csv(contents))
        candidates: list[tuple[models.Client, tuple[str, str]]] = []
        invalid_rows = 0
        documents_in_file: set[tuple[str, str]] = set()

        for row in reader:
            if not any(row.values()):
                continue
            client, document_key = _client_from_csv_row(
                row,
                tenant_id=repository.context.tenant_id,
            )
            if client is None or document_key is None:
                invalid_rows += 1
                continue
            if document_key in documents_in_file:
                invalid_rows += 1
                continue
            documents_in_file.add(document_key)

            candidates.append((client, document_key))

        # O parsing não precisa manter um lock no escritório. A seção crítica
        # começa apenas antes das consultas e gravações que consomem o plano.
        tenant, limit, active_clients = _lock_tenant_and_get_client_capacity(
            db,
            repository,
        )
        existing_documents = _existing_document_keys(
            repository,
            documents_in_file,
        )
        valid_clients = []
        for client, document_key in candidates:
            if document_key in existing_documents:
                invalid_rows += 1
                continue
            valid_clients.append(client)

        if limit is not None and active_clients + len(valid_clients) > limit:
            available_slots = max(0, int(limit - active_clients))
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    f"O arquivo possui {len(valid_clients)} cliente(s) válido(s), mas o plano "
                    f"{get_plan_name(tenant.plano)} tem apenas "
                    f"{available_slots} vaga(s) disponível(is). Nenhum cliente foi importado."
                ),
            )

        for client in valid_clients:
            db.add(client)
        db.commit()
        return {
            "message": "Importação concluída",
            "importados": len(valid_clients),
            "erros": invalid_rows,
        }
    except HTTPException:
        db.rollback()
        raise
    except IntegrityError as error:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "A importação encontrou um CPF/CNPJ já cadastrado. "
                "Nenhum cliente foi importado."
            ),
        ) from error
    except Exception as error:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao processar o CSV.",
        ) from error
