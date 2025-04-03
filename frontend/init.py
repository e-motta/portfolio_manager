import streamlit as st
from api_client import APIClient
from repositories.auth import AuthRepository
from services.auth import AuthService

# Initialize global API client
API_BASE_URL = "http://localhost:8000/api/v1"
_api_client = APIClient(API_BASE_URL, None)


def get_api_client():
    """Get the global API client instance with current token."""
    if "token" in st.session_state:
        _api_client.set_token(st.session_state.token)
    return _api_client


def get_auth_service():
    """Initialize the application with common settings and authentication."""
    auth_repository = AuthRepository(_api_client)
    auth_repository.init_auth_state()

    auth_service = AuthService(auth_repository)
    return auth_service
