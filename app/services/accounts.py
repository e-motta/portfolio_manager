from sqlmodel import Session

from app.models import Account, AccountCreate, AccountRead, AccountUpdate, User


def create(session: Session, account_in: AccountCreate, current_user: User):
    account_db = Account.model_validate(account_in, update={"user_id": current_user.id})
    session.add(account_db)
    session.commit()
    session.refresh(account_db)
    return account_db
