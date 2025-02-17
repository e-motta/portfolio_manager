from sqlmodel import Session, create_engine, select

from app.models.users import User

engine = create_engine("sqlite:///./local.db")

# FIRST_SUPERUSER = "superuser"
# FIRST_SUPERUSER_PASSWORD = "password"


def init_db() -> None:
    from sqlmodel import SQLModel

    SQLModel.metadata.create_all(engine)


# user = session.exec(
#     select(User).where(User.email == FIRST_SUPERUSER)
# ).first()
# if not user:
#     user_in = UserCreate(
#         username=FIRST_SUPERUSER,
#         email=FIRST_SUPERUSER,
#         first_name=FIRST_SUPERUSER,
#         last_name=FIRST_SUPERUSER,
#         is_admin=True,
#         password=FIRST_SUPERUSER_PASSWORD,
#     )
#     user = create_user(session=session, user_create=user_in)
