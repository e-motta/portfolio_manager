from typing import Any

from api_client import APIClient


class LedgerRepository:
    def __init__(self, client: APIClient):
        self.client = client

    def fetch_ledger(self, account_id: str) -> dict:
        """Fetch all ledger for a specific account."""
        try:
            response = self.client.get(f"/accounts/{account_id}/ledger")
            return response
        except Exception as e:
            raise Exception(f"Error fetching ledger: {str(e)}")

    def create_ledger_entry(
        self, account_id: str, ledger_entry_data: dict[str, Any]
    ) -> dict[str, Any]:
        """Create a new ledger_entry for a specific account."""
        return self.client.post(
            f"/accounts/{account_id}/ledger", json=ledger_entry_data
        )

    def delete_ledger_entry(
        self, account_id: str, ledger_entry_id: str
    ) -> dict[str, Any]:
        """Delete a ledger_entry from a specific account."""
        return self.client.delete(f"/accounts/{account_id}/ledger/{ledger_entry_id}")
