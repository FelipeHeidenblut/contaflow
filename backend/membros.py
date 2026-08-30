import logging
from typing import List
from uuid import UUID

import httpx
import models
from access_control import Permission, require_permission, tenant_repository
from app_config import get_settings
from database import get_db
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pagination import PaginatedResponse, paginate
from pydantic import BaseModel, ConfigDict, EmailStr, Field
from plan_config import get_plan_limit, get_plan_name
from typing import Literal
from security import get_active_user, get_current_user
from sqlalchemy import func, or_
from sqlalchemy.orm import Session

# ==========================================
# CONFIGURAÇÃO DOS ENDPOINTS DO SUPABASE
# ==========================================
settings = get_settings()
SUPABASE_URL = settings.supabase_url
SUPABASE_SERVICE_KEY = settings.supabase_service_key
SUPABASE_ANON_KEY = settings.supabase_anon_key
INVITE_REDIRECT_URL = (
    f"{settings.cors_allowed_origins[0].rstrip('/')}/redefinir-senha"
)

router = APIRouter(prefix="/api/v1/membros", tags=["Equipe e Membros"])
logger = logging.getLogger("ContablyTask.Membros")

def _supabase_admin_headers(*, include_json: bool = False) -> dict[str, str]:
    if not SUPABASE_SERVICE_KEY:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Gerenciamento de usuários temporariamente indisponível.",
        )
    headers = {
        "apikey": SUPABASE_SERVICE_KEY,
        "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
    }
    if include_json:
        headers["Content-Type"] = "application/json"
    return headers


def _delete_supabase_user(user_id: str) -> bool:
    url = f"{SUPABASE_URL.rstrip('/')}/auth/v1/admin/users/{user_id}"
    try:
        with httpx.Client(timeout=10.0) as client:
            response = client.delete(url, headers=_supabase_admin_headers())
    except httpx.RequestError:
        logger.exception("Falha ao compensar criação de usuário no provedor.")
        return False
    if response.status_code in {200, 204, 404}:
        return True
    logger.error(
        "Provedor recusou compensação de usuário (HTTP %s).",
        response.status_code,
    )
    return False


def _compensate_failed_member(db: Session, user_id: str) -> None:
    db.rollback()
    try:
        local_user_id = UUID(user_id)
    except ValueError:
        local_user_id = None
    try:
        stale_profile = None
        if local_user_id:
            stale_profile = (
                db.query(models.Profile)
                .filter(models.Profile.id == local_user_id)
                .first()
            )
        if stale_profile:
            db.delete(stale_profile)
            db.commit()
    except Exception:
        db.rollback()
        logger.exception("Falha ao remover perfil local após provisionamento incompleto.")
    if not _delete_supabase_user(user_id):
        logger.critical("Provisionamento incompleto exige reconciliação administrativa.")


# ==========================================
# SCHEMAS LOCAIS (Pydantic)
# ==========================================
class ProfileCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str = Field(..., min_length=2, max_length=150)
    email: EmailStr
    role: Literal["admin", "gerente", "colaborador"]


class ProfileResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    name: str
    email: str
    role: str


# ==========================================
# DEPENDÊNCIA DE SEGURANÇA (RBAC)
# ==========================================
def verificar_admin(current_user: dict = Depends(get_active_user)):
    """
    Verifica se o usuário logado tem permissão de 'admin'.
    Otimização: A role já vem no current_user (buscada no security.py), não precisamos de DB aqui.
    """
    require_permission(
        current_user,
        Permission.MEMBER_MANAGE,
        detail="Acesso negado. Apenas administradores podem gerenciar a equipe.",
    )
    return current_user


