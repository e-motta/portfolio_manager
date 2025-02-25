from sqlmodel import select, Session

from app.models import Account, AccountCreate, AccountRead, AccountUpdate, User


def create(session: Session, account_in: AccountCreate, current_user: User):
    account_db = Account.model_validate(account_in, update={"user_id": current_user.id})
    session.add(account_db)
    session.commit()
    session.refresh(account_db)
    return account_db


def get_by_id(session: Session, account_id: int) -> Account | None:
    account_statement = select(Account).where(Account.id == account_id)
    account = session.exec(account_statement).first()
    return account


def update(session: Session, account_db: Account, account_in: AccountUpdate):
    account_data = account_in.model_dump(exclude_unset=True)
    account_db.sqlmodel_update(account_data)
    session.add(account_db)
    session.commit()
    session.refresh(account_db)


def delete(session: Session, account_db: Account):
    session.delete(account_db)
    session.commit()
