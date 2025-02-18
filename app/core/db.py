from sqlmodel import create_engine
from alembic import command
from alembic.config import Config


engine = create_engine("sqlite:///./local.db")


def run_migrations() -> None:
    alembic_cfg = Config("alembic.ini")
    command.upgrade(alembic_cfg, "head")
