from decimal import Decimal

import pytest
from fastapi import HTTPException
from sqlmodel import Session

from app.models.contexts import (
    TradeTransactionContext,
)
from app.models.ledger import LedgerType
from app.models.trades import TradeType
from app.services import process_transaction, reprocess_transactions_excluding
from app.tests.utils import (
    create_account,
    create_and_process_ledger,
    create_stock,
    create_trade,
    create_user,
    delete_trade,
)


def test_buy_initial_stock(session: Session):
    user = create_user(session)
    account = create_account(session, current_user=user)
    create_and_process_ledger(
        session, account=account, type_=LedgerType.DEPOSIT, amount=Decimal("1000")
    )
    stock = create_stock(session, account=account)

    trade_1 = create_trade(
        session,
        account=account,
        stock=stock,
        type_=TradeType.BUY,
        quantity=Decimal("10"),
        price=Decimal("100"),
    )

    assert stock.cost_basis == 0
    assert stock.average_price == 0
    assert stock.position == 0

    ctx = TradeTransactionContext(
        session=session, account=account, stock=stock, trade=trade_1, type=trade_1.type
    )
    process_transaction(ctx)

    assert stock.cost_basis == 1000
    assert stock.average_price == 100
    assert stock.position == 10


def test_buy_at_different_price(session: Session):
    user = create_user(session)
    account = create_account(session, current_user=user)
    create_and_process_ledger(
        session, account=account, type_=LedgerType.DEPOSIT, amount=Decimal("2000")
    )
    stock = create_stock(session, account=account)

    # Initial purchase
    trade_1 = create_trade(
        session,
        account=account,
        stock=stock,
        type_=TradeType.BUY,
        quantity=Decimal("10"),
        price=Decimal("100"),
    )
    ctx_1 = TradeTransactionContext(
        session=session, account=account, stock=stock, trade=trade_1, type=trade_1.type
    )
    process_transaction(ctx_1)

    # Second purchase at a different price
    trade_2 = create_trade(
        session,
        account=account,
        stock=stock,
        type_=TradeType.BUY,
        quantity=Decimal("5"),
        price=Decimal("200"),
    )
    ctx_2 = TradeTransactionContext(
        session=session, account=account, stock=stock, trade=trade_2, type=trade_2.type
    )
    process_transaction(ctx_2)

    assert stock.cost_basis == 2000  # 1000 + (5 * 200)
    assert stock.position == 15  # 10 + 5
    assert stock.average_price == Decimal("133.33333333")  # 2000 / 15
    assert stock.fifo_lots == [
        ["10.0000", "100.00"],  # First lot (from first buy)
        ["5.0000", "200.00"],  # Second lot (from second buy)
    ]


def test_sell_some_stock_fifo_applies(session: Session):
    user = create_user(session)
    account = create_account(session, current_user=user)
    create_and_process_ledger(
        session, account=account, type_=LedgerType.DEPOSIT, amount=Decimal("10000")
    )
    stock = create_stock(session, account=account)

    # Initial and second purchase
    trade_1 = create_trade(
        session,
        account=account,
        stock=stock,
        type_=TradeType.BUY,
        quantity=Decimal("10"),
        price=Decimal("100"),
    )
    ctx_1 = TradeTransactionContext(
        session=session, account=account, stock=stock, trade=trade_1, type=trade_1.type
    )
    process_transaction(ctx_1)

    trade_2 = create_trade(
        session,
        account=account,
        stock=stock,
        type_=TradeType.BUY,
        quantity=Decimal("5"),
        price=Decimal("200"),
    )
    ctx_2 = TradeTransactionContext(
        session=session, account=account, stock=stock, trade=trade_2, type=trade_2.type
    )
    process_transaction(ctx_2)

    # Selling some stock (FIFO applies)
    trade_3 = create_trade(
        session,
        account=account,
        stock=stock,
        type_=TradeType.SELL,
        quantity=Decimal("5"),
        price=Decimal("300"),
    )
    ctx_3 = TradeTransactionContext(
        session=session, account=account, stock=stock, trade=trade_3, type=trade_3.type
    )
    process_transaction(ctx_3)

    assert stock.cost_basis == 1500  # (10 * 100) + (5 * 200) - (5 * 100)
    assert stock.position == 10  # 5 + 5
    assert stock.average_price == 150  # 1500 / 10
    assert stock.fifo_lots == [
        ["5.0000", "100.00"],  # Remaining from first buy
        ["5.0000", "200.00"],  # Second lot still untouched
    ]


