from app_config import get_database_url
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Cria o "motor" de conexão com o banco
SQLALCHEMY_DATABASE_URL = get_database_url()
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
