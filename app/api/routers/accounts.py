from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlmodel import select

from ...models import Account, AccountCreate, AccountRead, AccountUpdate
from ..dependencies import (
    CurrentUserDepAnnotated,
    IsAdminDep,
    SessionDepAnnotated,
    TokenDep,
    validate_unique_email,
    validate_unique_username,
)

router = APIRouter(prefix="/accounts")


@router.get("/", tags=["accounts"], response_model=AccountRead)
def read_accounts(session: SessionDepAnnotated, current_user: CurrentUserDepAnnotated):
    statement = select(Account).where(Account.user_id == current_user.id)
    accounts = session.exec(statement).all()
    return accounts


@router.post("/", tags=["accounts"], response_model=AccountRead)
def create_account(
    session: SessionDepAnnotated,
    current_user: CurrentUserDepAnnotated,
    account: AccountCreate,
):
    account_db = Account.model_validate(account, update={"user_id": current_user.id})
    session.add(account_db)
    session.commit()
    session.refresh(account_db)
    return account_db
