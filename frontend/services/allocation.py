
from repositories.allocation import AllocationRepository
from results import ResultMultiple
from utils import format_currency, format_percentage


class AllocationService:
    def __init__(self, repository: AllocationRepository):
        self.repository = repository

    def create_allocation_plan(
        self,
        account_id: str,
        new_investment: float,
        allocation_strategy: str | None = None,
    ) -> ResultMultiple:
        """Create an allocation plan for an account."""
        response = self.repository.create_allocation_plan(
            account_id, new_investment, allocation_strategy
        )

        data = self._transform_allocation_data(response["data"])
        return ResultMultiple(data=data, message=response["message"])

    def _transform_allocation_data(self, allocation_items: list[dict]) -> list[dict]:
        """Transform allocation plan data for display."""
        return [
            {
                "Security ID": item["security_id"],
                "Symbol": item["symbol"],
                "Current Value": format_currency(item["current_value"]),
                "Target Allocation": format_percentage(
                    item["effective_target_allocation"]
                ),
                "Current Weight": format_percentage(item["current_weight"]),
                "Ideal Value": format_currency(item["ideal_value"]),
                "Needed Investment": format_currency(item["needed_investment"]),
            }
            for item in allocation_items
        ]