def test_sell_full_fifo_lot_and_part_next(session: Session):
    user = create_user(session)
    account = create_account(session, current_user=user)
    create_and_process_ledger(
        session, account=account, type_=LedgerType.DEPOSIT, amount=Decimal("10000")
    )
    stock = create_stock(session, account=account)

    # Initial and second purchase
    trade_1 = create_trade(
        session,
        account=account,
        stock=stock,
        type_=TradeType.BUY,
        quantity=Decimal("5"),
        price=Decimal("100"),
    )
    ctx_1 = TradeTransactionContext(
        session=session, account=account, stock=stock, trade=trade_1, type=trade_1.type
    )
    process_transaction(ctx_1)

    trade_2 = create_trade(
        session,
        account=account,
        stock=stock,
        type_=TradeType.BUY,
        quantity=Decimal("5"),
        price=Decimal("200"),
    )
    ctx_2 = TradeTransactionContext(
        session=session, account=account, stock=stock, trade=trade_2, type=trade_2.type
    )
    process_transaction(ctx_2)

    # Selling full FIFO lot and part of the next one
    trade_3 = create_trade(
        session,
        account=account,
        stock=stock,
        type_=TradeType.SELL,
        quantity=Decimal("7"),
        price=Decimal("300"),
    )
    ctx_3 = TradeTransactionContext(
        session=session, account=account, stock=stock, trade=trade_3, type=trade_3.type
    )
    process_transaction(ctx_3)

    assert stock.cost_basis == 600  # (5 * 200) - (5 * 100) - (2 * 200)
    assert stock.position == 3  # 5 + 5 - 7
    assert stock.average_price == 200  # 600 / 3
    assert stock.fifo_lots == [
        ["3.0000", "200.00"],  # Remaining from second buy
    ]


def test_sell_all_remaining_stock(session: Session):
    user = create_user(session)
    account = create_account(session, current_user=user)
    create_and_process_ledger(
        session, account=account, type_=LedgerType.DEPOSIT, amount=Decimal("10000")
    )
    stock = create_stock(session, account=account)

    # Initial and second purchase
    trade_1 = create_trade(
        session,
        account=account,
        stock=stock,
        type_=TradeType.BUY,
        quantity=Decimal("10"),
        price=Decimal("100"),
    )
    ctx_1 = TradeTransactionContext(
        session=session, account=account, stock=stock, trade=trade_1, type=trade_1.type
    )
    process_transaction(ctx_1)

    trade_2 = create_trade(
        session,
        account=account,
        stock=stock,
        type_=TradeType.BUY,
        quantity=Decimal("5"),
        price=Decimal("200"),
    )
    ctx_2 = TradeTransactionContext(
        session=session, account=account, stock=stock, trade=trade_2, type=trade_2.type
    )
    process_transaction(ctx_2)

    # Selling all remaining stock
    trade_3 = create_trade(
        session,
        account=account,
        stock=stock,
        type_=TradeType.SELL,
        quantity=Decimal("15"),
        price=Decimal("300"),
    )
    ctx_3 = TradeTransactionContext(
        session=session, account=account, stock=stock, trade=trade_3, type=trade_3.type
    )
    process_transaction(ctx_3)

    assert stock.cost_basis == 0  # All stock sold
    assert stock.position == 0
    assert stock.average_price == 0
    assert stock.fifo_lots == []  # Empty FIFO queue


def test_sell_more_than_available_stock(session: Session):
    user = create_user(session)
    account = create_account(session, current_user=user)
    create_and_process_ledger(
        session, account=account, type_=LedgerType.DEPOSIT, amount=Decimal("10000")
    )
    stock = create_stock(session, account=account)

    # Initial purchase
    trade_1 = create_trade(
        session,
        account=account,
        stock=stock,
        type_=TradeType.BUY,
        quantity=Decimal("10"),
        price=Decimal("100"),
    )
    ctx_1 = TradeTransactionContext(
        session=session, account=account, stock=stock, trade=trade_1, type=trade_1.type
    )
    process_transaction(ctx_1)

    # Attempting to sell more than available stock (should fail)
    trade_2 = create_trade(
        session,
        account=account,
        stock=stock,
        type_=TradeType.SELL,
        quantity=Decimal("20"),
        price=Decimal("300"),
    )
    ctx_2 = TradeTransactionContext(
        session=session, account=account, stock=stock, trade=trade_2, type=trade_2.type
    )
    with pytest.raises(HTTPException):
        process_transaction(ctx_2)


