from sqlalchemy import func
from sqlmodel import Session, select

from app.api.utils import get_password_hash
from app.models.users import User, UserCreate, UserRegister, UserUpdate


def fetch_all(session: Session):
    statement = select(User)
    users = session.exec(statement).all()
    return users


def fetch_active(session: Session):
    statement = select(User).where(User.deleted_at == None)
    users = session.exec(statement).all()
    return users


def create(session: Session, user_in: UserCreate):
    db_obj = User.model_validate(
        user_in, update={"password_hash": get_password_hash(user_in.password)}
    )
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj


def register(session: Session, user_in: UserRegister):
    user_data = UserCreate.model_validate(user_in)
    user = create(session, user_data)
    return user


def update(session: Session, user_db: User, user_in: UserUpdate):
    user_data = user_in.model_dump(exclude_unset=True)
    extra = {}
    if user_in.password:
        extra.update({"password_hash": get_password_hash(user_in.password)})
    user_db.sqlmodel_update(user_data, update=extra)
    session.add(user_db)
    session.commit()
    session.refresh(user_db)


def hard_delete(session: Session, user_db: User):
    session.delete(user_db)
    session.commit()


def soft_delete(session: Session, user_db: User):
    user_db.sqlmodel_update({"deleted_at": func.now()})
    session.add(user_db)
    session.commit()
    session.refresh(user_db)


def recover(session: Session, user_db: User):
    user_db.sqlmodel_update({"deleted_at": None})
    session.add(user_db)
    session.commit()
    session.refresh(user_db)
