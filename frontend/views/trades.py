import streamlit as st
from components.base_view import BaseView
from components.trades import TradeAddForm, TradesTable
from repositories.accounts import AccountsRepository
from repositories.securities import SecuritiesRepository
from services.accounts import AccountsService
from services.securities import SecuritiesService
from services.trades import TradesService
from utils import handle_error, require_auth


class TradesView(BaseView[TradesService]):
    """
    View for managing trades within accounts.
    Extends the BaseView with trades-specific functionality.
    """

    def render_trades_table(self, account_id: str) -> None:
        """
        Render the trades table with delete functionality.

        Args:
            account_id: ID of the account to display trades for
        """
        try:
            trades = self.service.get_account_trades(account_id)
            if not trades:
                self.render_info("No trades found in this account.")
                return

            # Initialize the trades table component
            trades_table = TradesTable(trades)

            # Define callback for delete action
            def on_delete(trade: dict) -> None:
                try:
                    response = self.service.delete_trade(account_id, trade["id"])
                    self.render_success(response["message"])
                    st.rerun()
                except Exception as e:
                    handle_error(e)

            # Render the table with callback
            trades_table.render(on_delete=on_delete)

            # Add spacing after the table
            self.render_spacing()

        except Exception as e:
            handle_error(e)

    def render_add_trade_form(self, account_id: str) -> None:
        """
        Render the form for adding a new trade.

        Args:
            account_id: ID of the account to add the trade to
        """
        try:
            # Get securities for the account
            securities_repo = SecuritiesRepository(self.service.repository.client)
            securities_service = SecuritiesService(securities_repo)
            securities = securities_service.get_account_securities(account_id)

            # Initialize the add form component
            add_form = TradeAddForm()

            # Define the callback for adding a trade
            def on_add(
                trade_type: str, security_id: str, quantity: float, price: float
            ) -> None:
                try:
                    response = self.service.create_trade(
                        account_id, trade_type, security_id, quantity, price
                    )
                    self.render_success(response["message"])
                    st.rerun()
                except Exception as e:
                    handle_error(e)

            # Render the form with the callback
            add_form.render_with_handler(on_add=on_add, securities=securities)

        except Exception as e:
            handle_error(e)

    def render_trades(self, account_id: str) -> None:
        """
        Render the trades page content for a specific account.

        Args:
            account_id: ID of the account to display trades for
        """
        self.render_header("Trades")
        self.render_trades_table(account_id)
        self.render_add_trade_form(account_id)

    @staticmethod
    @require_auth
    def render_page(service: TradesService) -> None:
        """Entry point for the trades page."""
        view = TradesView(service)
        view.render()

    def render(self) -> None:
        """
        Render the trades page with account selection.
        """
        # Get accounts for the selector
        accounts_repo = AccountsRepository(self.service.repository.client)
        accounts_service = AccountsService(accounts_repo)
        accounts = accounts_service.get_all_accounts()

        # Render account selector or info message
        if not accounts:
            self.render_info(
                "No accounts found. Create an account first to manage trades."
            )
        else:
            # Render account selector and trades for selected account
            selected_account = self.render_account_selector(accounts)
            if selected_account:
                self.render_trades(selected_account)
