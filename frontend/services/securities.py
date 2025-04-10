from typing import Any

from repositories.securities import SecuritiesRepository
from utils import format_currency, format_number, format_percentage


class SecuritiesService:
    def __init__(self, repository: SecuritiesRepository):
        self.repository = repository

    def get_account_securities(self, account_id: str) -> list[dict[str, Any]]:
        """Get all securities for a specific account with formatted data."""
        securities = self.repository.fetch_securities(account_id)
        return self._transform_securities_data(securities)

    def create_security(
        self, account_id: str, symbol: str, name: str, target_allocation: float
    ) -> dict[str, Any]:
        """Create a new security for an account."""
        security_data = {
            "symbol": symbol,
            "name": name,
            "target_allocation": round(target_allocation / 100, 8),
        }
        return self.repository.create_security(account_id, security_data)

    def update_security(
        self, account_id: str, security_id: str, target_allocation: float
    ) -> dict[str, Any]:
        """Update a security's target allocation."""
        security_data = {"target_allocation": round(target_allocation / 100, 8)}
        return self.repository.update_security(account_id, security_id, security_data)

    def delete_security(self, account_id: str, security_id: str) -> dict[str, Any]:
        """Delete a security from an account."""
        return self.repository.delete_security(account_id, security_id)

    def _transform_securities_data(
        self, securities: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """Transform securities data for display."""
        return [
            {
                "Symbol": security["symbol"],
                "Target Allocation": format_percentage(security["target_allocation"]),
                "Cost Basis": format_currency(security["cost_basis"]),
                "Position": format_number(security["position"]),
                "Average Price": format_currency(security["average_price"]),
                "Latest Price": format_currency(security["latest_price"]),
                "Current Value": format_currency(
                    float(security["latest_price"]) * float(security["position"])
                ),
                "id": security["id"],
            }
            for security in securities
        ]
