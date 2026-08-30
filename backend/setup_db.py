"""Prepare the database by applying the complete Alembic history."""

from pathlib import Path

from alembic import command
from alembic.config import Config


def upgrade_database() -> None:
    backend_dir = Path(__file__).resolve().parent
    config = Config(backend_dir / "alembic.ini")
    config.set_main_option("script_location", str(backend_dir / "alembic"))
    command.upgrade(config, "head")


if __name__ == "__main__":
    print("Aplicando migrations do banco de dados...")
    upgrade_database()
    print("Banco atualizado com sucesso.")
