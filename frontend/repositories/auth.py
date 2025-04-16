import streamlit as st
from api_client import APIClient
from utils import handle_error


class AuthRepository:
    def __init__(self, api_client: APIClient):
        self.client = api_client

    def login(self, username: str, password: str) -> dict:
        """Authenticate user and store token."""
        response = self.client.post(
            "/auth/token",
            data={"username": username, "password": password},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        return response

    def register(
        self, username: str, email: str, password: str, first_name: str, last_name: str
    ) -> bool:
        """Register a new user."""
        try:
            data = {
                "username": username,
                "email": email,
                "password": password,
                "first_name": first_name,
                "last_name": last_name,
            }
            self.client.post("/users/register", json=data)
            st.success("Registration successful! Please log in.")
            return True
        except Exception as e:
            handle_error(e)
            return False

    def logout(self) -> None:
        """Clear user authentication state."""
        st.session_state.token = None

    def init_auth_state(self) -> None:
        """Initialize authentication state."""
        if "token" not in st.session_state:
            st.session_state.token = None
