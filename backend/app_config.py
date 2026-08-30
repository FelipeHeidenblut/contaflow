"""Typed, environment-aware application configuration."""

from collections.abc import Mapping
from dataclasses import dataclass
from functools import lru_cache
import os
from urllib.parse import urlsplit

from dotenv import load_dotenv


ENVIRONMENTS = {"development", "test", "staging", "production"}
DEPLOYED_ENVIRONMENTS = {"staging", "production"}


@dataclass(frozen=True)
class Settings:
    environment: str
    database_url: str
    cors_allowed_origins: tuple[str, ...]
    supabase_url: str
    supabase_anon_key: str
    supabase_service_key: str
    supabase_jwt_secret: str | None
    supabase_storage_bucket: str
    asaas_environment: str
    asaas_api_key: str | None
    asaas_webhook_token: str | None

    @property
    def is_production(self) -> bool:
        return self.environment == "production"

    @property
    def is_development(self) -> bool:
        return self.environment == "development"


def _clean(value: str | None) -> str:
    return (value or "").strip()


def _required(values: Mapping[str, str], name: str, environment: str) -> str:
    value = _clean(values.get(name))
    if not value:
        raise RuntimeError(f"{name} é obrigatória no ambiente {environment}.")
    return value


def _normalize_database_url(value: str) -> str:
    if value.startswith("postgres://"):
        return value.replace("postgres://", "postgresql://", 1)
    return value


def get_database_url(values: Mapping[str, str] | None = None) -> str:
    """Load only the setting required by Alembic and SQLAlchemy bootstrap."""
    source = values if values is not None else os.environ
    environment = _clean(source.get("ENVIRONMENT")) or "development"
    return _normalize_database_url(_required(source, "DATABASE_URL", environment))


def _parse_origins(raw_origins: str, environment: str) -> tuple[str, ...]:
    origins: list[str] = []
    for raw_origin in raw_origins.split(","):
        origin = raw_origin.strip().rstrip("/")
        if not origin:
            continue
        if origin == "*":
            raise RuntimeError("CORS_ALLOWED_ORIGINS não pode usar wildcard.")

        parsed = urlsplit(origin)
        if (
            parsed.scheme not in {"http", "https"}
            or not parsed.netloc
            or parsed.path not in {"", "/"}
            or parsed.query
            or parsed.fragment
        ):
            raise RuntimeError(f"Origem CORS inválida: {origin}")
        if environment in DEPLOYED_ENVIRONMENTS and parsed.hostname in {
            "localhost",
            "127.0.0.1",
            "::1",
        }:
            raise RuntimeError(
                f"Origem local não permitida no ambiente {environment}: {origin}"
            )
        if origin not in origins:
            origins.append(origin)

    if not origins:
        raise RuntimeError(
            f"CORS_ALLOWED_ORIGINS deve ter ao menos uma origem no ambiente {environment}."
        )
    return tuple(origins)


def load_settings(values: Mapping[str, str] | None = None) -> Settings:
    source = values if values is not None else os.environ
    environment = _clean(source.get("ENVIRONMENT")) or "development"
    if environment not in ENVIRONMENTS:
        raise RuntimeError(
            "ENVIRONMENT deve ser development, test, staging ou production."
        )

    database_url = get_database_url(source)

    default_origins = (
        "http://localhost:5173,http://localhost:3000"
        if environment in {"development", "test"}
        else ""
    )
    raw_origins = _clean(source.get("CORS_ALLOWED_ORIGINS"))
    if not raw_origins:
        # Compatibilidade temporária com a variável usada antes desta separação.
        raw_origins = _clean(source.get("FRONTEND_URL")) or default_origins
    cors_allowed_origins = _parse_origins(raw_origins, environment)

    require_external_services = environment in DEPLOYED_ENVIRONMENTS
    supabase_url = _clean(source.get("SUPABASE_URL"))
    supabase_anon_key = _clean(source.get("SUPABASE_ANON_KEY"))
    supabase_service_key = _clean(source.get("SUPABASE_SERVICE_KEY"))
    storage_bucket = _clean(source.get("SUPABASE_STORAGE_BUCKET"))
    if require_external_services:
        supabase_url = _required(source, "SUPABASE_URL", environment)
        supabase_anon_key = _required(source, "SUPABASE_ANON_KEY", environment)
        supabase_service_key = _required(source, "SUPABASE_SERVICE_KEY", environment)
        storage_bucket = _required(source, "SUPABASE_STORAGE_BUCKET", environment)
    elif not storage_bucket:
        storage_bucket = f"documentos-contablytask-{environment}"

    asaas_environment = _clean(source.get("ASAAS_ENV")) or "sandbox"
    if asaas_environment not in {"sandbox", "production"}:
        raise RuntimeError("ASAAS_ENV deve ser sandbox ou production.")
    if environment == "production" and asaas_environment != "production":
        raise RuntimeError("Produção deve usar ASAAS_ENV=production.")
    if environment != "production" and asaas_environment == "production":
        raise RuntimeError(
            "ASAAS_ENV=production só é permitido com ENVIRONMENT=production."
        )
    asaas_api_key = _clean(source.get("ASAAS_API_KEY"))
    asaas_webhook_token = _clean(source.get("ASAAS_WEBHOOK_TOKEN"))
    if require_external_services:
        asaas_api_key = _required(source, "ASAAS_API_KEY", environment)
        asaas_webhook_token = _required(source, "ASAAS_WEBHOOK_TOKEN", environment)

    return Settings(
        environment=environment,
        database_url=database_url,
        cors_allowed_origins=cors_allowed_origins,
        supabase_url=supabase_url,
        supabase_anon_key=supabase_anon_key,
        supabase_service_key=supabase_service_key,
        supabase_jwt_secret=_clean(source.get("SUPABASE_JWT_SECRET")) or None,
        supabase_storage_bucket=storage_bucket,
        asaas_environment=asaas_environment,
        asaas_api_key=asaas_api_key or None,
        asaas_webhook_token=asaas_webhook_token or None,
    )


load_dotenv()


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return load_settings()
