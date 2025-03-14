from decimal import Decimal

import pytest
from sqlmodel import Session

from app.models.transactions import TransactionType
from app.services import process_transaction, reprocess_all_transactions
from app.tests.utils import (
    create_account,
    create_stock,
    create_transaction,
    create_user,
    delete_transaction,
)


def test_buy_initial_stock(session: Session):
    user = create_user(session)
    account = create_account(session, current_user=user)
    stock = create_stock(session, account=account)

    transaction_1 = create_transaction(
        session,
        account=account,
        stock=stock,
        type=TransactionType.BUY,
        quantity=Decimal("10"),
        price=Decimal("100"),
    )

    assert stock.cost_basis == 0
    assert stock.average_price == 0
    assert stock.position == 0

    process_transaction(session, account, stock, transaction_1)

    assert stock.cost_basis == 1000
    assert stock.average_price == 100
    assert stock.position == 10


def test_buy_at_different_price(session: Session):
    user = create_user(session)
    account = create_account(session, current_user=user)
    stock = create_stock(session, account=account)

    # Initial purchase
    transaction_1 = create_transaction(
        session,
        account=account,
        stock=stock,
        type=TransactionType.BUY,
        quantity=Decimal("10"),
        price=Decimal("100"),
    )
    process_transaction(session, account, stock, transaction_1)

    # Second purchase at a different price
    transaction_2 = create_transaction(
        session,
        account=account,
        stock=stock,
        type=TransactionType.BUY,
        quantity=Decimal("5"),
        price=Decimal("200"),
    )

    process_transaction(session, account, stock, transaction_2)

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
    stock = create_stock(session, account=account)

    # Initial and second purchase
    transaction_1 = create_transaction(
        session,
        account=account,
        stock=stock,
        type=TransactionType.BUY,
        quantity=Decimal("10"),
        price=Decimal("100"),
    )
    process_transaction(session, account, stock, transaction_1)

    transaction_2 = create_transaction(
        session,
        account=account,
        stock=stock,
        type=TransactionType.BUY,
        quantity=Decimal("5"),
        price=Decimal("200"),
    )
    process_transaction(session, account, stock, transaction_2)

    # Selling some stock (FIFO applies)
    transaction_3 = create_transaction(
        session,
        account=account,
        stock=stock,
        type=TransactionType.SELL,
        quantity=Decimal("5"),
        price=Decimal("300"),
    )

    process_transaction(session, account, stock, transaction_3)

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
    stock = create_stock(session, account=account)

    # Initial and second purchase
    transaction_1 = create_transaction(
        session,
        account=account,
        stock=stock,
        type=TransactionType.BUY,
        quantity=Decimal("5"),
        price=Decimal("100"),
    )
    process_transaction(session, account, stock, transaction_1)

    transaction_2 = create_transaction(
        session,
        account=account,
        stock=stock,
        type=TransactionType.BUY,
        quantity=Decimal("5"),
        price=Decimal("200"),
    )
    process_transaction(session, account, stock, transaction_2)

    # Selling full FIFO lot and part of the next one
    transaction_3 = create_transaction(
        session,
        account=account,
        stock=stock,
        type=TransactionType.SELL,
        quantity=Decimal("7"),
        price=Decimal("300"),
    )

    process_transaction(session, account, stock, transaction_3)

    assert stock.cost_basis == 600  # (5 * 200) - (5 * 100) - (2 * 200)
    assert stock.position == 3  # 5 + 5 - 7
    assert stock.average_price == 200  # 600 / 3
    assert stock.fifo_lots == [
        ["3.0000", "200.00"],  # Remaining from second buy
    ]


def test_sell_all_remaining_stock(session: Session):
    user = create_user(session)
    account = create_account(session, current_user=user)
    stock = create_stock(session, account=account)

    # Initial and second purchase
    transaction_1 = create_transaction(
        session,
        account=account,
        stock=stock,
        type=TransactionType.BUY,
        quantity=Decimal("10"),
        price=Decimal("100"),
    )
    process_transaction(session, account, stock, transaction_1)

    transaction_2 = create_transaction(
        session,
        account=account,
        stock=stock,
        type=TransactionType.BUY,
        quantity=Decimal("5"),
        price=Decimal("200"),
    )
    process_transaction(session, account, stock, transaction_2)

    # Selling all remaining stock
    transaction_5 = create_transaction(
        session,
        account=account,
        stock=stock,
        type=TransactionType.SELL,
        quantity=Decimal("15"),
        price=Decimal("300"),
    )

    process_transaction(session, account, stock, transaction_5)

    assert stock.cost_basis == 0  # All stock sold
    assert stock.position == 0
    assert stock.average_price == 0
    assert stock.fifo_lots == []  # Empty FIFO queue


