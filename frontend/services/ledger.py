from typing import Any

from repositories.ledger import LedgerRepository
from utils import format_currency


class LedgerService:
    def __init__(self, repository: LedgerRepository):
        self.repository = repository

    def get_account_ledger(self, account_id: str) -> list[dict[str, Any]]:
        """Get all ledger for a specific account with formatted data."""
        ledger = self.repository.fetch_ledger(account_id)
        return self._transform_ledger_data(ledger)

    def create_ledger_entry(
        self,
        account_id: str,
        ledger_entry_type: str,
        amount: float,
    ) -> dict[str, Any]:
        """Create a new ledger_entry for an account."""
        ledger_entry_data = {
            "type": ledger_entry_type,
            "amount": amount,
        }
        return self.repository.create_ledger_entry(account_id, ledger_entry_data)

    def delete_ledger_entry(
        self, account_id: str, ledger_entry_id: str
    ) -> dict[str, Any]:
        """Delete a ledger_entry from an account."""
        return self.repository.delete_ledger_entry(account_id, ledger_entry_id)

    def _transform_ledger_data(
        self, ledger: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """Transform ledger data for display."""
        return [
            {
                "Date": ledger_entry["created_at"].split("T")[0],
                "Type": ledger_entry["type"].upper(),
                "Amount": format_currency(ledger_entry["amount"]),
                "id": ledger_entry["id"],
            }
            for ledger_entry in ledger
        ]
