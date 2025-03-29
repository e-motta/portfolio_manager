from collections import deque
from decimal import Decimal
from typing import Callable
from uuid import UUID

from fastapi import HTTPException, status
from sqlmodel import Session

from app import crud
from app.core.logging_config import logger
from app.models.accounts import Account
from app.models.contexts import (
    LedgerTransactionContext,
    TradeTransactionContext,
    TransactionContext,
)
from app.models.generic import DetailItem
from app.models.ledger import Ledger, LedgerType
from app.models.trades import Trade, TradeType
from app.utils import get_average_price


def _buy_update_account(ctx: TradeTransactionContext):
    total = ctx.trade.quantity * ctx.trade.price
    if total > ctx.account.buying_power:
        raise ValueError(
            f"Total value cannot be greater than account buying power for transaction of type '{ctx.trade.type.value}'"
        )
    ctx.account.buying_power -= total


def _sell_update_account(ctx: TradeTransactionContext):
    ctx.account.buying_power += ctx.trade.quantity * ctx.trade.price


def _buy_update_security(ctx: TradeTransactionContext):
    fifo_lots = deque(ctx.security.fifo_lots)

    new_cost_basis = ctx.security.cost_basis + ctx.trade.quantity * ctx.trade.price
    new_position = ctx.security.position + ctx.trade.quantity

    fifo_lots.append((str(ctx.trade.quantity), str(ctx.trade.price)))
    ctx.security.fifo_lots = list(fifo_lots)

    ctx.security.cost_basis = new_cost_basis
    ctx.security.position = new_position
    ctx.security.average_price = get_average_price(new_cost_basis, new_position)


def _sell_update_security(ctx: TradeTransactionContext):
    fifo_lots = deque(ctx.security.fifo_lots)

    if ctx.security.position < ctx.trade.quantity:
        raise ValueError(
            f"Quantity cannot be greater than current position for transaction of type '{ctx.trade.type.value}'"
        )

    sell_quantity = ctx.trade.quantity
    total_cost_removed = Decimal("0")

    # Process FIFO queue
    while sell_quantity > 0 and fifo_lots:
        first_lot_quantity, first_lot_price = fifo_lots[0]
        first_lot_quantity = Decimal(first_lot_quantity)
        first_lot_price = Decimal(first_lot_price)

        if first_lot_quantity <= sell_quantity:
            total_cost_removed += first_lot_quantity * first_lot_price
            sell_quantity -= first_lot_quantity
            fifo_lots.popleft()
        else:
            total_cost_removed += sell_quantity * first_lot_price
            fifo_lots[0] = (
                str(first_lot_quantity - sell_quantity),
                str(first_lot_price),
            )
            sell_quantity = 0
        ctx.security.fifo_lots = list(fifo_lots)

    new_cost_basis = ctx.security.cost_basis - total_cost_removed
    new_position = ctx.security.position - ctx.trade.quantity

    ctx.security.cost_basis = new_cost_basis
    ctx.security.position = new_position
    ctx.security.average_price = get_average_price(new_cost_basis, new_position)


def _deposit_update_account(ctx: LedgerTransactionContext):
    ctx.account.buying_power += ctx.ledger.amount


def _withdrawal_update_account(ctx: LedgerTransactionContext):
    if ctx.account.buying_power < ctx.ledger.amount:
        raise ValueError("Withdrawn amount cannot be greater than account buying power")
    ctx.account.buying_power -= ctx.ledger.amount


ACCOUNT_OPERATIONS: dict[TradeType | LedgerType, Callable] = {
    TradeType.BUY: _buy_update_account,
    TradeType.SELL: _sell_update_account,
    LedgerType.DEPOSIT: _deposit_update_account,
    LedgerType.WITHDRAWAL: _withdrawal_update_account,
}
SECURITY_OPERATIONS: dict[TradeType | LedgerType, Callable] = {
    TradeType.BUY: _buy_update_security,
    TradeType.SELL: _sell_update_security,
}


def process_transaction(ctx: TransactionContext):
    logger.info(f"Processing '{ctx.type.value}' transaction...")
    try:
        if ctx.account is not None:
            ACCOUNT_OPERATIONS[ctx.type](ctx)
            crud.accounts.update(ctx.session, ctx.account)
        if ctx.security is not None:
            SECURITY_OPERATIONS[ctx.type](ctx)
            crud.securities.update(ctx.session, ctx.security)
        logger.info(f"Transaction processed successfully")
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=DetailItem(
                type="cannot_process_transaction",
                loc=[],
                msg=str(e),
            ).model_dump(),
        )


def reprocess_transactions_excluding(
    session: Session, account: Account, exclude: list[UUID]
):
    """Reprocess all transactions for a given account, excluding some by id."""
    logger.info(f"Reprocessing all transactions...")
    account.buying_power = Decimal("0")

    securities = list(crud.securities.get_all_for_account(session, account))
    for s in securities:
        s.position = Decimal("0")
        s.cost_basis = Decimal("0")
        s.average_price = Decimal("0")
        s.fifo_lots = []

    trade_items = list(crud.trades.get_all_for_account(session, account))
    ledger_items = list(crud.ledger.get_all_for_account(session, account))

    transactions = trade_items + ledger_items
    transactions.sort(key=lambda item: item.updated_at)

    for txn in transactions:
        if txn.id in exclude:
            continue
        if isinstance(txn, Trade):
            ctx = TradeTransactionContext(session, account, txn.security, txn.type, txn)
        if isinstance(txn, Ledger):
            ctx = LedgerTransactionContext(session, account, txn.type, txn)
        process_transaction(ctx)

    logger.info(f"All transactions reprocessed successfully")
