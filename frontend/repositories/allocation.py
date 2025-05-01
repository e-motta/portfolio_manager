
from api_client import APIClient


class AllocationRepository:
    def __init__(self, client: APIClient):
        self.client = client

    def create_allocation_plan(
        self,
        account_id: str,
        new_investment: float,
        allocation_strategy: str | None = None,
    ) -> dict:
        """Create an allocation plan for a specific account."""
        payload: dict[str, str | float] = {
            "new_investment": new_investment,
        }

        if allocation_strategy:
            payload["allocation_strategy"] = allocation_strategy

        response = self.client.post(f"/accounts/{account_id}/plan", json=payload)
        return response
