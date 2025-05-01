
from repositories.trades import TradesRepository
from results import ResultMultiple, ResultSingle
from utils import format_currency, format_number


class TradesService:
    def __init__(self, repository: TradesRepository):
        self.repository = repository

    def get_account_trades(self, account_id: str) -> ResultMultiple:
        """Get all trades for a specific account with formatted data."""
        response = self.repository.fetch_trades(account_id)
        data = self._transform_trades_data(response["data"])
        return ResultMultiple(data=data, message=response["message"])

    def create_trade(
        self,
        account_id: str,
        trade_type: str,
        security_id: str,
        quantity: float,
        price: float,
    ) -> ResultSingle:
        """Create a new trade for an account."""
        trade_data = {
            "type": trade_type,
            "security_id": security_id,
            "quantity": quantity,
            "price": price,
        }
        response = self.repository.create_trade(account_id, trade_data)
        return ResultSingle(data=response["data"], message=response["message"])

    def delete_trade(self, account_id: str, trade_id: str) -> ResultSingle:
        """Delete a trade from an account."""
        response = self.repository.delete_trade(account_id, trade_id)
        return ResultSingle(data=response["data"], message=response["message"])

    def _transform_trades_data(self, trades: list[dict]) -> list[dict]:
        """Transform trades data for display."""
        return [
            {
                "Date": trade["created_at"].split("T")[0],  # Format date
                "Type": trade["type"].upper(),
                "Security": trade["security_symbol"],
                "Quantity": format_number(trade["quantity"]),
                "Price": format_currency(trade["price"]),
                "Total": format_currency(
                    float(trade["quantity"]) * float(trade["price"])
                ),
                "id": trade["id"],
            }
            for trade in trades
        ]
