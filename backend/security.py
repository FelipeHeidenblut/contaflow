import logging
import os
import time

import models
import requests
import jwt

# Imports locais da sua arquitetura
from database import get_db
from dotenv import load_dotenv
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

load_dotenv()

# ==========================================
# CONFIGURAÇÃO DE SEGURANÇA E LOGS
# ==========================================
logger = logging.getLogger("ContaFlow.Security")
security_scheme = HTTPBearer()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")
SUPABASE_JWT_AUDIENCE = os.getenv("SUPABASE_JWT_AUDIENCE", "authenticated")
JWKS_CACHE_TTL_SECONDS = 3600
_jwks_cache = None
_jwks_cached_at = 0.0

# ==========================================
# CAMADA 1: AUTENTICAÇÃO (Validando o JWT)
# ==========================================


def get_cached_jwks(force_refresh: bool = False):
    """
    [OTIMIZAÇÃO] Busca as chaves públicas do Supabase e as guarda na memória (cache).
    Evita gargalo de rede: Impede que o servidor faça requisições HTTP externas
    a cada clique do usuário no painel.
    """
    if not SUPABASE_URL or not SUPABASE_ANON_KEY:
        logger.error("Credenciais do Supabase ausentes no .env")
        raise HTTPException(
            status_code=500, detail="Erro de configuração interna de segurança."
        )

    global _jwks_cache, _jwks_cached_at
    if (
        not force_refresh
        and _jwks_cache is not None
        and time.monotonic() - _jwks_cached_at < JWKS_CACHE_TTL_SECONDS
    ):
        return _jwks_cache

    jwks_url = f"{SUPABASE_URL.rstrip('/')}/auth/v1/.well-known/jwks.json"
    headers = {"apikey": SUPABASE_ANON_KEY}

    try:
        # Timeout de 5s adicionado para evitar que o seu servidor trave se o Supabase cair
        response = requests.get(jwks_url, headers=headers, timeout=5)
        response.raise_for_status()
        _jwks_cache = response.json()
        _jwks_cached_at = time.monotonic()
        return _jwks_cache
    except requests.exceptions.RequestException as e:
        logger.error(f"Erro ao buscar JWKS no Supabase: {e}")
        raise HTTPException(
            status_code=500, detail="Erro ao buscar chaves de autenticação no provedor."
        )


def get_supabase_public_key(kid: str):
    """Procura a chave pública correspondente ao Key ID (kid) dentro do Cache"""
    for force_refresh in (False, True):
        jwks = get_cached_jwks(force_refresh=force_refresh)
        for key in jwks.get("keys", []):
            if key.get("kid") == kid:
                return key

    logger.warning(f"Tentativa de acesso com 'kid' desconhecido: {kid}")
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Chave pública não encontrada para este token.",
    )


def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security_scheme)):
    """Decodifica e valida criptograficamente o token"""
    token = credentials.credentials

    try:
        # 1. Lê o cabeçalho do token SEM validar, só para descobrir o 'kid'
        unverified_header = jwt.get_unverified_header(token)
        kid = unverified_header.get("kid")

        if not kid:
            raise HTTPException(status_code=401, detail="Token sem Key ID (kid).")

        # 2. Busca a chave pública no cache local usando o kid
        public_key = jwt.PyJWK.from_dict(get_supabase_public_key(kid))

        # 3. Valida o token usando a chave pública e o algoritmo ES256
        payload = jwt.decode(
            token,
            public_key,
            algorithms=["ES256"],
            audience=SUPABASE_JWT_AUDIENCE,
            issuer=f"{SUPABASE_URL.rstrip('/')}/auth/v1",
        )

        if not payload.get("sub"):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido: subject ausente.",
            )

        return payload

    except jwt.PyJWTError as e:
        logger.warning(f"Falha na validação do JWT: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Não foi possível validar as credenciais.",
            headers={"WWW-Authenticate": "Bearer"},
        )


def get_current_user(
    payload: dict = Depends(verify_token), db: Session = Depends(get_db)
):
    """Valida a existência do usuário e do escritório no banco de dados local"""
    user_id = payload.get("sub")

    profile = db.query(models.Profile).filter(models.Profile.id == user_id).first()

    # Validações de integridade
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Perfil de usuário não encontrado. Por favor, sincronize seu cadastro.",
        )

    if not profile.tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuário não está associado a um escritório.",
        )

    # Retorna os dados com a flag is_superadmin embutida para a próxima camada
    return {
        "user_id": user_id,
        "email": payload.get("email"),
        "tenant_id": str(profile.tenant_id),
        "role": profile.role,
        "is_superadmin": profile.is_superadmin,
    }


def get_active_user(
    current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)
):
    """Bloqueia mutações quando o escritório está inadimplente."""
    tenant = (
        db.query(models.Tenant)
        .filter(models.Tenant.id == current_user["tenant_id"])
        .first()
    )
    if not tenant:
        raise HTTPException(status_code=403, detail="Escritório não encontrado.")
    if tenant.status_pagamento == "inadimplente":
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail="Conta bloqueada por inadimplência. Regularize o pagamento para continuar.",
        )
    return current_user


# ==========================================
# CAMADA 2: AUTORIZAÇÃO (Gatekeeper do Backoffice)
# ==========================================


def get_super_admin(current_user: dict = Depends(get_current_user)):
    """
    Dependência de validação RBAC de nível global.
    Permite a passagem apenas de usuários marcados como is_superadmin = True no banco.
    """
    # Como a função 'get_current_user' já buscou a flag do banco de dados,
    # não precisamos fazer uma nova requisição ao PostgreSQL aqui.
    # Isso economiza I/O e melhora a velocidade da API.

    if not current_user.get("is_superadmin"):
        logger.warning(
            f"Acesso negado ao Backoffice. User ID: {current_user.get('user_id')}"
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado. Área restrita aos administradores do SaaS.",
        )

    return current_user
