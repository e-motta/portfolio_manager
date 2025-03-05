from sqlmodel import Session, create_engine, select

from alembic import command
from alembic.config import Config
from app import crud
from app.core.config import settings
from app.models import User, UserCreate

engine = create_engine(settings.DATABASE_URL)


def run_migrations() -> None:
    alembic_cfg = Config("alembic.ini")
    command.upgrade(alembic_cfg, "head")


def init_db(session: Session) -> None:
    user = session.exec(
        select(User).where(User.username == settings.FIRST_SUPERUSER_USERNAME)
    ).first()
    if not user:
        user_in = UserCreate(
            username=settings.FIRST_SUPERUSER_USERNAME,
            email=settings.FIRST_SUPERUSER_EMAIL,
            first_name=settings.FIRST_SUPERUSER_FIRST_NAME,
            last_name=settings.FIRST_SUPERUSER_LAST_NAME,
            password=settings.FIRST_SUPERUSER_PASSWORD,
            is_admin=True,
        )
        user = crud.users.create(session=session, user_in=user_in)


if __name__ == "__main__":
    with Session(engine) as session:
        init_db(session)
