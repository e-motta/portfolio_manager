import streamlit as st
from init import get_api_client
from repositories.accounts import AccountsRepository
from repositories.allocation import AllocationRepository
from services.accounts import AccountsService
from services.allocation import AllocationService
from utils import require_auth
from views.allocation import AllocationView

st.set_page_config(
    page_title="Allocation",
    page_icon="📈",
    layout="wide",
)


@require_auth
def main():
    api_client = get_api_client()
    accounts_repository = AccountsRepository(api_client)
    accounts_service = AccountsService(accounts_repository)

    allocation_repository = AllocationRepository(api_client)
    allocation_service = AllocationService(allocation_repository)

    AllocationView.render_page(allocation_service, accounts_service)


if __name__ == "__main__":
    main()