# ==========================================
# ROTAS
# ==========================================
@router.get("", response_model=PaginatedResponse[ProfileResponse])
def listar_membros(
    search: str | None = Query(None, max_length=120),
    role: Literal["admin", "gerente", "colaborador"] | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    require_permission(current_user, Permission.MEMBER_READ)
    base_query = tenant_repository(db, current_user).query(models.Profile)
    total, admins, gerentes, colaboradores = base_query.with_entities(
        func.count(models.Profile.id),
        func.count(models.Profile.id).filter(models.Profile.role == "admin"),
        func.count(models.Profile.id).filter(models.Profile.role == "gerente"),
        func.count(models.Profile.id).filter(models.Profile.role == "colaborador"),
    ).one()
    query = base_query
    if search:
        term = search.strip()
        query = query.filter(
            or_(
                models.Profile.name.icontains(term, autoescape=True),
                models.Profile.email.icontains(term, autoescape=True),
            )
        )
    if role:
        query = query.filter(models.Profile.role == role)
    query = query.order_by(
        models.Profile.name.asc(), models.Profile.id.asc()
    )
    return paginate(
        query,
        page=page,
        page_size=page_size,
        summary={
            "total": total,
            "admins": admins,
            "gerentes": gerentes,
            "colaboradores": colaboradores,
        },
    )


@router.post("", response_model=ProfileResponse, status_code=status.HTTP_201_CREATED)
def adicionar_membro(
    membro_in: ProfileCreate,
    db: Session = Depends(get_db),
    admin_user: dict = Depends(verificar_admin),
):
    repository = tenant_repository(db, admin_user)
    tenant_id = repository.context.tenant_id

    tenant = (
        db.query(models.Tenant)
        .filter(models.Tenant.id == tenant_id)
        .first()
    )
    if not tenant:
        raise HTTPException(status_code=404, detail="Escritório não encontrado.")
    limite = get_plan_limit(tenant.plano, "members")

    total_membros = repository.query(models.Profile).count()

    if limite is not None and total_membros >= limite:
        raise HTTPException(
            status_code=403,
            detail=(
                f"Seu plano {get_plan_name(tenant.plano)} permite "
                f"apenas {limite} usuário(s). Faça upgrade para adicionar mais membros!"
            ),
        )

    # 1. Verifica no banco se o e-mail já existe
    existe = (
        db.query(models.Profile).filter(models.Profile.email == membro_in.email).first()
    )
    if existe:
        raise HTTPException(
            status_code=400, detail="Este e-mail já está cadastrado no sistema."
        )

    # 2. O provedor cria o usuário e envia um convite de uso único. A senha é
    # definida pelo próprio funcionário depois que ele comprova acesso ao e-mail.
    url_create = f"{SUPABASE_URL.rstrip('/')}/auth/v1/invite"
    payload_create = {
        "email": membro_in.email,
        "data": {"name": membro_in.name, "tenant_id": str(tenant_id)},
    }

    provider_user_id: str | None = None
    try:
        with httpx.Client(timeout=10.0) as client:
            response = client.post(
                url_create,
                json=payload_create,
                params={"redirect_to": INVITE_REDIRECT_URL},
                headers=_supabase_admin_headers(include_json=True),
            )

            if response.status_code not in [200, 201]:
                raise HTTPException(
                    status_code=502,
                    detail="Não foi possível criar o usuário no provedor de autenticação.",
                )

            dados_supabase = response.json()
            if not isinstance(dados_supabase, dict):
                raise HTTPException(
                    status_code=502,
                    detail="O provedor retornou uma resposta inválida.",
                )
            provider_user = dados_supabase.get("user") or dados_supabase
            if not isinstance(provider_user, dict):
                raise HTTPException(
                    status_code=502,
                    detail="O provedor retornou uma identidade inválida.",
                )
            provider_user_id = str(provider_user.get("id") or "") or None

        if not provider_user_id:
            raise HTTPException(
                status_code=500, detail="Supabase não retornou o ID do novo usuário."
            )
        try:
            novo_user_id = UUID(provider_user_id)
        except ValueError as error:
            raise HTTPException(
                status_code=502,
                detail="O provedor retornou uma identidade inválida.",
            ) from error

        # 3. A chamada externa já terminou. Agora serializa a checagem final do
        # limite sem bloquear a trigger do Supabase que referencia este tenant.
        db.expire_all()
        tenant = (
            db.query(models.Tenant)
            .filter(models.Tenant.id == tenant_id)
            .with_for_update()
            .first()
        )
        if not tenant:
            raise HTTPException(status_code=404, detail="Escritório não encontrado.")
        limite = get_plan_limit(tenant.plano, "members")

        # 4. Busca o perfil que a Trigger do banco pode ter criado automaticamente.
        perfil_criado = (
            repository.query(models.Profile)
            .filter(models.Profile.id == novo_user_id)
            .first()
        )
        total_membros = repository.query(models.Profile).count()
        limite_excedido = limite is not None and (
            total_membros > limite if perfil_criado else total_membros >= limite
        )
        if limite_excedido:
            raise HTTPException(
                status_code=403,
                detail=(
                    f"Seu plano {get_plan_name(tenant.plano)} permite "
                    f"apenas {limite} usuário(s). O usuário excedente não foi criado."
                ),
            )

        if perfil_criado:
            perfil_criado.name = membro_in.name  # type: ignore
            perfil_criado.role = membro_in.role  # type: ignore
            db.commit()
            db.refresh(perfil_criado)
            return perfil_criado
        novo_perfil = models.Profile(
            id=novo_user_id,
            name=membro_in.name,
            email=membro_in.email,
            role=membro_in.role,
            tenant_id=tenant_id,
        )
        db.add(novo_perfil)
        db.commit()
        db.refresh(novo_perfil)
        return novo_perfil
    except httpx.RequestError as error:
        db.rollback()
        raise HTTPException(
            status_code=502,
            detail="Falha de comunicação com o provedor de autenticação.",
        ) from error
    except HTTPException:
        if provider_user_id:
            _compensate_failed_member(db, provider_user_id)
        else:
            db.rollback()
        raise
    except Exception as error:
        if provider_user_id:
            _compensate_failed_member(db, provider_user_id)
        else:
            db.rollback()
        logger.exception("Falha ao concluir o provisionamento local de membro.")
        raise HTTPException(
            status_code=500,
            detail="Usuário não pôde ser provisionado. Tente novamente.",
        ) from error


@router.delete("/{membro_id}", status_code=status.HTTP_204_NO_CONTENT)
def remover_membro(
    membro_id: UUID,
    db: Session = Depends(get_db),
    admin_user: dict = Depends(verificar_admin),
):
    membro = tenant_repository(db, admin_user).get(
        models.Profile, membro_id, detail="Membro não encontrado."
    )

    if str(membro.id) == admin_user.get("user_id"):
        raise HTTPException(
            status_code=400, detail="Você não pode excluir sua própria conta."
        )

    # ==========================================
    # CORREÇÃO: Apagar o usuário do Supabase Auth também!
    # ==========================================
    user_id_str = str(membro.id)
    url_delete = f"{SUPABASE_URL.rstrip('/')}/auth/v1/admin/users/{user_id_str}"
    headers = {
        "apikey": SUPABASE_SERVICE_KEY,
        "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
    }

    try:
        with httpx.Client(timeout=10.0) as client:
            # Faz a requisição DELETE para o Supabase
            response = client.delete(url_delete, headers=headers)
            
            # Se o Supabase devolver 200, 204 ou 404 (já apagado), podemos prosseguir.
            # Se devolver outro erro, precisamos abortar para não ficar órfão.
            if response.status_code not in [200, 204, 404]:
                raise HTTPException(
                    status_code=500,
                    detail="Não foi possível remover o usuário do provedor de autenticação."
                )
    except httpx.RequestError as e:
        raise HTTPException(
            status_code=500,
            detail="Falha de comunicação com o provedor de autenticação."
        )

    # Agora sim, apaga o perfil do banco de dados local
    db.delete(membro)
    db.commit()
    return None
