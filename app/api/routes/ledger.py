from fastapi import APIRouter, Depends, status

from app import crud
from app.api.dependencies import (
    CurrentUserDepAnnotated,
    SessionDepAnnotated,
    get_account_or_404,
    get_ledger_item_or_404,
)
from app.api.utils import verify_ownership_or_403
from app.core.config import settings
from app.models.accounts import Account
from app.models.contexts import LedgerTransactionContext
from app.models.generic import Meta, ResponseMultiple, ResponseSingle
from app.models.ledger import (
    Ledger,
    LedgerCreate,
    LedgerRead,
)
from app.services.transactions import (
    process_transaction,
    reprocess_transactions_excluding,
)
from app.constants.messages import Messages

router = APIRouter(
    prefix=f"/{settings.ACCOUNTS_ROUTE_STR}/{{account_id}}/{settings.LEDGER_ROUTE_STR}",
    tags=[settings.LEDGER_ROUTE_STR],
)


@router.get("/", response_model=ResponseMultiple[LedgerRead])
def read_ledger_list(
    current_user: CurrentUserDepAnnotated,
    account_db: Account = Depends(get_account_or_404),
):
    verify_ownership_or_403(account_db.user_id, current_user.id, current_user.is_admin)
    return ResponseMultiple(
        data=account_db.ledger, meta=Meta(count=len(account_db.ledger))
    )


@router.get("/{ledger_id}", response_model=ResponseSingle[LedgerRead])
def read_ledger_detail(
    current_user: CurrentUserDepAnnotated,
    account_db: Account = Depends(get_account_or_404),
    ledger_db: Ledger = Depends(get_ledger_item_or_404),
):
    verify_ownership_or_403(account_db.user_id, current_user.id, current_user.is_admin)
    verify_ownership_or_403(ledger_db.account_id, account_db.id)
    return ResponseSingle(data=ledger_db)


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=ResponseSingle[LedgerRead],
)
def create_ledger_item(
    session: SessionDepAnnotated,
    current_user: CurrentUserDepAnnotated,
    ledger_in: LedgerCreate,
    account_db: Account = Depends(get_account_or_404),
):
    verify_ownership_or_403(account_db.user_id, current_user.id, current_user.is_admin)

    ctx = LedgerTransactionContext(
        session=session,
        account=account_db,
        type=ledger_in.type,
        ledger=ledger_in,
    )
    process_transaction(ctx)

    ledger_db = crud.ledger.create(session, ledger_in, account_db)

    return ResponseSingle(data=ledger_db, message=Messages.Ledger.CREATED)


@router.delete("/{ledger_id}", response_model=ResponseSingle[None])
def delete_ledger_item(
    session: SessionDepAnnotated,
    current_user: CurrentUserDepAnnotated,
    account_db: Account = Depends(get_account_or_404),
    ledger_db: Ledger = Depends(get_ledger_item_or_404),
):
    verify_ownership_or_403(account_db.user_id, current_user.id, current_user.is_admin)
    verify_ownership_or_403(ledger_db.account_id, account_db.id)

    reprocess_transactions_excluding(session, account_db, exclude=[ledger_db.id])

    crud.ledger.delete(session, ledger_db)

    return ResponseSingle(message=Messages.Ledger.DELETED)
