from decimal import Decimal
from typing import Callable
from uuid import UUID

import yfinance as yf
from fastapi import HTTPException, status
from sqlmodel import Session

from app import crud
from app.core.logging_config import logger
from app.models.accounts import Account, AllocationPlanItem, AllocationStrategy
from app.models.generic import DetailItem
from app.utils import round_decimal
from app.constants.messages import Messages


def validate_target_allocation(
    account: Account, new_allocation: Decimal, exclude: list[UUID] = []
):
    total_allocations = sum(
        s.target_allocation for s in account.securities if s.id not in exclude
    )
    total_allocations += new_allocation
    if total_allocations > Decimal("1"):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=DetailItem(
                type="max_target_allocation",
                loc=["body", "target_allocation"],
                msg=Messages.Allocation.Validation.MAX_TARGET_ALLOCATION,
            ).model_dump(),
        )


def fetch_prices(symbols: list[str]) -> dict[str, Decimal]:
    logger.info(Messages.Security.FETCHING)
    tickers = yf.Tickers(" ".join(symbols))
    bid_prices = {}

    for symbol in symbols:
        ticker = tickers.tickers.get(symbol)
        if not ticker:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=DetailItem(
                    type="external_service_error",
                    loc=[],
                    msg=Messages.Security.could_not_fetch_symbol(symbol),
                ).model_dump(),
            )

        info = ticker.info
        if "bid" in info and info["bid"] is not None:
            bid_prices[symbol] = Decimal(str(info["bid"]))
        else:
            data = ticker.history(period="1d")
            if not data.empty:
                bid_prices[symbol] = Decimal(str(data["Close"].iloc[-1]))
            else:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail=DetailItem(
                        type="external_service_error",
                        loc=[],
                        msg=Messages.Security.could_not_fetch_symbol(symbol),
                    ).model_dump(),
                )

    return bid_prices


class AccountManager:
    def __init__(
        self,
        session: Session,
        account: Account,
        fetch_prices: Callable[[list[str]], dict[str, Decimal]],
    ):
        self.session = session
        self.account = account
        self.fetch_prices = fetch_prices

    def update_security_prices(self) -> None:
        securities = self.account.securities
        updated_prices = self.fetch_prices([sec.symbol for sec in securities])
        for sec in securities:
            sec.latest_price = updated_prices[sec.symbol]
            crud.securities.update(self.session, sec)

    def get_total_value(self) -> Decimal:
        s = sum([s.latest_price * s.position for s in self.account.securities])
        return Decimal(s)

    def get_total_allocation(self) -> Decimal:
        s = sum([s.target_allocation for s in self.account.securities])
        return Decimal(s)

    def get_allocation_plan(
        self,
        new_investment_amount: Decimal,
        allocation_strategy: AllocationStrategy | None = None,
    ):
        logger.info(Messages.Allocation.CREATING)
        self.update_security_prices()
        current_total_value = self.get_total_value()
        new_total = current_total_value + new_investment_amount
        total_target_allocation = self.get_total_allocation()

        if total_target_allocation == Decimal("0"):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=DetailItem(
                    type="target_allocation_required",
                    loc=[],
                    msg=Messages.Allocation.Validation.AT_LEAST_ONE_GREATER_THAN_ZERO,
                ).model_dump(),
            )

        if total_target_allocation < Decimal("1") and allocation_strategy is None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=DetailItem(
                    type="allocation_strategy_required",
                    loc=[],
                    msg=Messages.Allocation.Validation.ALLOCATION_STRATEGY_REQUIRED,
                ).model_dump(),
            )

        plan = []

        for sec in self.account.securities:
            target_allocation = sec.target_allocation
            if allocation_strategy == AllocationStrategy.SCALE:
                target_allocation = target_allocation / total_target_allocation
            ideal_value = new_total * target_allocation
            current_value = sec.latest_price * sec.position
            needed_investment = max(Decimal("0"), ideal_value - current_value)
            needed_investment = min(needed_investment, new_investment_amount)
            current_weight = (
                current_value / current_total_value
                if current_total_value != 0
                else Decimal("0")
            )

            current_value = round_decimal(current_value, 8)
            target_allocation = round_decimal(target_allocation, 2)
            ideal_value = round_decimal(ideal_value, 8)
            current_weight = round_decimal(current_weight, 2)
            needed_investment = round_decimal(needed_investment, 8)

            plan_item = AllocationPlanItem(
                security_id=sec.id,
                symbol=sec.symbol,
                current_value=current_value,
                effective_target_allocation=target_allocation,
                ideal_value=ideal_value,
                current_weight=current_weight,
                needed_investment=needed_investment,
            )

            plan.append(plan_item)

        logger.info(Messages.Allocation.CREATED)
        return plan
