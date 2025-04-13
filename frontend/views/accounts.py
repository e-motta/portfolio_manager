from typing import Callable

import streamlit as st
from components.accounts import AccountEditForm
from components.base_view import BaseView
from components.data_table import DataForm, SelectableDataTable
from services.accounts import AccountsService
from utils import handle_error, require_auth


class AccountsTable(SelectableDataTable):
    """
    A specialized data table for accounts with specific column configuration.
    """

    def __init__(self, accounts: list[dict], key_prefix: str = "accounts"):
        """
        Initialize the accounts table with appropriate column configuration.

        Args:
            accounts: List of account dictionaries
            key_prefix: Prefix for the table key in session state
        """
        # Define column configuration specific to accounts
        col_config = {
            "selected": st.column_config.CheckboxColumn(
                "",
                default=False,
                pinned=True,
                help="Select to Edit or Delete",
            ),
            "Name": st.column_config.TextColumn("Name", disabled=True),
            "Buying Power": st.column_config.Column("Buying Power", disabled=True),
        }

        super().__init__(
            data=accounts,
            column_config=col_config,
            key_prefix=key_prefix,
            id_field="ID",
            hide_id=True,
        )


class AccountAddForm(DataForm):
    """
    Form component for adding a new account.
    """

    def __init__(self):
        """
        Initialize the account add form.
        """
        super().__init__(
            form_id="new_account_form",
            title="Create New Account",
            use_expander=True,
            clear_on_submit=True,
            expanded=False,
        )

    def render_with_handler(self, on_add: Callable[[str], None]) -> None:
        """
        Render the add form with the provided handler.

        Args:
            on_add: Callback for adding a new account
        """

        def render_fields(_):
            name = st.text_input("Account Name")
            st.session_state["new_account_name"] = name

        def handle_submit():
            name = st.session_state.get("new_account_name", "")
            if name:
                on_add(name)
            else:
                st.error("Account name is required")

        self.render(
            render_fields=render_fields,
            on_submit=handle_submit,
            submit_label="Create Account",
            use_columns=False,
            submit_button_type="primary",
        )


class AccountsView(BaseView[AccountsService]):
    """
    View for managing accounts.
    Extends the BaseView with account-specific functionality.
    """

    def render_accounts_table(self) -> None:
        """
        Render the accounts table with edit and delete functionality.
        """
        try:
            accounts = self.service.get_all_accounts()
            if not accounts:
                self.render_info("No accounts found. Create one to get started!")
                return

            # Initialize the accounts table component
            accounts_table = AccountsTable(accounts)

            # Define callbacks for edit and delete actions
            def on_edit(account: dict) -> None:
                st.session_state.editing_account = account["ID"]

            def on_delete(account: dict) -> None:
                try:
                    response = self.service.delete_account(account["ID"])
                    print(response["message"])
                    self.render_success(response["message"])
                    st.rerun()
                except Exception as e:
                    handle_error(e)

            # Render the table with callbacks
            def reset_edit_form():
                st.session_state.editing_account = None

            accounts_table.render(
                on_edit=on_edit, on_delete=on_delete, on_change=reset_edit_form
            )

            # Handle editing if an account is selected for edit
            if st.session_state.get("editing_account"):
                account_to_edit = next(
                    (
                        a
                        for a in accounts
                        if a["ID"] == st.session_state.editing_account
                    ),
                    None,
                )

                if account_to_edit:
                    # Initialize and render the edit form
                    edit_form = AccountEditForm(account_to_edit["ID"])

                    def on_save(new_name: str) -> None:
                        try:
                            response = self.service.update_account(
                                account_to_edit["ID"],
                                new_name,
                            )
                            self.render_success("Account updated successfully")
                            del st.session_state.editing_account
                            st.rerun()
                        except Exception as e:
                            handle_error(e)

                    def on_cancel() -> None:
                        del st.session_state.editing_account
                        st.rerun()

                    edit_form.render_with_data(
                        account=account_to_edit,
                        on_save=on_save,
                        on_cancel=on_cancel,
                    )

            # Add spacing after the table
            self.render_spacing()

        except Exception as e:
            handle_error(e)

    def render_add_account_form(self) -> None:
        """
        Render the form for adding a new account.
        """
        # Initialize the add form component
        add_form = AccountAddForm()

        # Define the callback for adding an account
        def on_add(name: str) -> None:
            try:
                response = self.service.create_account(name)
                self.render_success(response["message"])
                st.rerun()
            except Exception as e:
                handle_error(e)

        # Render the form with the callback
        add_form.render_with_handler(on_add=on_add)

    def render(self) -> None:
        """
        Render the accounts page.
        """
        self.render_header("Accounts")
        self.render_accounts_table()
        self.render_add_account_form()

    @staticmethod
    @require_auth
    def render_page(service: AccountsService) -> None:
        """
        Entry point for the accounts page.
        """
        view = AccountsView(service)
        view.render()