def test_buy_after_selling_all_stock(session: Session):
    user = create_user(session)
    account = create_account(session, current_user=user)
    create_and_process_ledger(
        session, account=account, type_=LedgerType.DEPOSIT, amount=Decimal("10000")
    )
    stock = create_stock(session, account=account)

    # Initial and second purchase
    trade_1 = create_trade(
        session,
        account=account,
        stock=stock,
        type_=TradeType.BUY,
        quantity=Decimal("10"),
        price=Decimal("100"),
    )
    ctx_1 = TradeTransactionContext(
        session=session, account=account, stock=stock, trade=trade_1, type=trade_1.type
    )
    process_transaction(ctx_1)

    trade_2 = create_trade(
        session,
        account=account,
        stock=stock,
        type_=TradeType.BUY,
        quantity=Decimal("5"),
        price=Decimal("200"),
    )
    ctx_2 = TradeTransactionContext(
        session=session, account=account, stock=stock, trade=trade_2, type=trade_2.type
    )
    process_transaction(ctx_2)

    # Selling all stock
    trade_3 = create_trade(
        session,
        account=account,
        stock=stock,
        type_=TradeType.SELL,
        quantity=Decimal("15"),
        price=Decimal("300"),
    )
    ctx_3 = TradeTransactionContext(
        session=session, account=account, stock=stock, trade=trade_3, type=trade_3.type
    )
    process_transaction(ctx_3)

    # Buying new stock after selling all
    trade_4 = create_trade(
        session,
        account=account,
        stock=stock,
        type_=TradeType.BUY,
        quantity=Decimal("4"),
        price=Decimal("250"),
    )
    ctx_4 = TradeTransactionContext(
        session=session, account=account, stock=stock, trade=trade_4, type=trade_4.type
    )
    process_transaction(ctx_4)

    assert stock.cost_basis == 1000
    assert stock.position == 4
    assert stock.average_price == 250
    assert stock.fifo_lots == [
        ["4.0000", "250.00"],
    ]


def test_buy_trade_exceeds_buying_power(session: Session):
    user = create_user(session)
    account = create_account(session, current_user=user)
    create_and_process_ledger(
        session, account=account, type_=LedgerType.DEPOSIT, amount=Decimal("1000")
    )
    stock = create_stock(session, account=account)

    trade = create_trade(
        session,
        account=account,
        stock=stock,
        type_=TradeType.BUY,
        quantity=Decimal("10"),
        price=Decimal("200"),  # Total cost = 10 * 200 = 2000 (exceeds buying power)
    )
    ctx = TradeTransactionContext(
        session=session, account=account, stock=stock, trade=trade, type=trade.type
    )
    with pytest.raises(HTTPException):
        process_transaction(ctx)

    assert stock.cost_basis == 0
    assert stock.average_price == 0
    assert stock.position == 0
    assert stock.fifo_lots == []
    assert account.buying_power == Decimal("1000")


def test_buy_trade_subtracts_from_buying_power(session: Session):
    user = create_user(session)
    account = create_account(session, current_user=user)
    create_and_process_ledger(
        session, account=account, type_=LedgerType.DEPOSIT, amount=Decimal("10000")
    )
    stock = create_stock(session, account=account)

    trade = create_trade(
        session,
        account=account,
        stock=stock,
        type_=TradeType.BUY,
        quantity=Decimal("5"),
        price=Decimal("100"),
    )
    ctx = TradeTransactionContext(
        session=session, account=account, stock=stock, trade=trade, type=trade.type
    )
    process_transaction(ctx)

    assert account.buying_power == Decimal("9500")  # 10000 - 500 = 9500


def test_sell_trade_adds_to_buying_power(session: Session):
    user = create_user(session)
    account = create_account(session, current_user=user)
    create_and_process_ledger(
        session, account=account, type_=LedgerType.DEPOSIT, amount=Decimal("10000")
    )
    stock = create_stock(session, account=account)

    trade_1 = create_trade(
        session,
        account=account,
        stock=stock,
        type_=TradeType.BUY,
        quantity=Decimal("5"),
        price=Decimal("100"),
    )
    ctx_1 = TradeTransactionContext(
        session=session, account=account, stock=stock, trade=trade_1, type=trade_1.type
    )
    process_transaction(ctx_1)

    trade_2 = create_trade(
        session,
        account=account,
        stock=stock,
        type_=TradeType.SELL,
        quantity=Decimal("3"),
        price=Decimal("150"),
    )
    ctx_2 = TradeTransactionContext(
        session=session, account=account, stock=stock, trade=trade_2, type=trade_2.type
    )
    process_transaction(ctx_2)

    assert account.buying_power == Decimal("9950")  # 10000 - 500 + 450 = 9500


def test_delete_buy_trade(session: Session):
    user = create_user(session)
    account = create_account(session, current_user=user)
    create_and_process_ledger(
        session, account=account, type_=LedgerType.DEPOSIT, amount=Decimal("10000")
    )
    stock = create_stock(session, account=account)

    trade = create_trade(
        session,
        account=account,
        stock=stock,
        type_=TradeType.BUY,
        quantity=Decimal("5"),
        price=Decimal("100"),
    )

    ctx = TradeTransactionContext(
        session, account=account, stock=stock, trade=trade, type=trade.type
    )
    process_transaction(ctx)

    assert account.buying_power == Decimal("9500")  # 10000 - (5 * 100)
    assert stock.position == Decimal("5")
    assert stock.cost_basis == Decimal("500")
    assert stock.fifo_lots == [
        ["5.0000", "100.00"],
    ]

    reprocess_transactions_excluding(session, account, exclude=[trade.id])
    delete_trade(session, trade=trade)

    assert account.buying_power == Decimal("10000")
    assert stock.position == Decimal("0")
    assert stock.cost_basis == Decimal("0")
    assert stock.fifo_lots == []


