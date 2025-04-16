import streamlit as st
from components.base_view import BaseView
from components.securities import SecuritiesTable, SecurityAddForm, SecurityEditForm
from repositories.accounts import AccountsRepository
from services.accounts import AccountsService
from services.securities import SecuritiesService
from utils import handle_error, require_auth


class SecuritiesView(BaseView[SecuritiesService]):
    """
    View for managing securities within accounts.
    Extends the BaseView with securities-specific functionality.
    """

    def render_securities_table(self, account_id: str) -> None:
        """
        Render the securities table with edit and delete functionality.

        Args:
            account_id: ID of the account to display securities for
        """
        try:
            result = self.service.get_account_securities(account_id)
            securities = result.data
            if not securities:
                self.render_info("No securities found in this account.")
                return

            # Initialize the securities table component
            securities_table = SecuritiesTable(securities)

            # Define callbacks for edit and delete actions
            def on_edit(security: dict) -> None:
                st.session_state.editing_security = security["id"]

            def on_delete(security: dict) -> None:
                try:
                    response = self.service.delete_security(account_id, security["id"])
                    if response.message:
                        self.render_success(response.message)
                    st.rerun()
                except Exception as e:
                    handle_error(e)

            # Render the table with callbacks
            def reset_edit_form():
                st.session_state.editing_security = None

            securities_table.render(
                on_edit=on_edit, on_delete=on_delete, on_change=reset_edit_form
            )

            # Handle editing if a security is selected for edit
            if st.session_state.get("editing_security"):
                security_to_edit = next(
                    (
                        s
                        for s in securities
                        if s["id"] == st.session_state.editing_security
                    ),
                    None,
                )

                if security_to_edit:
                    # Initialize and render the edit form
                    edit_form = SecurityEditForm(security_to_edit["id"])

                    def on_save(new_allocation: float) -> None:
                        try:
                            response = self.service.update_security(
                                account_id,
                                security_to_edit["id"],
                                new_allocation,
                            )
                            if response.message:
                                self.render_success(response.message)
                            del st.session_state.editing_security
                            st.rerun()
                        except Exception as e:
                            handle_error(e)

                    def on_cancel() -> None:
                        del st.session_state.editing_security
                        st.rerun()

                    edit_form.render_with_data(
                        security=security_to_edit,
                        on_save=on_save,
                        on_cancel=on_cancel,
                    )

            # Add spacing after the table
            self.render_spacing()

        except Exception as e:
            handle_error(e)

    def render_add_security_form(self, account_id: str) -> None:
        """
        Render the form for adding a new security.

        Args:
            account_id: ID of the account to add the security to
        """
        # Initialize the add form component
        add_form = SecurityAddForm()

        # Define the callback for adding a security
        def on_add(symbol: str, name: str, allocation: float) -> None:
            try:
                response = self.service.create_security(
                    account_id, symbol, name, allocation
                )
                if response.message:
                    self.render_success(response.message)
                st.rerun()
            except Exception as e:
                handle_error(e)

        # Render the form with the callback
        add_form.render_with_handler(on_add=on_add)

    def render_securities(self, account_id: str) -> None:
        """
        Render the securities page content for a specific account.

        Args:
            account_id: ID of the account to display securities for
        """
        self.render_header("Securities")
        self.render_securities_table(account_id)
        self.render_add_security_form(account_id)

    @staticmethod
    @require_auth
    def render_page(service: SecuritiesService) -> None:
        """Entry point for the securities page."""
        view = SecuritiesView(service)
        view.render()

    def render(self) -> None:
        """
        Render the securities page with account selection.
        """
        # Get accounts for the selector
        accounts_repo = AccountsRepository(self.service.repository.client)
        accounts_service = AccountsService(accounts_repo)
        result = accounts_service.get_all_accounts()
        accounts = result.data

        # Render account selector or info message
        if not accounts:
            self.render_info(
                "No accounts found. Create an account first to manage securities."
            )
        else:
            # Render account selector and securities for selected account
            selected_account = self.render_account_selector(accounts)
            if selected_account:
                self.render_securities(selected_account)
