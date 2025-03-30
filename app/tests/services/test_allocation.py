from decimal import Decimal
from uuid import UUID

import pytest
from fastapi import HTTPException
from sqlmodel import Session

from app.models.accounts import AllocationPlanItem, AllocationStrategy
from app.models.securities import SecurityCreate
from app.services.allocation import AccountManager, validate_target_allocation
from app.tests.utils import (
    create_account,
    create_and_process_ledger,
    create_and_process_trade,
    create_security,
    create_user,
)


@pytest.fixture()
def fetch_prices_mock():
    def fixture(symbols: list[str]) -> dict[str, Decimal]:
        securities = {
            "ONE": Decimal("500"),
            "TWO": Decimal("500"),
        }
        diff = set(symbols).difference(set(securities.keys()))
        if diff:
            raise ValueError(f"Could not fetch price for securities: {diff}")
        return securities

    return fixture


def test_validate_target_allocation(session: Session):
    user = create_user(session)
    account = create_account(session, current_user=user)
    create_security(
        session, account=account, symbol="ONE", target_allocation=Decimal("0.9")
    )
    new_sec_in = SecurityCreate(
        name="Two", symbol="TWO", target_allocation=Decimal("0.1")
    )
    validate_target_allocation(account, new_sec_in.target_allocation)


def test_validate_max_target_allocation_raises(session: Session):
    user = create_user(session)
    account = create_account(session, current_user=user)
    create_security(
        session, account=account, symbol="ONE", target_allocation=Decimal("1")
    )
    new_sec_in = SecurityCreate(
        name="Two", symbol="TWO", target_allocation=Decimal("0.1")
    )

    with pytest.raises(HTTPException):
        validate_target_allocation(account, new_sec_in.target_allocation)


def test_portfolio_get_allocation_plan_negative_needed_investment_becomes_zero(
    session, fetch_prices_mock
):
    user = create_user(session)
    account = create_account(session, current_user=user)
    create_and_process_ledger(session, account=account, amount=Decimal("2000"))
    sec_1 = create_security(
        session,
        account=account,
        symbol="ONE",
        target_allocation=Decimal("0.3"),
    )
    create_and_process_trade(
        session,
        account=account,
        security=sec_1,
        quantity=Decimal("2"),
        price=Decimal("500"),
    )
    sec_2 = create_security(
        session,
        account=account,
        symbol="TWO",
        target_allocation=Decimal("0.7"),
    )
    create_and_process_trade(
        session,
        account=account,
        security=sec_2,
        quantity=Decimal("2"),
        price=Decimal("500"),
    )

    portfolio = AccountManager(session, account, fetch_prices_mock)

    new_investment_amount = Decimal("1000")
    plan = portfolio.get_allocation_plan(new_investment_amount)

    expected_plan = [
        AllocationPlanItem(
            security_id=sec_1.id,
            symbol=sec_1.symbol,
            current_value=Decimal("1000.00000000"),
            effective_target_allocation=Decimal("0.3"),
            ideal_value=Decimal("900.00000000"),
            current_weight=Decimal("0.5"),
            needed_investment=Decimal("0.00000000"),
        ),
        AllocationPlanItem(
            security_id=sec_2.id,
            symbol=sec_2.symbol,
            current_value=Decimal("1000.00000000"),
            effective_target_allocation=Decimal("0.7"),
            ideal_value=Decimal("2100.00000000"),
            current_weight=Decimal("0.5"),
            needed_investment=Decimal("1000.00000000"),
        ),
    ]

    assert plan == expected_plan


def test_portfolio_get_allocation_plan(session, fetch_prices_mock):
    user = create_user(session)
    account = create_account(session, current_user=user)
    create_and_process_ledger(session, account=account, amount=Decimal("2000"))
    sec_1 = create_security(
        session,
        account=account,
        symbol="ONE",
        target_allocation=Decimal("0.3"),
    )
    create_and_process_trade(
        session,
        account=account,
        security=sec_1,
        quantity=Decimal("2"),
        price=Decimal("500"),
    )
    sec_2 = create_security(
        session,
        account=account,
        symbol="TWO",
        target_allocation=Decimal("0.7"),
    )
    create_and_process_trade(
        session,
        account=account,
        security=sec_2,
        quantity=Decimal("2"),
        price=Decimal("500"),
    )

    portfolio = AccountManager(session, account, fetch_prices_mock)

    new_investment_amount = Decimal("3000")
    plan = portfolio.get_allocation_plan(new_investment_amount)

    expected_plan = [
        AllocationPlanItem(
            security_id=sec_1.id,
            symbol=sec_1.symbol,
            current_value=Decimal("1000.00000000"),
            effective_target_allocation=Decimal("0.3"),
            ideal_value=Decimal("1500.00000000"),
            current_weight=Decimal("0.5"),
            needed_investment=Decimal("500.00000000"),
        ),
        AllocationPlanItem(
            security_id=sec_2.id,
            symbol=sec_2.symbol,
            current_value=Decimal("1000.00000000"),
            effective_target_allocation=Decimal("0.7"),
            ideal_value=Decimal("3500.00000000"),
            current_weight=Decimal("0.5"),
            needed_investment=Decimal("2500.00000000"),
        ),
    ]

    assert plan == expected_plan