def test_sell_more_than_available_stock(session: Session):
    user = create_user(session)
    account = create_account(session, current_user=user)
    stock = create_stock(session, account=account)

    # Initial purchase
    transaction_1 = create_transaction(
        session,
        account=account,
        stock=stock,
        type=TransactionType.BUY,
        quantity=Decimal("10"),
        price=Decimal("100"),
    )
    process_transaction(session, account, stock, transaction_1)

    # Attempting to sell more than available stock (should fail)
    transaction_6 = create_transaction(
        session,
        account=account,
        stock=stock,
        type=TransactionType.SELL,
        quantity=Decimal("20"),
        price=Decimal("300"),
    )

    with pytest.raises(ValueError):
        process_transaction(session, account, stock, transaction_6)


def test_buy_after_selling_all_stock(session: Session):
    user = create_user(session)
    account = create_account(session, current_user=user)
    stock = create_stock(session, account=account)

    # Initial and second purchase
    transaction_1 = create_transaction(
        session,
        account=account,
        stock=stock,
        type=TransactionType.BUY,
        quantity=Decimal("10"),
        price=Decimal("100"),
    )
    process_transaction(session, account, stock, transaction_1)

    transaction_2 = create_transaction(
        session,
        account=account,
        stock=stock,
        type=TransactionType.BUY,
        quantity=Decimal("5"),
        price=Decimal("200"),
    )
    process_transaction(session, account, stock, transaction_2)

    # Selling all stock
    transaction_5 = create_transaction(
        session,
        account=account,
        stock=stock,
        type=TransactionType.SELL,
        quantity=Decimal("15"),
        price=Decimal("300"),
    )
    process_transaction(session, account, stock, transaction_5)

    # Buying new stock after selling all
    transaction_7 = create_transaction(
        session,
        account=account,
        stock=stock,
        type=TransactionType.BUY,
        quantity=Decimal("4"),
        price=Decimal("250"),
    )

    process_transaction(session, account, stock, transaction_7)

    assert stock.cost_basis == 1000
    assert stock.position == 4
    assert stock.average_price == 250
    assert stock.fifo_lots == [
        ["4.0000", "250.00"],
    ]


def test_buy_transaction_exceeds_buying_power(session: Session):
    user = create_user(session)
    account = create_account(session, current_user=user, buying_power=Decimal("1000"))
    stock = create_stock(session, account=account)

    # Attempt to buy more than the available buying power allows
    transaction = create_transaction(
        session,
        account=account,
        stock=stock,
        type=TransactionType.BUY,
        quantity=Decimal("10"),
        price=Decimal("200"),  # Total cost = 10 * 200 = 2000 (exceeds buying power)
    )

    with pytest.raises(ValueError):
        process_transaction(session, account, stock, transaction)

    # Ensure the stock and account remain unchanged
    assert stock.cost_basis == 0
    assert stock.average_price == 0
    assert stock.position == 0
    assert stock.fifo_lots == []  # Should still be empty
    assert account.buying_power == Decimal("1000")  # No change in buying power


def test_buy_transaction_subtracts_from_buying_power(session: Session):
    user = create_user(session)
    account = create_account(session, current_user=user, buying_power=Decimal("10000"))
    stock = create_stock(session, account=account)

    transaction = create_transaction(
        session,
        account=account,
        stock=stock,
        type=TransactionType.BUY,
        quantity=Decimal("5"),
        price=Decimal("100"),
    )

    process_transaction(session, account, stock, transaction)

    assert account.buying_power == Decimal("9500")  # 10000 - 500 = 9500


