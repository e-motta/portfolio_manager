import streamlit as st
from repositories.accounts import AccountsRepository
from services.accounts import AccountsService
from utils import require_auth
from views.accounts import AccountsView
from init import get_api_client

st.set_page_config(
    page_title="Accounts",
    page_icon="📊",
    layout="wide",
)


@require_auth
def main():
    api_client = get_api_client()
    repository = AccountsRepository(api_client)
    service = AccountsService(repository)
    AccountsView.render_page(service)


if __name__ == "__main__":
    main()
