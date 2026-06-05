from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
import os
import requests
from dotenv import load_dotenv
from database import get_db
import models

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY") # Adicionado

security_scheme = HTTPBearer()

# Função para buscar a chave pública (JWKS) no Supabase dinamicamente
def get_supabase_public_key(kid: str):
    # URL oficial do padrão OIDC para buscar chaves públicas
    jwks_url = f"{SUPABASE_URL}/auth/v1/.well-known/jwks.json"
    
    # O Supabase exige a apikey (anon key) no cabeçalho para não bloquear com 401!
    headers = {
        "apikey": SUPABASE_ANON_KEY
    }
    
    try:
        response = requests.get(jwks_url, headers=headers)
        response.raise_for_status()
        jwks = response.json()
        
        # Procura a chave que corresponde ao ID (kid) do token que o usuário enviou
        for key in jwks["keys"]:
            if key["kid"] == kid:
                return key 
                
    except Exception as e:
        print(f"🔴 Erro ao buscar JWKS no Supabase: {e}")
        raise HTTPException(status_code=500, detail="Erro ao buscar chaves de autenticação no provedor")
    
    raise HTTPException(status_code=401, detail="Chave pública não encontrada para este token")

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security_scheme)):
    token = credentials.credentials
    
    try:
        # 1. Lê o cabeçalho do token SEM validar a assinatura, só para descobrir o 'kid'
        unverified_header = jwt.get_unverified_header(token)
        kid = unverified_header.get("kid")
        
        if not kid:
            raise HTTPException(status_code=401, detail="Token sem Key ID (kid)")
            
        # 2. Busca a chave pública no Supabase usando o kid
        public_key = get_supabase_public_key(kid)
        
        # 3. Valida o token usando a chave pública e o algoritmo ES256
        payload = jwt.decode(
            token, 
            public_key, 
            algorithms=["ES256"], 
            options={"verify_aud": False}
        )
        
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido: subject ausente.",
            )
            
        return payload

    except JWTError as e:
        print(f"🔴 ERRO JWT DETALHADO: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Não foi possível validar as credenciais.",
            headers={"WWW-Authenticate": "Bearer"},
        )

def get_current_user(payload: dict = Depends(verify_token), db: Session = Depends(get_db)):
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido: subject ausente.",
            )
        
        # Em vez de ler do token, buscamos o perfil do usuário no nosso banco local
        profile = db.query(models.Profile).filter(models.Profile.id == user_id).first()
        
        # Se o usuário logou no Supabase mas nunca sincronizou, ele não tem Profile no nosso banco
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Perfil de usuário não encontrado. Por favor, sincronize seu cadastro."
            )
            
        # Se o perfil existe mas por algum motivo não tem tenant (impossível pelo nosso código, mas seguro fazer)
        if not profile.tenant_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Usuário não está associado a um escritório."
            )

        # Retorna os dados seguros, puxando o tenant_id direto do nosso PostgreSQL
        return {
            "user_id": user_id,
            "email": payload.get("email"),
            "tenant_id": str(profile.tenant_id) # Garantia absoluta de que vem do banco
        }