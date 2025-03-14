from collections import deque
from decimal import Decimal

from sqlmodel import Session

from app import crud
from app.models.accounts import Account
from app.models.contexts import TransactionContext
from app.models.stocks import Stock
from app.models.transactions import TransactionType
from app.utils import get_average_price


def _buy_update_account(ctx: TransactionContext):
    total = ctx.transaction.quantity * ctx.transaction.price
    if total > ctx.account.buying_power:
        raise ValueError(
            f"Total value cannot be greater than account buying power for transaction of type '{ctx.transaction.type.value}'"
        )
    ctx.account.buying_power -= total


def _sell_update_account(ctx: TransactionContext):
    ctx.account.buying_power += ctx.transaction.quantity * ctx.transaction.price


def _buy_update_stock(ctx: TransactionContext):
    fifo_lots = deque(ctx.stock.fifo_lots)

    new_cost_basis = (
        ctx.stock.cost_basis + ctx.transaction.quantity * ctx.transaction.price
    )
    new_position = ctx.stock.position + ctx.transaction.quantity

    fifo_lots.append((str(ctx.transaction.quantity), str(ctx.transaction.price)))
    ctx.stock.fifo_lots = list(fifo_lots)

    ctx.stock.cost_basis = new_cost_basis
    ctx.stock.position = new_position
    ctx.stock.average_price = get_average_price(new_cost_basis, new_position)


def _sell_update_stock(ctx: TransactionContext):
    fifo_lots = deque(ctx.stock.fifo_lots)

    if ctx.stock.position < ctx.transaction.quantity:
        raise ValueError(
            f"Quantity cannot be greater than current position for transaction of type '{ctx.transaction.type.value}'"
        )

    sell_quantity = ctx.transaction.quantity
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
        ctx.stock.fifo_lots = list(fifo_lots)

    new_cost_basis = ctx.stock.cost_basis - total_cost_removed
    new_position = ctx.stock.position - ctx.transaction.quantity

    ctx.stock.cost_basis = new_cost_basis
    ctx.stock.position = new_position
    ctx.stock.average_price = get_average_price(new_cost_basis, new_position)


ACCOUNT_OPERATIONS = {
    TransactionType.BUY: _buy_update_account,
    TransactionType.SELL: _sell_update_account,
}
STOCK_OPERATIONS = {
    TransactionType.BUY: _buy_update_stock,
    TransactionType.SELL: _sell_update_stock,
}


def process_transaction(ctx: TransactionContext):
    ACCOUNT_OPERATIONS[ctx.transaction.type](ctx)
    STOCK_OPERATIONS[ctx.transaction.type](ctx)
    crud.accounts.update(ctx.session, ctx.account)
    crud.stocks.update(ctx.session, ctx.stock)


def reprocess_all_transactions(session: Session, account: Account, stock: Stock):
    """Reprocess all transactions for a given stock.
    This is necessary when a transaction is updated or deleted,
     in order to maintain FIFO order.
    """
    # ! not working yet
    # todo: add transaction types: deposit, withdrawal
    # todo: change Account model: don't allow direct buying_power updates
    # todo: change Account model: update buying_power with transactions

    stock.position = Decimal("0")
    stock.cost_basis = Decimal("0")
    stock.average_price = Decimal("0")
    stock.fifo_lots = []

    transactions = crud.transactions.get_all_for_stock(session, account, stock)

    for txn in transactions:
        ctx = TransactionContext(
            session=session,
            account=account,
            stock=stock,
            transaction=txn,
        )
        process_transaction(ctx)
