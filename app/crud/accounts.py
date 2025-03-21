from sqlalchemy import func
from sqlmodel import Session, select

from app.models.accounts import Account, AccountCreate, AccountUpdate
from app.models.users import User


def fetch_all(session: Session):
    statement = select(Account)
    accounts = session.exec(statement).all()
    count_statement = select(func.count()).select_from(Account)
    count = session.exec(count_statement).one()
    return accounts, count


def create(session: Session, account_in: AccountCreate, current_user: User):
    account_db = Account.model_validate(account_in, update={"user_id": current_user.id})
    session.add(account_db)
    session.commit()
    session.refresh(account_db)
    return account_db


def update(
    session: Session, account_db: Account, account_in: AccountUpdate | None = None
):
    if account_in is not None:
        account_data = account_in.model_dump(exclude_unset=True)
        account_db.sqlmodel_update(account_data)
    session.add(account_db)
    session.commit()
    session.refresh(account_db)


def delete(session: Session, account_db: Account):
    session.delete(account_db)
    session.commit()
