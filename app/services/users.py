from sqlalchemy import func
from sqlmodel import select, Session

from app.api.utils import get_password_hash
from app.models.users import User, UserCreate, UserUpdate


def fetch(session: Session, include_deleted: bool = False):
    statement = select(User)

    if not include_deleted:
        statement = statement.where(User.deleted_at == None)

    users = session.exec(statement)
    return users


def create(session: Session, user_in: UserCreate):
    db_obj = User.model_validate(
        user_in, update={"password_hash": get_password_hash(user_in.password)}
    )
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj


def update(session: Session, user_db: User, user_in: UserUpdate):
    user_data = user_in.model_dump(exclude_unset=True)
    extra = {}
    if user_in.password:
        extra.update({"password_hash": get_password_hash(user_in.password)})
    user_db.sqlmodel_update(user_data, update=extra)
    session.add(user_db)
    session.commit()
    session.refresh(user_db)
    return user_db


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
