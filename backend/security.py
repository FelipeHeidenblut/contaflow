import logging
import os
from functools import lru_cache

import models
import requests

# Imports locais da sua arquitetura
from database import get_db
from dotenv import load_dotenv
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

load_dotenv()

# ==========================================
# CONFIGURAÇÃO DE SEGURANÇA E LOGS
# ==========================================
logger = logging.getLogger("ContaFlow.Security")
security_scheme = HTTPBearer()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")

# ==========================================
# CAMADA 1: AUTENTICAÇÃO (Validando o JWT)
# ==========================================


@lru_cache(maxsize=1)
def get_cached_jwks():
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

    jwks_url = f"{SUPABASE_URL}/auth/v1/.well-known/jwks.json"
    headers = {"apikey": SUPABASE_ANON_KEY}

    try:
        # Timeout de 5s adicionado para evitar que o seu servidor trave se o Supabase cair
        response = requests.get(jwks_url, headers=headers, timeout=5)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Erro ao buscar JWKS no Supabase: {e}")
        raise HTTPException(
            status_code=500, detail="Erro ao buscar chaves de autenticação no provedor."
        )


def get_supabase_public_key(kid: str):
    """Procura a chave pública correspondente ao Key ID (kid) dentro do Cache"""
    jwks = get_cached_jwks()

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
        public_key = get_supabase_public_key(kid)

        # 3. Valida o token usando a chave pública e o algoritmo ES256
        payload = jwt.decode(
            token, public_key, algorithms=["ES256"], options={"verify_aud": False}
        )

        if not payload.get("sub"):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido: subject ausente.",
            )

        return payload

    except JWTError as e:
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
        "is_superadmin": profile.is_superadmin,
    }


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
