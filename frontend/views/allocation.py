import streamlit as st
from components.allocation import AllocationPlanForm, AllocationPlanTable
from components.base_view import BaseView
from services.accounts import AccountsService
from services.allocation import AllocationService
from utils import handle_error


class AllocationView(BaseView[AllocationService]):
    """
    View for managing investment allocations.
    Extends the BaseView with allocation-specific functionality.
    """

    @classmethod
    def render_page(
        cls, allocation_service: AllocationService, accounts_service: AccountsService
    ):
        """
        Render the allocation page with account selection and allocation plan creation.

        Args:
            allocation_service: Service for allocation operations
            accounts_service: Service for account operations
        """
        view = cls(allocation_service)
        view.render_header("Investment Allocation")

        try:
            # Get accounts for selection
            accounts_result = accounts_service.get_all_accounts()
            accounts = accounts_result.data

            if not accounts:
                st.info("No accounts found. Create one to get started!")
                return

            # Account selector
            selected_account = view.render_account_selector(accounts)

            if selected_account:
                # Create allocation plan form
                allocation_form = AllocationPlanForm()

                # Define callback for creating allocation plan
                def on_create_plan(new_investment, allocation_strategy):
                    try:
                        # Use the spinner placeholder that was created in the form
                        with st.session_state["spinner_placeholder"].container():
                            with st.spinner("Creating allocation plan..."):
                                result = allocation_service.create_allocation_plan(
                                    selected_account,
                                    new_investment,
                                    allocation_strategy,
                                )

                                if result.data:
                                    st.session_state["allocation_plan"] = result.data
                                if result.message:
                                    view.render_success(result.message)
                                    st.rerun()
                    except Exception as e:
                        handle_error(e)

                # Render the allocation form
                allocation_form.render_with_handler(
                    on_create_plan=on_create_plan,
                    allocation_strategies=["scale", "fixed"],
                )

                # Display allocation plan if available
                if (
                    "allocation_plan" in st.session_state
                    and st.session_state["allocation_plan"]
                ):
                    st.subheader("Allocation Plan")

                    allocation_table = AllocationPlanTable(
                        st.session_state["allocation_plan"]
                    )
                    allocation_table.render(use_container_width=True)

                    # Add a button to clear the current plan
                    if st.button("Clear Plan", type="secondary"):
                        del st.session_state["allocation_plan"]
                        st.rerun()

        except Exception as e:
            handle_error(e)
