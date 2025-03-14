from fastapi import APIRouter, Depends, status

from app import crud
from app.api.dependencies import (
    CurrentUserDepAnnotated,
    SessionDepAnnotated,
    get_account_or_404,
)
from app.api.utils import verify_ownership_or_403
from app.core.config import settings
from app.models.accounts import Account, AccountCreate, AccountRead, AccountUpdate
from app.models.generic import Meta, ResponseMultiple, ResponseSingle

router = APIRouter(
    prefix=f"/{settings.ACCOUNTS_ROUTE_STR}", tags=[settings.ACCOUNTS_ROUTE_STR]
)


@router.get("/", response_model=ResponseMultiple[AccountRead])
def read_account_list(
    session: SessionDepAnnotated,
    current_user: CurrentUserDepAnnotated,
):
    if current_user.is_admin:
        accounts, count = crud.accounts.fetch_all(session)
    else:
        accounts = current_user.accounts
        count = len(accounts)
    return ResponseMultiple(data=accounts, meta=Meta(count=count))


@router.get("/{account_id}", response_model=ResponseSingle[AccountRead])
def read_account_detail(
    current_user: CurrentUserDepAnnotated,
    account_db: Account = Depends(get_account_or_404),
):
    verify_ownership_or_403(account_db.user_id, current_user.id, current_user.is_admin)
    return ResponseSingle(data=account_db)


@router.post(
    "/", status_code=status.HTTP_201_CREATED, response_model=ResponseSingle[AccountRead]
)
def create_account(
    session: SessionDepAnnotated,
    current_user: CurrentUserDepAnnotated,
    account_in: AccountCreate,
):
    account_db = crud.accounts.create(session, account_in, current_user)
    return ResponseSingle(data=account_db, message="Account created successfully")


@router.patch("/{account_id}", response_model=ResponseSingle[AccountRead])
def update_account(
    session: SessionDepAnnotated,
    current_user: CurrentUserDepAnnotated,
    account_in: AccountUpdate,
    account_db: Account = Depends(get_account_or_404),
):
    verify_ownership_or_403(account_db.user_id, current_user.id, current_user.is_admin)
    crud.accounts.update(session, account_db, account_in)
    return ResponseSingle(data=account_db, message="Account updated successfully")


@router.delete("/{account_id}", response_model=ResponseSingle[None])
def delete_account(
    session: SessionDepAnnotated,
    current_user: CurrentUserDepAnnotated,
    account_db: Account = Depends(get_account_or_404),
):
    verify_ownership_or_403(account_db.user_id, current_user.id, current_user.is_admin)
    crud.accounts.delete(session, account_db)
    return ResponseSingle(message="Account deleted successfully")