def test_delete_previous_buy_trade(session: Session):
    user = create_user(session)
    account = create_account(session, current_user=user)
    create_and_process_ledger(
        session, account=account, type_=LedgerType.DEPOSIT, amount=Decimal("10000")
    )
    stock = create_stock(session, account=account)

    trade_1 = create_trade(
        session,
        account=account,
        stock=stock,
        type_=TradeType.BUY,
        quantity=Decimal("5"),
        price=Decimal("100"),
    )

    ctx = TradeTransactionContext(
        session, account=account, stock=stock, trade=trade_1, type=trade_1.type
    )
    process_transaction(ctx)

    assert account.buying_power == Decimal("9500")  # 10000 - (5 * 100)
    assert stock.position == Decimal("5")
    assert stock.cost_basis == Decimal("500")
    assert stock.fifo_lots == [
        ["5.0000", "100.00"],
    ]

    trade_2 = create_trade(
        session,
        account=account,
        stock=stock,
        type_=TradeType.BUY,
        quantity=Decimal("10"),
        price=Decimal("200"),
    )

    ctx = TradeTransactionContext(
        session, account=account, stock=stock, trade=trade_2, type=trade_2.type
    )
    process_transaction(ctx)

    reprocess_transactions_excluding(session, account, exclude=[trade_1.id])
    delete_trade(session, trade=trade_1)

    assert account.buying_power == Decimal("8000")
    assert stock.position == Decimal("10")
    assert stock.cost_basis == Decimal("2000")
    assert stock.fifo_lots == [
        ["10.0000", "200.00"],
    ]


def test_delete_sell_trade(session: Session):
    user = create_user(session)
    account = create_account(session, current_user=user)
    create_and_process_ledger(
        session, account=account, type_=LedgerType.DEPOSIT, amount=Decimal("10000")
    )
    stock = create_stock(session, account=account)

    trade_1 = create_trade(
        session,
        account=account,
        stock=stock,
        type_=TradeType.BUY,
        quantity=Decimal("5"),
        price=Decimal("100"),
    )
    ctx = TradeTransactionContext(
        session, account=account, stock=stock, trade=trade_1, type=trade_1.type
    )
    process_transaction(ctx)

    trade_2 = create_trade(
        session,
        account=account,
        stock=stock,
        type_=TradeType.SELL,
        quantity=Decimal("3"),
        price=Decimal("150"),
    )
    ctx = TradeTransactionContext(
        session, account=account, stock=stock, trade=trade_2, type=trade_2.type
    )
    process_transaction(ctx)

    assert account.buying_power == Decimal("9950")  # 10000 - 500 + 450
    assert stock.position == Decimal("2")  # 5 - 3
    assert stock.cost_basis == Decimal("200")
    assert stock.fifo_lots == [["2.0000", "100.00"]]

    reprocess_transactions_excluding(session, account, exclude=[trade_2.id])
    delete_trade(session, trade=trade_2)

    assert account.buying_power == Decimal("9500")  # 10000 - 500
    assert stock.position == Decimal("5")
    assert stock.cost_basis == Decimal("500")
    assert stock.fifo_lots == [["5.0000", "100.00"]]


# todo: test service for ledger
def test_deposit(session: Session):
    user = create_user(session)
    account = create_account(session, current_user=user)
    create_and_process_ledger(
        session, account=account, type_=LedgerType.DEPOSIT, amount=Decimal("1000")
    )

    assert account.buying_power == Decimal("1000")


def test_withdraw(session: Session):
    user = create_user(session)
    account = create_account(session, current_user=user)
    create_and_process_ledger(
        session, account=account, type_=LedgerType.DEPOSIT, amount=Decimal("1000")
    )
    create_and_process_ledger(
        session, account=account, type_=LedgerType.WITHDRAWAL, amount=Decimal("600")
    )

    assert account.buying_power == Decimal("400")


def test_deposit_negative_value(session: Session):
    user = create_user(session)
    account = create_account(session, current_user=user)
    with pytest.raises(ValueError):
        create_and_process_ledger(
            session, account=account, type_=LedgerType.DEPOSIT, amount=Decimal("-1000")
        )


def test_withdraw_more_than_buying_power(session: Session):
    user = create_user(session)
    account = create_account(session, current_user=user)
    with pytest.raises(HTTPException):
        create_and_process_ledger(
            session,
            account=account,
            type_=LedgerType.WITHDRAWAL,
            amount=Decimal("1000"),
        )
