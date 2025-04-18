from typing import Callable
import pandas as pd

import streamlit as st
from components.data_table import DataForm


class AllocationPlanTable:
    """
    A specialized data table for displaying allocation plans with specific column configuration.
    """

    def __init__(
        self,
        allocation_items: list[dict],
    ):
        """
        Initialize the allocation plan table with appropriate column configuration.

        Args:
            allocation_items: List of allocation plan item dictionaries
        """
        # Define column configuration specific to allocation plans
        self.col_config = {
            "Symbol": st.column_config.TextColumn(disabled=True),
            "Current Value": st.column_config.TextColumn(disabled=True),
            "Target Allocation": st.column_config.TextColumn("Target %", disabled=True),
            "Current Weight": st.column_config.TextColumn("Current %", disabled=True),
            "Ideal Value": st.column_config.TextColumn(disabled=True),
            "Needed Investment": st.column_config.TextColumn(disabled=True),
        }

        self.allocation_items = pd.DataFrame(allocation_items).drop(
            columns=["Security ID"]
        )

    def render(self, use_container_width: bool = False):
        st.dataframe(
            data=self.allocation_items,
            column_config=self.col_config,
            hide_index=True,
            use_container_width=use_container_width,
        )


class AllocationPlanForm(DataForm):
    """
    Form component for creating an allocation plan.
    """

    def __init__(self):
        """
        Initialize the allocation plan form.
        """
        super().__init__(
            form_id="allocation_plan_form",
            title="Create Allocation Plan",
            use_expander=False,
            clear_on_submit=True,
        )

    def render_with_handler(
        self,
        on_create_plan: Callable[[float, str | None], None],
        allocation_strategies=None,
    ) -> None:
        """
        Render the allocation plan form with the provided handler.

        Args:
            on_create_plan: Callback for creating an allocation plan
            allocation_strategies: List of available allocation strategies
        """

        def render_fields(_):
            col1, col2 = st.columns(2)

            with col1:
                new_investment = st.number_input(
                    "New Investment Amount",
                    min_value=0.0,
                    step=100.0,
                    format="%.2f",
                    help="Enter the amount you want to invest",
                )
                st.session_state["new_investment_amount"] = new_investment

            with col2:
                strategy = None
                if allocation_strategies:
                    strategy = st.selectbox(
                        "Allocation Strategy",
                        options=allocation_strategies,
                        format_func=lambda x: x.capitalize(),
                        help="Select an allocation strategy if your target allocations don't sum to 100%",
                    )
                st.session_state["allocation_strategy"] = strategy

            # Create a placeholder for the spinner that will appear beside the button
            st.session_state["spinner_placeholder"] = st.empty()

        def handle_submit():
            new_investment = st.session_state.get("new_investment_amount", 0.0)
            strategy = st.session_state.get("allocation_strategy")

            if new_investment > 0:
                on_create_plan(new_investment, strategy)
            else:
                st.error("Investment amount must be greater than zero")

        self.render(
            render_fields=render_fields,
            on_submit=handle_submit,
            submit_label="Create Plan",
            use_columns=False,
            submit_button_type="primary",
        )
