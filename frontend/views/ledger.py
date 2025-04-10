import streamlit as st

from repositories.accounts import AccountsRepository
from repositories.securities import SecuritiesRepository
from services.accounts import AccountsService
from services.securities import SecuritiesService
from services.ledger import LedgerService
from utils import handle_error, require_auth

from components.base_view import BaseView
from components.ledger import LedgerTable, LedgerAddForm


class LedgerView(BaseView[LedgerService]):
    """
    View for managing ledger within accounts.
    Extends the BaseView with ledger-specific functionality.
    """

    def render_ledger_table(self, account_id: str) -> None:
        """
        Render the ledger table with delete functionality.

        Args:
            account_id: ID of the account to display ledger for
        """
        try:
            ledger = self.service.get_account_ledger(account_id)
            if not ledger:
                self.render_info("No ledger entries found in this account.")
                return

            # Initialize the ledger table component
            ledger_table = LedgerTable(ledger)

            # Define callback for delete action
            def on_delete(ledger_entry: dict) -> None:
                try:
                    response = self.service.delete_ledger_entry(
                        account_id, ledger_entry["id"]
                    )
                    self.render_success(response["message"])
                    st.rerun()
                except Exception as e:
                    handle_error(e)

            # Render the table with callback
            ledger_table.render(on_delete=on_delete)

            # Add spacing after the table
            self.render_spacing()

        except Exception as e:
            handle_error(e)

    def render_add_ledger_entry_form(self, account_id: str) -> None:
        """
        Render the form for adding a new ledger_entry.

        Args:
            account_id: ID of the account to add the ledger_entry to
        """
        try:
            # Initialize the add form component
            add_form = LedgerAddForm()

            # Define the callback for adding a ledger_entry
            def on_add(ledger_entry_type: str, amount: float) -> None:
                try:
                    response = self.service.create_ledger_entry(
                        account_id, ledger_entry_type, amount
                    )
                    self.render_success(response["message"])
                    st.rerun()
                except Exception as e:
                    handle_error(e)

            # Render the form with the callback
            add_form.render_with_handler(on_add=on_add)

        except Exception as e:
            handle_error(e)

    def render_ledger(self, account_id: str) -> None:
        """
        Render the ledger page content for a specific account.

        Args:
            account_id: ID of the account to display ledger for
        """
        self.render_header("Ledger")
        self.render_ledger_table(account_id)
        self.render_add_ledger_entry_form(account_id)

    @staticmethod
    @require_auth
    def render_page(service: LedgerService) -> None:
        """Entry point for the ledger page."""
        view = LedgerView(service)
        view.render()

    def render(self) -> None:
        """
        Render the ledger page with account selection.
        """
        # Get accounts for the selector
        accounts_repo = AccountsRepository(self.service.repository.client)
        accounts_service = AccountsService(accounts_repo)
        accounts = accounts_service.get_all_accounts()

        # Render account selector or info message
        if not accounts:
            self.render_info(
                "No accounts found. Create an account first to manage ledger."
            )
        else:
            # Render account selector and ledger for selected account
            selected_account = self.render_account_selector(accounts)
            if selected_account:
                self.render_ledger(selected_account)
