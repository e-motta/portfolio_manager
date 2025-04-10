from typing import Any

from repositories.trades import TradesRepository
from utils import format_currency, format_number, format_percentage


class TradesService:
    def __init__(self, repository: TradesRepository):
        self.repository = repository

    def get_account_trades(self, account_id: str) -> list[dict[str, Any]]:
        """Get all trades for a specific account with formatted data."""
        trades = self.repository.fetch_trades(account_id)
        return self._transform_trades_data(trades)

    def create_trade(
        self,
        account_id: str,
        trade_type: str,
        security_id: str,
        quantity: float,
        price: float,
    ) -> dict[str, Any]:
        """Create a new trade for an account."""
        trade_data = {
            "type": trade_type,
            "security_id": security_id,
            "quantity": quantity,
            "price": price,
        }
        return self.repository.create_trade(account_id, trade_data)

    def delete_trade(self, account_id: str, trade_id: str) -> dict[str, Any]:
        """Delete a trade from an account."""
        return self.repository.delete_trade(account_id, trade_id)

    def _transform_trades_data(
        self, trades: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """Transform trades data for display."""
        return [
            {
                "Date": trade["created_at"].split("T")[0],  # Format date
                "Type": trade["type"].upper(),
                "Security ID": trade["security_id"],
                "Quantity": format_number(trade["quantity"]),
                "Price": format_currency(trade["price"]),
                "Total": format_currency(
                    float(trade["quantity"]) * float(trade["price"])
                ),
                "id": trade["id"],
            }
            for trade in trades
        ]
