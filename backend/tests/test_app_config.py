import pytest

from app_config import load_settings


BASE = {
    "DATABASE_URL": "postgresql://postgres:postgres@localhost/contablytask",
}


def test_development_uses_only_local_cors_defaults():
    settings = load_settings({**BASE, "ENVIRONMENT": "development"})

    assert settings.environment == "development"
    assert settings.cors_allowed_origins == (
        "http://localhost:5173",
        "http://localhost:3000",
    )
    assert settings.supabase_storage_bucket == "documentos-contablytask-development"
    assert settings.asaas_environment == "sandbox"


def test_deployed_environment_requires_explicit_external_services():
    with pytest.raises(RuntimeError, match="SUPABASE_URL"):
        load_settings(
            {
                **BASE,
                "ENVIRONMENT": "staging",
                "CORS_ALLOWED_ORIGINS": "https://staging.contablytask.com.br",
            }
        )


def test_production_rejects_local_or_wildcard_cors():
    common = {
        **BASE,
        "ENVIRONMENT": "production",
        "SUPABASE_URL": "https://production.supabase.co",
        "SUPABASE_ANON_KEY": "anon",
        "SUPABASE_SERVICE_KEY": "service",
        "SUPABASE_STORAGE_BUCKET": "documents-production",
        "ASAAS_ENV": "production",
        "ASAAS_API_KEY": "asaas-production-key",
        "ASAAS_WEBHOOK_TOKEN": "asaas-production-webhook-token",
    }

    with pytest.raises(RuntimeError, match="Origem local"):
        load_settings({**common, "CORS_ALLOWED_ORIGINS": "http://localhost:5173"})
    with pytest.raises(RuntimeError, match="wildcard"):
        load_settings({**common, "CORS_ALLOWED_ORIGINS": "*"})


def test_staging_cannot_connect_to_production_asaas():
    with pytest.raises(RuntimeError, match="só é permitido"):
        load_settings(
            {
                **BASE,
                "ENVIRONMENT": "staging",
                "CORS_ALLOWED_ORIGINS": "https://staging.contablytask.com.br",
                "SUPABASE_URL": "https://staging.supabase.co",
                "SUPABASE_ANON_KEY": "anon",
                "SUPABASE_SERVICE_KEY": "service",
                "SUPABASE_STORAGE_BUCKET": "documents-staging",
                "ASAAS_ENV": "production",
                "ASAAS_API_KEY": "asaas-production-key",
                "ASAAS_WEBHOOK_TOKEN": "asaas-production-webhook-token",
            }
        )


def test_production_accepts_only_explicit_isolated_resources():
    settings = load_settings(
        {
            **BASE,
            "ENVIRONMENT": "production",
            "CORS_ALLOWED_ORIGINS": (
                "https://contablytask.com.br,https://www.contablytask.com.br"
            ),
            "SUPABASE_URL": "https://production.supabase.co",
            "SUPABASE_ANON_KEY": "anon",
            "SUPABASE_SERVICE_KEY": "service",
            "SUPABASE_STORAGE_BUCKET": "documents-production",
            "ASAAS_ENV": "production",
            "ASAAS_API_KEY": "asaas-production-key",
            "ASAAS_WEBHOOK_TOKEN": "asaas-production-webhook-token",
        }
    )

    assert settings.is_production is True
    assert settings.supabase_storage_bucket == "documents-production"
    assert settings.asaas_environment == "production"
