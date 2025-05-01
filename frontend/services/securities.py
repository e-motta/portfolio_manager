from typing import Any

from repositories.securities import SecuritiesRepository
from results import ResultMultiple, ResultSingle
from utils import format_currency, format_number, format_percentage


class SecuritiesService:
    def __init__(self, repository: SecuritiesRepository):
        self.repository = repository

    def get_account_securities(self, account_id: str) -> ResultMultiple:
        """Get all securities for a specific account with formatted data."""
        response = self.repository.fetch_securities(account_id)
        data = self._transform_securities_data(response["data"])
        return ResultMultiple(data=data, message=response["message"])

    def create_security(
        self, account_id: str, symbol: str, target_allocation: float
    ) -> ResultSingle:
        """Create a new security for an account."""
        security_data = {
            "symbol": symbol,
            "target_allocation": round(target_allocation / 100, 8),
        }
        result = self.repository.create_security(account_id, security_data)
        return ResultSingle(data=result["data"], message=result["message"])

    def update_security(
        self, account_id: str, security_id: str, target_allocation: float
    ) -> ResultSingle:
        """Update a security's target allocation."""
        security_data = {"target_allocation": round(target_allocation / 100, 8)}
        result = self.repository.update_security(account_id, security_id, security_data)
        return ResultSingle(data=result["data"], message=result["message"])

    def delete_security(self, account_id: str, security_id: str) -> ResultSingle:
        """Delete a security from an account."""
        result = self.repository.delete_security(account_id, security_id)
        return ResultSingle(message=result["message"])

    def _transform_securities_data(self, securities: list[dict]) -> list[dict]:
        """Transform securities data for display."""
        return [
            {
                "Symbol": security["symbol"],
                "Name": security["name"],
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
