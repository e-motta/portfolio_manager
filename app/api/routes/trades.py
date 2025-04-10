from fastapi import APIRouter, Depends, status

from app import crud
from app.api.dependencies import (
    CurrentUserDepAnnotated,
    SessionDepAnnotated,
    get_account_or_404,
    get_security_or_404,
    get_trade_or_404,
)
from app.api.utils import verify_ownership_or_403
from app.core.config import settings
from app.models.accounts import Account
from app.models.contexts import TradeTransactionContext
from app.models.generic import Meta, ResponseMultiple, ResponseSingle
from app.models.trades import Trade, TradeCreate, TradeRead
from app.services.transactions import (
    process_transaction,
    reprocess_transactions_excluding,
)

router = APIRouter(
    prefix=f"/{settings.ACCOUNTS_ROUTE_STR}/{{account_id}}/{settings.TRADES_ROUTE_STR}",
    tags=[settings.TRADES_ROUTE_STR],
)


@router.get("/", response_model=ResponseMultiple[TradeRead])
def read_trade_list(
    current_user: CurrentUserDepAnnotated,
    account_db: Account = Depends(get_account_or_404),
):
    verify_ownership_or_403(account_db.user_id, current_user.id, current_user.is_admin)
    return ResponseMultiple(
        data=account_db.trades, meta=Meta(count=len(account_db.trades))
    )


@router.get("/{trade_id}", response_model=ResponseSingle[TradeRead])
def read_trade_detail(
    current_user: CurrentUserDepAnnotated,
    account_db: Account = Depends(get_account_or_404),
    trade_db: Trade = Depends(get_trade_or_404),
):
    verify_ownership_or_403(account_db.user_id, current_user.id, current_user.is_admin)
    verify_ownership_or_403(trade_db.account_id, account_db.id)
    return ResponseSingle(data=trade_db)


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=ResponseSingle[TradeRead],
)
def create_trade(
    session: SessionDepAnnotated,
    current_user: CurrentUserDepAnnotated,
    trade_in: TradeCreate,
    account_db: Account = Depends(get_account_or_404),
):
    verify_ownership_or_403(account_db.user_id, current_user.id, current_user.is_admin)
    security_db = get_security_or_404(session, trade_in.security_id)
    verify_ownership_or_403(security_db.account_id, account_db.id)

    ctx = TradeTransactionContext(
        session=session,
        account=account_db,
        security=security_db,
        trade=trade_in,
        type=trade_in.type,
    )
    process_transaction(ctx)

    trade_db = crud.trades.create(session, trade_in, account_db)

    return ResponseSingle(data=trade_db, message="Transaction created successfully")


@router.delete("/{trade_id}", response_model=ResponseSingle[None])
def delete_trade(
    session: SessionDepAnnotated,
    current_user: CurrentUserDepAnnotated,
    account_db: Account = Depends(get_account_or_404),
    trade_db: Trade = Depends(get_trade_or_404),
):
    verify_ownership_or_403(account_db.user_id, current_user.id, current_user.is_admin)
    verify_ownership_or_403(trade_db.account_id, account_db.id)

    reprocess_transactions_excluding(session, account_db, exclude=[trade_db.id])

    crud.trades.delete(session, trade_db)

    return ResponseSingle(message="Transaction deleted successfully")
