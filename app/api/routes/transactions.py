from fastapi import APIRouter, Depends, status

from app import crud
from app.api.dependencies import (
    CurrentUserDepAnnotated,
    SessionDepAnnotated,
    get_account_or_404,
    get_stock_or_404,
    get_transaction_or_404,
)
from app.api.utils import verify_ownership_or_403
from app.core.config import settings
from app.models.accounts import Account
from app.models.contexts import TransactionContext
from app.models.generic import Meta, ResponseMultiple, ResponseSingle
from app.models.transactions import (
    Transaction,
    TransactionCreate,
    TransactionRead,
)
from app.services import process_transaction

router = APIRouter(
    prefix=f"/{settings.ACCOUNTS_ROUTE_STR}/{{account_id}}/{settings.TRANSACTIONS_ROUTE_STR}",
    tags=[settings.TRANSACTIONS_ROUTE_STR],
)


@router.get("/", response_model=ResponseMultiple[TransactionRead])
def read_transaction_list(
    current_user: CurrentUserDepAnnotated,
    account_db: Account = Depends(get_account_or_404),
):
    verify_ownership_or_403(account_db.user_id, current_user.id, current_user.is_admin)
    return ResponseMultiple(
        data=account_db.transactions, meta=Meta(count=len(account_db.transactions))
    )


@router.get("/{transaction_id}", response_model=ResponseSingle[TransactionRead])
def read_transaction_detail(
    current_user: CurrentUserDepAnnotated,
    account_db: Account = Depends(get_account_or_404),
    transaction_db: Transaction = Depends(get_transaction_or_404),
):
    verify_ownership_or_403(account_db.user_id, current_user.id, current_user.is_admin)
    verify_ownership_or_403(transaction_db.account_id, account_db.id)
    return ResponseSingle(data=transaction_db)


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=ResponseSingle[TransactionRead],
)
def create_transaction(
    session: SessionDepAnnotated,
    current_user: CurrentUserDepAnnotated,
    transaction_in: TransactionCreate,
    account_db: Account = Depends(get_account_or_404),
):
    verify_ownership_or_403(account_db.user_id, current_user.id, current_user.is_admin)
    stock_db = get_stock_or_404(session, transaction_in.stock_id)
    verify_ownership_or_403(stock_db.account_id, account_db.id)
    transaction_db = crud.transactions.create(session, transaction_in, account_db)

    ctx = TransactionContext(
        session=session,
        account=account_db,
        stock=stock_db,
        transaction=transaction_db,
    )
    process_transaction(ctx)

    return ResponseSingle(
        data=transaction_db, message="Transaction created successfully"
    )


@router.delete("/{transaction_id}", response_model=ResponseSingle[None])
def delete_transaction(
    session: SessionDepAnnotated,
    current_user: CurrentUserDepAnnotated,
    account_db: Account = Depends(get_account_or_404),
    transaction_db: Transaction = Depends(get_transaction_or_404),
):
    verify_ownership_or_403(account_db.user_id, current_user.id, current_user.is_admin)
    verify_ownership_or_403(transaction_db.account_id, account_db.id)
    crud.transactions.delete(session, transaction_db)
    return ResponseSingle(message="Transaction deleted successfully")
