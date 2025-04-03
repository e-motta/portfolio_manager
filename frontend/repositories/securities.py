from typing import Any

from api_client import APIClient


class SecuritiesRepository:
    def __init__(self, client: APIClient):
        self.client = client

    def fetch_securities(self, account_id: str) -> list[dict[str, Any]]:
        """Fetch all securities for a specific account."""
        try:
            response = self.client.get(f"/accounts/{account_id}/securities")
            return response["data"]
        except Exception as e:
            return []

    def create_security(
        self, account_id: str, security_data: dict[str, Any]
    ) -> dict[str, Any]:
        """Create a new security for a specific account."""
        return self.client.post(
            f"/accounts/{account_id}/securities", json=security_data
        )

    def update_security(
        self, account_id: str, security_id: str, security_data: dict[str, Any]
    ) -> dict[str, Any]:
        """Update a security for a specific account."""
        return self.client.patch(
            f"/accounts/{account_id}/securities/{security_id}", json=security_data
        )

    def delete_security(self, account_id: str, security_id: str) -> dict[str, Any]:
        """Delete a security from a specific account."""
        return self.client.delete(f"/accounts/{account_id}/securities/{security_id}")
