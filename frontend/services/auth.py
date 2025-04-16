import streamlit as st
from repositories.auth import AuthRepository


class AuthService:
    def __init__(self, repository: AuthRepository):
        self.repository = repository

    def login(self, username: str, password: str) -> bool:
        """Attempt to log in a user with the given credentials."""
        response = self.repository.login(username, password)
        if "access_token" in response:
            st.session_state.token = response["access_token"]
            return True
        return False

    def register(
        self, username: str, email: str, password: str, first_name: str, last_name: str
    ) -> bool:
        """Register a new user with the given details."""
        return self.repository.register(
            username, email, password, first_name, last_name
        )

    def logout(self) -> None:
        """Log out the current user."""
        self.repository.logout()

    def is_authenticated(self) -> bool:
        """Check if a user is currently authenticated."""
        return st.session_state.token is not None
