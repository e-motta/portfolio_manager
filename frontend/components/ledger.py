import streamlit as st
from typing import Callable
from components.data_table import SelectableDataTable, DataForm


class LedgerTable(SelectableDataTable):
    """
    A specialized data table for ledger with specific column configuration
    and formatting for ledger data.
    """

    def __init__(self, ledger: list[dict], key_prefix: str = "ledger"):
        """
        Initialize the ledger table with appropriate column configuration.

        Args:
            ledger: List of ledger_entry dictionaries
            key_prefix: Prefix for the table key in session state
        """
        # Define column configuration specific to ledger
        col_config = {
            "selected": st.column_config.CheckboxColumn(
                "",
                default=False,
                pinned=True,
                help="Select to Delete",
            ),
            "Date": st.column_config.TextColumn("Date", disabled=True),
            "Type": st.column_config.TextColumn(
                "Type", disabled=True, help="DEPOSIT or WITHDRAWAL"
            ),
            "Amount": st.column_config.Column("Amount", disabled=True, help="Amount"),
        }

        super().__init__(
            data=ledger,
            column_config=col_config,
            key_prefix=key_prefix,
            id_field="id",
            hide_id=True,
        )


class LedgerAddForm(DataForm):
    """
    Form component for adding a new ledger entry.
    """

    def __init__(self):
        """
        Initialize the ledger entry add form.
        """
        super().__init__(
            form_id="add_ledger_entry",
            title="Add New Ledger Entry",
            use_expander=True,
            clear_on_submit=True,
            expanded=False,
        )

    def render_with_handler(
        self,
        on_add: Callable[[str, float], None],
    ) -> None:
        """
        Render the add form with the provided handler.

        Args:
            on_add: Callback for adding a new ledger_entry
            securities: List of securities available for trading
        """

        def render_fields(_):
            col1, col2 = st.columns([1, 1])

            with col1:
                ledger_entry_type = st.selectbox(
                    "Transaction Type",
                    options=["deposit", "withdrawal"],
                    format_func=lambda x: x.upper(),
                    help="Select the type of transaction",
                    index=None,
                )

            with col2:
                amount = st.number_input(
                    "Amount",
                    min_value=0.01,
                    step=0.01,
                    format="%.2f",
                    help="Enter the amount",
                    value=None,
                )

            # Store values in session state
            st.session_state["new_ledger_entry_type"] = ledger_entry_type
            st.session_state["new_ledger_entry_amount"] = amount

        def handle_submit():
            ledger_entry_type = st.session_state.get("new_ledger_entry_type", "")
            amount = st.session_state.get("new_ledger_entry_amount", 0.0)

            if ledger_entry_type and amount > 0:
                on_add(ledger_entry_type, amount)
            else:
                st.error("All fields are required and must be valid")

        self.render(
            render_fields=render_fields,
            on_submit=handle_submit,
            submit_label="Add Ledger Entry",
            use_columns=True,
            submit_button_type="primary",
        )
