from fastapi import APIRouter, Depends, status

from app import crud
from app.api.dependencies import (
    CurrentUserDepAnnotated,
    SessionDepAnnotated,
    get_account_or_404,
    get_security_or_404,
)
from app.api.utils import verify_ownership_or_403
from app.constants.messages import Messages
from app.core.config import settings
from app.models.accounts import Account
from app.models.generic import Meta, ResponseMultiple, ResponseSingle
from app.models.securities import Security, SecurityCreate, SecurityRead, SecurityUpdate
from app.services.allocation import validate_target_allocation
from app.services.securities import create_security_with_info

router = APIRouter(
    prefix=f"/{settings.ACCOUNTS_ROUTE_STR}/{{account_id}}/{settings.SECURITIES_ROUTE_STR}",
    tags=[settings.SECURITIES_ROUTE_STR],
)


@router.get("/", response_model=ResponseMultiple[SecurityRead])
def read_security_list(
    current_user: CurrentUserDepAnnotated,
    account_db: Account = Depends(get_account_or_404),
):
    verify_ownership_or_403(account_db.user_id, current_user.id, current_user.is_admin)
    return ResponseMultiple(
        data=account_db.securities, meta=Meta(count=len(account_db.securities))
    )


@router.get("/{security_id}", response_model=ResponseSingle[SecurityRead])
def read_security_detail(
    current_user: CurrentUserDepAnnotated,
    account_db: Account = Depends(get_account_or_404),
    security_db: Security = Depends(get_security_or_404),
):
    verify_ownership_or_403(account_db.user_id, current_user.id, current_user.is_admin)
    verify_ownership_or_403(security_db.account_id, account_db.id)
    return ResponseSingle(data=security_db)


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=ResponseSingle[SecurityRead],
)
def create_security(
    session: SessionDepAnnotated,
    current_user: CurrentUserDepAnnotated,
    security_in: SecurityCreate,
    account_db: Account = Depends(get_account_or_404),
):
    verify_ownership_or_403(account_db.user_id, current_user.id, current_user.is_admin)
    validate_target_allocation(account_db, security_in.target_allocation)
    security_db = create_security_with_info(session, security_in, account_db)
    return ResponseSingle(data=security_db, message=Messages.Security.CREATED)


@router.patch("/{security_id}", response_model=ResponseSingle[SecurityRead])
def update_security(
    session: SessionDepAnnotated,
    current_user: CurrentUserDepAnnotated,
    security_in: SecurityUpdate,
    account_db: Account = Depends(get_account_or_404),
    security_db: Security = Depends(get_security_or_404),
):
    verify_ownership_or_403(account_db.user_id, current_user.id, current_user.is_admin)
    verify_ownership_or_403(security_db.account_id, account_db.id)
    if security_in.target_allocation is not None:
        validate_target_allocation(
            account_db, security_in.target_allocation, exclude=[security_db.id]
        )
    crud.securities.update(session, security_db, security_in)
    return ResponseSingle(data=security_db, message=Messages.Security.UPDATED)


@router.delete("/{security_id}", response_model=ResponseSingle[None])
def delete_security(
    session: SessionDepAnnotated,
    current_user: CurrentUserDepAnnotated,
    account_db: Account = Depends(get_account_or_404),
    security_db: Security = Depends(get_security_or_404),
):
    verify_ownership_or_403(account_db.user_id, current_user.id, current_user.is_admin)
    verify_ownership_or_403(security_db.account_id, account_db.id)
    crud.securities.delete(session, security_db)
    return ResponseSingle(message=Messages.Security.DELETED)
