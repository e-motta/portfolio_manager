import streamlit as st
from init import get_api_client
from repositories.ledger import LedgerRepository
from services.ledger import LedgerService
from utils import require_auth
from views.ledger import LedgerView

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
