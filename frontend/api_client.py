import requests


class APIClient:
    def __init__(self, base_url: str, token: str | None):
        self.base_url = base_url
        self.token = token
        self.headers = {"Authorization": f"Bearer {token}"}

    def set_token(self, token: str):
        self.token = token
        self.headers = {"Authorization": f"Bearer {token}"}

    def get(self, endpoint: str):
        response = requests.get(f"{self.base_url}{endpoint}", headers=self.headers)
        response.raise_for_status()
        return response.json()

    def post(self, endpoint: str, json: dict):
        response = requests.post(
            f"{self.base_url}{endpoint}", headers=self.headers, json=json
        )
        response.raise_for_status()
        return response.json()

    def patch(self, endpoint: str, json: dict):
        response = requests.patch(
            f"{self.base_url}{endpoint}", headers=self.headers, json=json
        )
        response.raise_for_status()
        return response.json()

    def delete(self, endpoint: str):
        response = requests.delete(f"{self.base_url}{endpoint}", headers=self.headers)
        response.raise_for_status()
        return response.json()
