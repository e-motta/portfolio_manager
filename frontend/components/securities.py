from typing import Callable

import streamlit as st
from components.data_table import DataForm, SelectableDataTable


class SecuritiesTable(SelectableDataTable):
    """
    A specialized data table for securities with specific column configuration
    and formatting for securities data.
    """

    def __init__(self, securities: list[dict], key_prefix: str = "securities"):
        """
        Initialize the securities table with appropriate column configuration.

        Args:
            securities: List of security dictionaries
            key_prefix: Prefix for the table key in session state
        """
        # Define column configuration specific to securities
        col_config = {
            "selected": st.column_config.CheckboxColumn(
                "",
                default=False,
                pinned=True,
                help="Select to Edit or Delete",
            ),
            "Symbol": st.column_config.TextColumn("Symbol", disabled=True),
            "Target Allocation": st.column_config.Column("Target %", disabled=True),
            "Cost Basis": st.column_config.Column("Cost Basis", disabled=True),
            "Position": st.column_config.Column("Position", disabled=True),
            "Average Price": st.column_config.Column("Avg Price", disabled=True),
            "Latest Price": st.column_config.Column("Latest Price", disabled=True),
            "Current Value": st.column_config.Column("Current Value", disabled=True),
        }

        super().__init__(
            data=securities,
            column_config=col_config,
            key_prefix=key_prefix,
            id_field="id",
            hide_id=True,
        )


class SecurityEditForm(DataForm):
    """
    Form component for editing a security's details.
    """

    def __init__(self, security_id: str):
        """
        Initialize the security edit form.

        Args:
            security_id: ID of the security being edited
        """
        super().__init__(
            form_id=f"edit_security_{security_id}",
            title="Edit Security",
            clear_on_submit=False,
        )
        self.security_id = security_id

    def render_with_data(
        self,
        security: dict,
        on_save: Callable[[float], None],
        on_cancel: Callable[[], None],
    ) -> None:
        """
        Render the edit form with the security's data.

        Args:
            security: Security data dictionary
            on_save: Callback for saving changes
            on_cancel: Callback for canceling changes
        """

        def render_fields(_):
            # Extract the numeric value from the percentage string
            current_value = (
                float(security["Target Allocation"].rstrip("%"))
                if isinstance(security["Target Allocation"], str)
                else security["Target Allocation"]
            )

            # Create the target allocation input
            new_target_allocation = st.number_input(
                "Target Allocation (%)",
                value=current_value,
                step=0.1,
                format="%.1f",
                help="Adjust the target allocation percentage for this security",
            )

            # Store the value in the form's state
            st.session_state[f"edit_allocation_{self.security_id}"] = (
                new_target_allocation
            )

        def handle_submit():
            new_allocation = st.session_state.get(
                f"edit_allocation_{self.security_id}", 0.0
            )
            on_save(new_allocation)

        self.render(
            render_fields=render_fields,
            on_submit=handle_submit,
            submit_label="💾 Save Changes",
            cancel_label="❌ Cancel",
            on_cancel=on_cancel,
            use_columns=True,
            submit_button_type="primary",
        )


class SecurityAddForm(DataForm):
    """
    Form component for adding a new security.
    """

    def __init__(self):
        """
        Initialize the security add form.
        """
        super().__init__(
            form_id="add_security",
            title="Add New Security",
            use_expander=True,
            clear_on_submit=True,
            expanded=False,
        )

    def render_with_handler(
        self,
        on_add: Callable[[str, str, float], None],
    ) -> None:
        """
        Render the add form with the provided handler.

        Args:
            on_add: Callback for adding a new security
        """

        def render_fields(_):
            col1, col2 = st.columns([1, 1])

            with col1:
                symbol = st.text_input(
                    "Symbol",
                    max_chars=10,
                    help="Enter the security symbol (e.g., AAPL)",
                ).upper()

            with col2:
                name = st.text_input(
                    "Name",
                    help="Enter the full name of the security",
                )

            target_allocation = st.number_input(
                "Target Allocation (%)",
                value=None,
                step=0.1,
                format="%.1f",
                help="Set the target allocation percentage for this security",
            )

            print(target_allocation)
            # Store values in session state
            st.session_state["new_security_symbol"] = symbol
            st.session_state["new_security_name"] = name
            st.session_state["new_security_allocation"] = target_allocation

        def handle_submit():
            symbol = st.session_state.get("new_security_symbol", "")
            name = st.session_state.get("new_security_name", "")
            allocation = st.session_state.get("new_security_allocation", 0.0)

            if not symbol or not name:
                st.error("Symbol and Name are required")
                st.stop()

            on_add(symbol, name, allocation)

        self.render(
            render_fields=render_fields,
            on_submit=handle_submit,
            submit_label="Add Security",
            use_columns=True,
            submit_button_type="primary",
        )
