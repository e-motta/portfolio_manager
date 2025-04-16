from typing import Any

from repositories.ledger import LedgerRepository
from results import ResultMultiple, ResultSingle
from utils import format_currency


class LedgerService:
    def __init__(self, repository: LedgerRepository):
        self.repository = repository

    def get_account_ledger(self, account_id: str) -> ResultMultiple:
        """Get all ledger for a specific account with formatted data."""
        response = self.repository.fetch_ledger(account_id)
        data = self._transform_ledger_data(response["data"])
        return ResultMultiple(data=data, message=response["message"])

    def create_ledger_entry(
        self,
        account_id: str,
        ledger_entry_type: str,
        amount: float,
    ) -> ResultSingle:
        """Create a new ledger_entry for an account."""
        ledger_entry_data = {
            "type": ledger_entry_type,
            "amount": amount,
        }
        response = self.repository.create_ledger_entry(account_id, ledger_entry_data)
        return ResultSingle(data=response["data"], message=response["message"])

    def delete_ledger_entry(
        self, account_id: str, ledger_entry_id: str
    ) -> ResultSingle:
        """Delete a ledger_entry from an account."""
        response = self.repository.delete_ledger_entry(account_id, ledger_entry_id)
        return ResultSingle(message=response["message"])

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
