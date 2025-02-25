from fastapi import APIRouter, HTTPException, status
from sqlmodel import select

from app import crud
from app.api.dependencies import CurrentUserDepAnnotated, SessionDepAnnotated
from app.models import Account, AccountCreate, AccountRead, AccountUpdate

router = APIRouter(prefix="/accounts", tags=["accounts"])


@router.get("/", response_model=list[AccountRead])
def read_accounts(session: SessionDepAnnotated, current_user: CurrentUserDepAnnotated):
    statement = select(Account)
    if not current_user.is_admin:
        statement = statement.where(Account.user_id == current_user.id)
    accounts = session.exec(statement).all()
    return accounts


@router.post("/", response_model=AccountRead)
def create_account(
    session: SessionDepAnnotated,
    current_user: CurrentUserDepAnnotated,
    account_in: AccountCreate,
):
    account_db = crud.accounts.create(session, account_in, current_user)
    return account_db


@router.patch("/{id}", response_model=AccountRead)
def update_account(session: SessionDepAnnotated, id: int, account_in: AccountUpdate):
    account_db = crud.accounts.get_by_id(session, id)

    if not account_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Account not found"
        )

    crud.accounts.update(session, account_db, account_in)
    return account_db


@router.delete("/{id}")
def delete_account(session: SessionDepAnnotated, id: int):
    account_db = crud.accounts.get_by_id(session, id)

    if not account_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Account not found"
        )

    crud.accounts.delete(session, account_db)
    return {"ok": True}
