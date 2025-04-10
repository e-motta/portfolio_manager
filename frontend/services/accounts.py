from repositories.accounts import AccountsRepository


class AccountsService:
    def __init__(self, repository: AccountsRepository):
        self.repository = repository

    def get_all_accounts(self) -> list[dict]:
        """Get all accounts with formatted data."""
        accounts = self.repository.fetch_all()
        return self._transform_accounts_data(accounts)

    def create_account(self, name: str) -> dict:
        """Create a new account."""
        return self.repository.create(name)

    def update_account(self, account_id: str, name: str) -> dict:
        """Update an existing account."""
        return self.repository.update(account_id, name)

    def delete_account(self, account_id: str) -> dict:
        """Delete an account."""
        return self.repository.delete(account_id)

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
