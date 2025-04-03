import requests
import streamlit as st
from api_client import APIClient


class AuthRepository:
    def __init__(self, api_client: APIClient):
        self.client = api_client

    def login(self, username: str, password: str) -> bool:
        """Authenticate user and store token."""
        try:
            response = requests.post(
                f"{self.client.base_url}/auth/token",
                data={"username": username, "password": password},
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )
            token = response.json()["access_token"]
            st.session_state.token = token
            return True
        except requests.exceptions.HTTPError as e:
            st.error("Invalid username or password")
            return False
        except Exception as e:
            st.error(f"Error during login: {str(e)}")
            return False

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
            try:
                self.client.post("/users/register", json=data)
                st.success("Registration successful! Please log in.")
                return True
            except requests.exceptions.HTTPError as e:
                detail = e.response.json()["detail"]
                if isinstance(detail, list):
                    for error in detail:
                        if error["type"] == "missing":
                            formatted_values = {
                                "first_name": "First name",
                                "last_name": "Last name",
                                "email": "Email",
                                "password": "Password",
                            }
                            value = error["loc"][1]
                            st.error(
                                f"{formatted_values.get(value, value)} is required"
                            )
                        elif error["type"] == "password_validation_error":
                            for rule in error["ctx"]["rules"]:
                                st.error(rule)
                else:
                    st.error(f"Registration failed: {detail['msg']}")
                return False
        except Exception as e:
            st.error(f"Error during registration: {str(e)}")
            return False

    def logout(self) -> None:
        """Clear user authentication state."""
        st.session_state.token = None

    def init_auth_state(self) -> None:
        """Initialize authentication state."""
        if "token" not in st.session_state:
            st.session_state.token = None
