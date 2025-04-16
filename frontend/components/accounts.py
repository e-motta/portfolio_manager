from typing import Callable

import streamlit as st
from components.data_table import DataForm


class AccountEditForm(DataForm):
    """
    Form component for editing an account's details.
    """

    def __init__(self, account_id: str):
        """
        Initialize the account edit form.

        Args:
            account_id: ID of the account being edited
        """
        super().__init__(
            form_id=f"edit_account_{account_id}",
            title="Edit Account",
            clear_on_submit=False,
        )
        self.account_id = account_id

    def render_with_data(
        self,
        account: dict,
        on_save: Callable[[str], None],
        on_cancel: Callable[[], None],
    ) -> None:
        """
        Render the edit form with the account's data.

        Args:
            account: Account data dictionary
            on_save: Callback for saving changes
            on_cancel: Callback for canceling changes
        """

        def render_fields(_):
            # Create the account name input
            new_name = st.text_input(
                "Account Name",
                value=account["Name"],
                help="Edit the account name",
            )

            # Store the value in the form's state
            st.session_state[f"edit_name_{self.account_id}"] = new_name

        def handle_submit():
            new_name = st.session_state.get(f"edit_name_{self.account_id}", "")
            if new_name:
                on_save(new_name)
            else:
                st.error("Account name is required")

        self.render(
            render_fields=render_fields,
            on_submit=handle_submit,
            submit_label="💾 Save Changes",
            cancel_label="❌ Cancel",
            on_cancel=on_cancel,
            use_columns=False,
            submit_button_type="primary",
        )