def test_portfolio_get_allocation_plan_partial_allocation_scale(
    session, fetch_prices_mock
):
    user = create_user(session)
    account = create_account(session, current_user=user)
    create_and_process_ledger(session, account=account, amount=Decimal("2000"))
    sec_1 = create_security(
        session,
        account=account,
        symbol="ONE",
        target_allocation=Decimal("0.3"),
    )
    create_and_process_trade(
        session,
        account=account,
        security=sec_1,
        quantity=Decimal("2"),
        price=Decimal("500"),
    )
    sec_2 = create_security(
        session,
        account=account,
        symbol="TWO",
        target_allocation=Decimal("0.2"),
    )
    create_and_process_trade(
        session,
        account=account,
        security=sec_2,
        quantity=Decimal("2"),
        price=Decimal("500"),
    )

    portfolio = AccountManager(session, account, fetch_prices_mock)

    new_investment_amount = Decimal("3000")
    plan = portfolio.get_allocation_plan(
        new_investment_amount, AllocationStrategy.SCALE
    )

    expected_plan = [
        AllocationPlanItem(
            security_id=sec_1.id,
            symbol=sec_1.symbol,
            current_value=Decimal("1000.00000000"),
            effective_target_allocation=Decimal("0.6"),
            ideal_value=Decimal("3000.00000000"),
            current_weight=Decimal("0.5"),
            needed_investment=Decimal("2000.00000000"),
        ),
        AllocationPlanItem(
            security_id=sec_2.id,
            symbol=sec_2.symbol,
            current_value=Decimal("1000.00000000"),
            effective_target_allocation=Decimal("0.4"),
            ideal_value=Decimal("2000.00000000"),
            current_weight=Decimal("0.5"),
            needed_investment=Decimal("1000.00000000"),
        ),
    ]

    assert plan == expected_plan


def test_portfolio_get_allocation_plan_partial_allocation_fixed(
    session, fetch_prices_mock
):
    user = create_user(session)
    account = create_account(session, current_user=user)
    create_and_process_ledger(session, account=account, amount=Decimal("2000"))
    sec_1 = create_security(
        session,
        account=account,
        symbol="ONE",
        target_allocation=Decimal("0.3"),
    )
    create_and_process_trade(
        session,
        account=account,
        security=sec_1,
        quantity=Decimal("2"),
        price=Decimal("500"),
    )
    sec_2 = create_security(
        session,
        account=account,
        symbol="TWO",
        target_allocation=Decimal("0.2"),
    )
    create_and_process_trade(
        session,
        account=account,
        security=sec_2,
        quantity=Decimal("2"),
        price=Decimal("500"),
    )

    mgr = AccountManager(session, account, fetch_prices_mock)

    new_investment_amount = Decimal("3000")
    plan = mgr.get_allocation_plan(new_investment_amount, AllocationStrategy.FIXED)

    expected_plan = [
        AllocationPlanItem(
            security_id=sec_1.id,
            symbol=sec_1.symbol,
            current_value=Decimal("1000.00000000"),
            effective_target_allocation=Decimal("0.3"),
            ideal_value=Decimal("1500.00000000"),
            current_weight=Decimal("0.5"),
            needed_investment=Decimal("500.00000000"),
        ),
        AllocationPlanItem(
            security_id=sec_2.id,
            symbol=sec_2.symbol,
            current_value=Decimal("1000.00000000"),
            effective_target_allocation=Decimal("0.2"),
            ideal_value=Decimal("1000.00000000"),
            current_weight=Decimal("0.5"),
            needed_investment=Decimal("0.00000000"),
        ),
    ]

    assert plan == expected_plan


def test_portfolio_get_allocation_plan_partial_allocation_no_strategy(
    session, fetch_prices_mock
):
    user = create_user(session)
    account = create_account(session, current_user=user)
    create_and_process_ledger(session, account=account, amount=Decimal("2000"))
    sec_1 = create_security(
        session, account=account, symbol="ONE", target_allocation=Decimal("0.3")
    )
    create_and_process_trade(
        session,
        account=account,
        security=sec_1,
        quantity=Decimal("2"),
        price=Decimal("500"),
    )
    sec_2 = create_security(
        session, account=account, symbol="TWO", target_allocation=Decimal("0.2")
    )
    create_and_process_trade(
        session,
        account=account,
        security=sec_2,
        quantity=Decimal("2"),
        price=Decimal("500"),
    )

    mgr = AccountManager(session, account, fetch_prices_mock)
    new_investment_amount = Decimal("3000")

    with pytest.raises(HTTPException):
        mgr.get_allocation_plan(new_investment_amount)


def test_portfolio_get_allocation_plan_zero_allocation(session, fetch_prices_mock):
    user = create_user(session)
    account = create_account(session, current_user=user)
    create_and_process_ledger(session, account=account, amount=Decimal("2000"))
    sec_1 = create_security(
        session, account=account, symbol="ONE", target_allocation=Decimal("0")
    )
    create_and_process_trade(
        session,
        account=account,
        security=sec_1,
        quantity=Decimal("2"),
        price=Decimal("500"),
    )
    sec_2 = create_security(
        session, account=account, symbol="TWO", target_allocation=Decimal("0")
    )
    create_and_process_trade(
        session,
        account=account,
        security=sec_2,
        quantity=Decimal("2"),
        price=Decimal("500"),
    )

    portfolio = AccountManager(session, account, fetch_prices_mock)
    new_investment_amount = Decimal("3000")

    with pytest.raises(HTTPException):
        portfolio.get_allocation_plan(new_investment_amount)
