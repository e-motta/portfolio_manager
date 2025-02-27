from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import select
from typing import Annotated

from app import crud
from app.api.dependencies import (
    CurrentUserDepAnnotated,
    SessionDepAnnotated,
    get_account_or_404,
)
from app.models import Account, AccountCreate, AccountRead, AccountUpdate
from app.api.utils import verify_ownership_or_403

router = APIRouter(prefix="/accounts", tags=["accounts"])


@router.get("/", response_model=list[AccountRead])
def read_account_list(
    session: SessionDepAnnotated,
    current_user: CurrentUserDepAnnotated,
):
    if current_user.is_admin:
        accounts = crud.accounts.fetch_all(session)
    else:
        accounts = current_user.accounts
    return accounts


@router.get("/", response_model=AccountRead)
def read_account_detail(
    current_user: CurrentUserDepAnnotated,
    account_db: Account = Depends(get_account_or_404),
):
    verify_ownership_or_403(account_db.user_id, current_user.id, current_user.is_admin)
    return account_db


@router.post("/", response_model=AccountRead)
def create_account(
    session: SessionDepAnnotated,
    current_user: CurrentUserDepAnnotated,
    account_in: AccountCreate,
):
    account_db = crud.accounts.create(session, account_in, current_user)
    return account_db


@router.patch("/{account_id}", response_model=AccountRead)
def update_account(
    session: SessionDepAnnotated,
    current_user: CurrentUserDepAnnotated,
    account_in: AccountUpdate,
    account_db: Account = Depends(get_account_or_404),
):
    verify_ownership_or_403(account_db.user_id, current_user.id, current_user.is_admin)
    crud.accounts.update(session, account_db, account_in)
    return account_db


@router.delete("/{account_id}")
def delete_account(
    session: SessionDepAnnotated,
    current_user: CurrentUserDepAnnotated,
    account_db: Account = Depends(get_account_or_404),
):
    verify_ownership_or_403(account_db.user_id, current_user.id, current_user.is_admin)
    crud.accounts.delete(session, account_db)
    return {"ok": True}
