from repositories.accounts import AccountsRepository
from results import ResultMultiple, ResultSingle


class AccountsService:
    def __init__(self, repository: AccountsRepository):
        self.repository = repository

    def get_all_accounts(self) -> ResultMultiple:
        """Get all accounts with formatted data."""
        response = self.repository.fetch_all()
        data = self._transform_accounts_data(response["data"])
        return ResultMultiple(data=data, message=response["message"])

    def create_account(self, name: str) -> ResultSingle:
        """Create a new account."""
        response = self.repository.create(name)
        return ResultSingle(data=response["data"], message=response["message"])

    def update_account(self, account_id: str, name: str) -> ResultSingle:
        """Update an existing account."""
        response = self.repository.update(account_id, name)
        return ResultSingle(data=response["data"], message=response["message"])

    def delete_account(self, account_id: str) -> ResultSingle:
        """Delete an account."""
        response = self.repository.delete(account_id)
        return ResultSingle(message=response["message"])

    def _transform_accounts_data(self, accounts: list[dict]) -> list[dict]:
        """Transform accounts data for display."""
        return [
            {
                "ID": account["id"],
                "Name": account["name"],
                "Buying Power": f"${float(account['buying_power']):.2f}",
            }
            for account in accounts
        ]
