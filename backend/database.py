import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Carrega as variáveis do arquivo .env
load_dotenv()

SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL") or "sqlite:///./test.db"
# Segurança: Se a URL do pooler tiver :6543 (Supabase Pooler), adiciona o parâmetro automaticamente
if SQLALCHEMY_DATABASE_URL and ":6543" in SQLALCHEMY_DATABASE_URL:
    SQLALCHEMY_DATABASE_URL += "?prepare_threshold=0"

# Cria o "motor" de conexão com o banco
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Cria a fábrica de sessões (cada requisição vai usar uma sessão)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para criarmos as tabelas depois
Base = declarative_base()


# Função para injetar o banco de dados nas rotas
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