def test_sell_transaction_adds_to_buying_power(session: Session):
    user = create_user(session)
    account = create_account(session, current_user=user, buying_power=Decimal("10000"))
    stock = create_stock(session, account=account)

    transaction_1 = create_transaction(
        session,
        account=account,
        stock=stock,
        type=TransactionType.BUY,
        quantity=Decimal("5"),
        price=Decimal("100"),
    )
    process_transaction(session, account, stock, transaction_1)

    transaction_2 = create_transaction(
        session,
        account=account,
        stock=stock,
        type=TransactionType.SELL,
        quantity=Decimal("3"),
        price=Decimal("150"),
    )

    process_transaction(session, account, stock, transaction_2)

    assert account.buying_power == Decimal("9950")  # 10000 - 500 + 450 = 9500


# def test_delete_buy_transaction(session: Session):
#     user = create_user(session)
#     account = create_account(session, current_user=user, buying_power=Decimal("10000"))
#     stock = create_stock(session, account=account)

#     transaction = create_transaction(
#         session,
#         account=account,
#         stock=stock,
#         type=TransactionType.BUY,
#         quantity=Decimal("5"),
#         price=Decimal("100"),
#     )

#     process_transaction(session, account, stock, transaction)

#     assert account.buying_power == Decimal("9500")  # 10000 - (5 * 100)
#     assert stock.position == Decimal("5")
#     assert stock.cost_basis == Decimal("500")
#     assert stock.fifo_lots == [
#         ["5.0000", "100.00"],
#     ]

#     delete_transaction(session, transaction=transaction)
#     reprocess_all_transactions(session, account, stock)

#     assert account.buying_power == Decimal("10000")
#     assert stock.position == Decimal("0")
#     assert stock.cost_basis == Decimal("0")
#     assert stock.fifo_lots == []


# def test_delete_previous_buy_transaction(session: Session):
#     user = create_user(session)
#     account = create_account(session, current_user=user, buying_power=Decimal("10000"))
#     stock = create_stock(session, account=account)

#     transaction_1 = create_transaction(
#         session,
#         account=account,
#         stock=stock,
#         type=TransactionType.BUY,
#         quantity=Decimal("5"),
#         price=Decimal("100"),
#     )

#     process_transaction(session, account, stock, transaction_1)

#     assert account.buying_power == Decimal("9500")  # 10000 - (5 * 100)
#     assert stock.position == Decimal("5")
#     assert stock.cost_basis == Decimal("500")
#     assert stock.fifo_lots == [
#         ["5.0000", "100.00"],
#     ]

#     transaction_2 = create_transaction(
#         session,
#         account=account,
#         stock=stock,
#         type=TransactionType.BUY,
#         quantity=Decimal("10"),
#         price=Decimal("200"),
#     )

#     process_transaction(session, account, stock, transaction_2)

#     delete_transaction(session, transaction=transaction_1)
#     reprocess_all_transactions(session, account, stock)

#     assert account.buying_power == Decimal("8000")
#     assert stock.position == Decimal("10")
#     assert stock.cost_basis == Decimal("2000")
#     assert stock.fifo_lots == [
#         ["10.0000", "200.00"],
#     ]


# def test_delete_sell_transaction(session: Session):
#     user = create_user(session)
#     account = create_account(session, current_user=user, buying_power=Decimal("10000"))
#     stock = create_stock(session, account=account)

#     # Buy first to have shares available for selling
#     transaction_1 = create_transaction(
#         session,
#         account=account,
#         stock=stock,
#         type=TransactionType.BUY,
#         quantity=Decimal("5"),
#         price=Decimal("100"),
#     )
#     process_transaction(session, account, stock, transaction_1)

#     # Sell some shares
#     transaction_2 = create_transaction(
#         session,
#         account=account,
#         stock=stock,
#         type=TransactionType.SELL,
#         quantity=Decimal("3"),
#         price=Decimal("150"),
#     )
#     process_transaction(session, account, stock, transaction_2)

#     # Assert initial state after selling
#     assert account.buying_power == Decimal("9950")  # 10000 - 500 + 450
#     assert stock.position == Decimal("2")  # 5 - 3
#     assert stock.cost_basis == Decimal("200")
#     assert stock.fifo_lots == [["2.0000", "100.00"]]

#     delete_transaction(session, transaction=transaction_2)
#     reprocess_all_transactions(session, account, stock)

#     # Assert account and stock state after undoing
#     assert account.buying_power == Decimal("9500")  # 10000 - 500
#     assert stock.position == Decimal("5")
#     assert stock.cost_basis == Decimal("500")
#     assert stock.fifo_lots == [["5.0000", "100.00"]]
