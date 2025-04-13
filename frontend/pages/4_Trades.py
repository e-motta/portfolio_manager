import streamlit as st
from init import get_api_client
from repositories.trades import TradesRepository
from services.trades import TradesService
from utils import require_auth
from views.trades import TradesView

st.set_page_config(
    page_title="Trades",
    page_icon="📊",
    layout="wide",
)


@require_auth
def main():
    # Initialize API client, repository, and service
    client = get_api_client()
    trades_repo = TradesRepository(client)
    trades_service = TradesService(trades_repo)

    # Render the trades view
    TradesView.render_page(trades_service)


if __name__ == "__main__":
    main()
