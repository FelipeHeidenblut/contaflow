"""Keep the test suite isolated from every developer or production environment."""

import os


os.environ["ENVIRONMENT"] = "test"
os.environ["DATABASE_URL"] = (
    "postgresql://postgres:postgres@localhost:5432/contablytask_test"
)
os.environ["CORS_ALLOWED_ORIGINS"] = "http://localhost:5173"
os.environ["SUPABASE_URL"] = "https://example.supabase.co"
os.environ["SUPABASE_ANON_KEY"] = "test-placeholder"
os.environ["SUPABASE_SERVICE_KEY"] = "test-placeholder"
os.environ["SUPABASE_STORAGE_BUCKET"] = "documentos-contablytask-test"
os.environ["ASAAS_ENV"] = "sandbox"
os.environ["ASAAS_API_KEY"] = "$aact_hmlg_test-placeholder"
os.environ["ASAAS_WEBHOOK_TOKEN"] = "test-webhook-token-with-32-characters"
os.environ["ASAAS_RECONCILIATION_SECRET"] = "test-reconciliation-secret-32-characters"
