import streamlit as st
from api_client import APIClient
from pages.accounts import render_accounts_page
from pages.securities import render_securities_page
from repositories.auth import AuthRepository
from services.auth import AuthService
from views.main import MainView

API_BASE_URL = "http://localhost:8000/api/v1"

api_client = APIClient(API_BASE_URL, None)
auth_repository = AuthRepository(api_client)
auth_repository.init_auth_state()

api_client.set_token(st.session_state.token)

auth_service = AuthService(auth_repository)
main_view = MainView(auth_service)


def render_trades():
    st.header("Trades")
    st.info("Trade management coming soon!")


def render_ledger():
    st.header("Ledger")
    st.info("Ledger management coming soon!")


def main():
    pages = {
        "Accounts": lambda: render_accounts_page(api_client),
        "Securities": lambda: render_securities_page(api_client),
        "Trades": render_trades,
        "Ledger": render_ledger,
    }

    main_view.render(pages)


if __name__ == "__main__":
    main()
