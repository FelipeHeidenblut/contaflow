import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

# Carrega as variáveis do arquivo .env
load_dotenv()

SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")

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