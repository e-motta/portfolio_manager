import pandas as pd
import streamlit as st
from services.accounts import AccountsService
from utils import handle_error, require_auth


class AccountsView:
    def __init__(self, service: AccountsService):
        self.service = service

    def _display_accounts_table(self, accounts_data: list) -> None:
        """Display accounts in a table format."""
        df = pd.DataFrame(accounts_data)
        st.dataframe(
            df,
            hide_index=True,
            use_container_width=True,
            column_config={
                "ID": st.column_config.TextColumn(),
                "Name": st.column_config.TextColumn(),
                "Buying Power": st.column_config.TextColumn(),
            },
        )

    def _add_new_account(self) -> None:
        """Render form for creating a new account."""
        with st.expander("Create New Account"):
            with st.form("new_account_form"):
                name = st.text_input("Account Name")
                if st.form_submit_button("Create Account"):
                    try:
                        response = self.service.create_account(name)
                        st.success(response["message"])
                        st.rerun()
                    except Exception as e:
                        handle_error(e)

    def _list_existing_accounts(self) -> None:
        """Display list of existing accounts."""
        try:
            accounts = self.service.get_all_accounts()
            if not accounts:
                st.info("No accounts found. Create one to get started!")
                return
            self._display_accounts_table(accounts)
        except Exception as e:
            handle_error(e)

    def render(self) -> None:
        """Render the accounts page."""
        st.header("Accounts")
        self._add_new_account()
        self._list_existing_accounts()

    @staticmethod
    @require_auth
    def render_page(service: AccountsService) -> None:
        """Entry point for the accounts page."""
        view = AccountsView(service)
        view.render()
