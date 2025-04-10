from api_client import APIClient


class AccountsRepository:
    def __init__(self, client: APIClient):
        self.client = client

    def fetch_all(self) -> list[dict]:
        """Fetch all accounts from the API."""
        try:
            response = self.client.get("/accounts")
            return response["data"]
        except Exception as e:
            raise Exception(f"Error fetching accounts: {str(e)}")

    def create(self, name: str) -> dict:
        """Create a new account."""
        try:
            response = self.client.post(
                "/accounts",
                json={"name": name},
            )
            return response
        except Exception as e:
            raise Exception(f"Error creating account: {str(e)}")

    def update(self, account_id: str, name: str) -> dict:
        """Update an existing account."""
        try:
            response = self.client.patch(
                f"/accounts/{account_id}",
                json={"name": name},
            )
            return response
        except Exception as e:
            raise Exception(f"Error updating account: {str(e)}")

    def delete(self, account_id: str) -> dict:
        """Delete an account."""
        try:
            return self.client.delete(f"/accounts/{account_id}")
        except Exception as e:
            raise Exception(f"Error deleting account: {str(e)}")
