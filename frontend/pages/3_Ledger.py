import streamlit as st
from api_client import APIClient
from repositories.ledger import LedgerRepository
from services.ledger import LedgerService
from views.ledger import LedgerView
from utils import require_auth
from init import get_api_client

st.set_page_config(
    page_title="Ledger",
    page_icon="📊",
    layout="wide",
)


@require_auth
def main():
    # Initialize API client, repository, and service
    client = get_api_client()
    ledger_repo = LedgerRepository(client)
    ledger_service = LedgerService(ledger_repo)

    # Render the ledger view
    LedgerView.render_page(ledger_service)


if __name__ == "__main__":
    main()
