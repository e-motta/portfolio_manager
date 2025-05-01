from decimal import Decimal
from uuid import UUID

from fastapi import HTTPException, status
from sqlmodel import Session

from app.constants.messages import Messages
from app.core.logging_config import logger
from app.models.accounts import Account, AllocationPlanItem, AllocationStrategy
from app.models.generic import DetailItem
from app.services.securities import fetch_tickers_info, update_securities_info
from app.utils import round_decimal


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


class AccountManager:
    def __init__(
        self,
        session: Session,
        account: Account,
    ):
        self.session = session
        self.account = account

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
        tickers_info = fetch_tickers_info([s.symbol for s in self.account.securities])
        update_securities_info(
            self.session, self.account.securities, tickers_info, fields=["latest_price"]
        )
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
