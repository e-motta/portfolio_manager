
from api_client import APIClient


class SecuritiesRepository:
    def __init__(self, client: APIClient):
        self.client = client

    def fetch_securities(self, account_id: str) -> dict:
        """Fetch all securities for a specific account."""
        try:
            response = self.client.get(f"/accounts/{account_id}/securities")
            return response
        except Exception as e:
            raise Exception(f"Error fetching securities: {str(e)}")

    def create_security(self, account_id: str, security_data: dict) -> dict:
        """Create a new security for a specific account."""
        return self.client.post(
            f"/accounts/{account_id}/securities", json=security_data
        )

    def update_security(
        self, account_id: str, security_id: str, security_data: dict
    ) -> dict:
        """Update a security for a specific account."""
        return self.client.patch(
            f"/accounts/{account_id}/securities/{security_id}", json=security_data
        )

    def delete_security(self, account_id: str, security_id: str) -> dict:
        """Delete a security from a specific account."""
        return self.client.delete(f"/accounts/{account_id}/securities/{security_id}")
