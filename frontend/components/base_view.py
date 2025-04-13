from typing import Callable, Generic, TypeVar

import streamlit as st
from utils import require_auth

# Generic type for service classes
ServiceT = TypeVar("ServiceT")


class BaseView(Generic[ServiceT]):
    """
    Base view class that provides common functionality for all views.
    This class can be extended by specific views like SecuritiesView, AccountsView, etc.
    """

    def __init__(self, service: ServiceT):
        """
        Initialize the base view with a service.

        Args:
            service: Service instance for data operations
        """
        self.service = service

        # Display any pending success messages at the beginning of each view rendering
        self._display_success_messages()

    def _display_success_messages(self):
        """Display any pending success messages using toast notifications that persist across reruns."""
        if "success_messages" in st.session_state and st.session_state.success_messages:
            for msg in st.session_state.success_messages:
                st.toast(msg, icon="✅")
            st.session_state.success_messages = []

    def render_account_selector(
        self,
        accounts: list[dict],
        on_account_selected: Callable | None = None,
        account_id_field: str = "ID",
        account_name_field: str = "Name",
    ) -> str | None:
        """
        Render a dropdown to select an account.

        Args:
            accounts: List of account dictionaries
            on_account_selected: Callback when an account is selected
            account_id_field: Field name for account ID
            account_name_field: Field name for account name

        Returns:
            Selected account ID or None
        """
        if not accounts:
            st.info("No accounts found. Create an account first.")
            return None

        account_names = {
            str(acc[account_id_field]): acc[account_name_field] for acc in accounts
        }
        selected_account = st.selectbox(
            "Select Account",
            options=list(account_names.keys()),
            format_func=lambda x: account_names[x],
        )

        if selected_account and on_account_selected:
            on_account_selected(selected_account)

        return selected_account

    def render_header(self, title: str) -> None:
        """
        Render a page header with consistent styling.

        Args:
            title: Header title text
        """
        st.header(title)

    def render_info(self, message: str) -> None:
        """
        Display an info message with consistent styling.

        Args:
            message: Info message to display
        """
        st.info(message)

    def render_success(self, message: str) -> None:
        """
        Display a success message with consistent styling.
        Stores the message in session state to persist across reruns.

        Args:
            message: Success message to display
        """
        # Initialize success messages list if it doesn't exist
        if "success_messages" not in st.session_state:
            st.session_state.success_messages = []

        # Add the new message to the list
        st.session_state.success_messages.append(message)

    def render_error(self, message: str) -> None:
        """
        Display an error message with consistent styling.

        Args:
            message: Error message to display
        """
        st.error(message)

    def render_spacing(self, height_px: int = 25) -> None:
        """
        Add vertical spacing with consistent styling.

        Args:
            height_px: Height in pixels
        """
        st.markdown(
            f"<div style='margin-top: {height_px}px;'></div>", unsafe_allow_html=True
        )

    def render(self) -> None:
        """
        Main render method to be implemented by subclasses.
        This method should contain the main rendering logic for the view.
        """
        raise NotImplementedError("Subclasses must implement render()")

    @classmethod
    @require_auth
    def render_page(cls, service: ServiceT) -> None:
        """
        Entry point for the page. This method creates an instance of the view
        and calls its render method.

        Args:
            service: Service instance for data operations
        """
        view = cls(service)
        view.render()
