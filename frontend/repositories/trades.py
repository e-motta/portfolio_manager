from typing import Any

from api_client import APIClient


class TradesRepository:
    def __init__(self, client: APIClient):
        self.client = client

    def fetch_trades(self, account_id: str) -> list[dict[str, Any]]:
        """Fetch all trades for a specific account."""
        try:
            response = self.client.get(f"/accounts/{account_id}/trades")
            return response["data"]
        except Exception:
            return []

    def create_trade(
        self, account_id: str, trade_data: dict[str, Any]
    ) -> dict[str, Any]:
        """Create a new trade for a specific account."""
        return self.client.post(f"/accounts/{account_id}/trades", json=trade_data)

    def delete_trade(self, account_id: str, trade_id: str) -> dict[str, Any]:
        """Delete a trade from a specific account."""
        return self.client.delete(f"/accounts/{account_id}/trades/{trade_id}")
