from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool, create_engine # Adicionado create_engine
from alembic import context

import os
from dotenv import load_dotenv
from database import Base 
import models            

load_dotenv()

# this is the Alembic Config object
config = context.config

# Puxa a URL do .env
sqlalchemy_url = os.getenv("DATABASE_URL")

# Ajusta o prefixo para o SQLAlchemy moderno
if sqlalchemy_url and sqlalchemy_url.startswith("postgres://"):
    sqlalchemy_url = sqlalchemy_url.replace("postgres://", "postgresql://", 1)

# Interpret the config file for Python logging.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# MetaData dos seus modelos
target_metadata = Base.metadata

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    # Passamos a URL diretamente aqui também
    context.configure(
        url=sqlalchemy_url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    # Em vez de usar o config.set_main_option (que causa o erro do %), 
    # nós criamos a engine diretamente usando a URL do .env
    connectable = create_engine(sqlalchemy_url, poolclass=pool.NullPool)

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()