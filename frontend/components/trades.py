import streamlit as st
from typing import Callable
from components.data_table import SelectableDataTable, DataForm


class TradesTable(SelectableDataTable):
    """
    A specialized data table for trades with specific column configuration
    and formatting for trades data.
    """

    def __init__(self, trades: list[dict], key_prefix: str = "trades"):
        """
        Initialize the trades table with appropriate column configuration.

        Args:
            trades: List of trade dictionaries
            key_prefix: Prefix for the table key in session state
        """
        # Define column configuration specific to trades
        col_config = {
            "selected": st.column_config.CheckboxColumn(
                "",
                default=False,
                pinned=True,
                help="Select to Delete",
            ),
            "Date": st.column_config.TextColumn("Date", disabled=True),
            "Type": st.column_config.TextColumn(
                "Type", disabled=True, help="BUY or SELL transaction"
            ),
            "Security ID": st.column_config.TextColumn(
                "Security", disabled=True, help="Security identifier"
            ),
            "Quantity": st.column_config.Column(
                "Quantity", disabled=True, help="Number of shares/units"
            ),
            "Price": st.column_config.Column(
                "Price", disabled=True, help="Price per share/unit"
            ),
            "Total": st.column_config.Column(
                "Total", disabled=True, help="Total transaction value"
            ),
        }

        super().__init__(
            data=trades,
            column_config=col_config,
            key_prefix=key_prefix,
            id_field="id",
            hide_id=True,
        )


class TradeAddForm(DataForm):
    """
    Form component for adding a new trade.
    """

    def __init__(self):
        """
        Initialize the trade add form.
        """
        super().__init__(
            form_id="add_trade",
            title="Add New Trade",
            use_expander=True,
            clear_on_submit=False,
            expanded=False,
        )
        # Initialize trade confirmation state
        if "trade_confirmed" not in st.session_state:
            st.session_state["trade_confirmed"] = False

    def render_with_handler(
        self,
        on_add: Callable[[str, str, float, float], None],
        securities: list[dict],
    ) -> None:
        """
        Render the add form with the provided handler.

        Args:
            on_add: Callback for adding a new trade
            securities: List of securities available for trading
        """

        def render_fields(_):
            if not securities:
                st.warning("No securities available. Please add securities first.")
                return

            col1, col2 = st.columns([1, 1])

            with col1:
                trade_type = st.selectbox(
                    "Transaction Type",
                    options=["buy", "sell"],
                    format_func=lambda x: x.upper(),
                    help="Select the type of transaction",
                    index=None,
                )

            with col2:
                security_options = {s["id"]: s["Symbol"] for s in securities}
                security_id = st.selectbox(
                    "Security",
                    options=list(security_options.keys()),
                    format_func=lambda x: security_options[x],
                    help="Select the security to trade",
                    index=None,
                )

            col3, col4 = st.columns([1, 1])

            with col3:
                quantity = st.number_input(
                    "Quantity",
                    min_value=0.0001,
                    step=0.0001,
                    format="%.4f",
                    help="Enter the number of shares/units",
                    value=None,
                )

            with col4:
                price = st.number_input(
                    "Price",
                    min_value=0.01,
                    step=0.01,
                    format="%.2f",
                    help="Enter the price per share/unit",
                    value=None,
                )

            # Store values in session state
            st.session_state["new_trade_type"] = trade_type
            st.session_state["new_trade_security_id"] = security_id
            st.session_state["new_trade_quantity"] = quantity
            st.session_state["new_trade_price"] = price

        def handle_submit():
            trade_type = st.session_state.get("new_trade_type", "")
            security_id = st.session_state.get("new_trade_security_id", "")
            quantity = st.session_state.get("new_trade_quantity", 0.0)
            price = st.session_state.get("new_trade_price", 0.0)

            if all([trade_type, security_id, quantity > 0, price > 0]):
                on_add(trade_type, security_id, quantity, price)
                # Reset the confirmation state after successful submission
                st.session_state["trade_confirmed"] = False
                if "confirmed_total" in st.session_state:
                    del st.session_state["confirmed_total"]
            else:
                st.error("All fields are required and must be valid")

        def handle_confirm():
            trade_type = st.session_state.get("new_trade_type", "")
            security_id = st.session_state.get("new_trade_security_id", "")
            quantity = st.session_state.get("new_trade_quantity", 0.0)
            price = st.session_state.get("new_trade_price", 0.0)
            total = quantity * price

            if all([trade_type, security_id, quantity > 0, price > 0]):
                # Set confirmation state
                st.session_state["trade_confirmed"] = True
                st.session_state["confirmed_total"] = total
                st.rerun()
            else:
                st.error("All fields are required and must be valid")

        self.render(
            render_fields=render_fields,
            on_submit=handle_submit,
            submit_label="Add Trade",
        )
