import streamlit as st
from repositories.accounts import AccountsRepository
from services.accounts import AccountsService
from services.securities import SecuritiesService
from utils import handle_error, require_auth


class SecuritiesView:
    def __init__(self, service: SecuritiesService):
        self.service = service

    def render_add_security_form(self, account_id: str) -> None:
        with st.expander("Add New Security"):
            with st.form("add_security"):
                symbol = st.text_input("Symbol").upper()
                name = st.text_input("Name")
                target_allocation = st.number_input(
                    "Target Allocation (%)",
                    min_value=0.0,
                    max_value=100.0,
                    step=0.1,
                    format="%.1f",
                )

                if st.form_submit_button("Add Security"):
                    try:
                        response = self.service.create_security(
                            account_id, symbol, name, target_allocation
                        )
                        st.success(response["message"])
                        st.rerun()
                    except Exception as e:
                        handle_error(e)

    def render_securities_table(self, account_id: str) -> None:
        try:
            securities = self.service.get_account_securities(account_id)
            if not securities:
                st.info("No securities found in this account.")
                return

            widths = [1, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5]

            # Create column headers
            cols = st.columns(widths)
            titles = [
                "**Sym**",
                "**Target %**",
                "**Cost Basis**",
                "**Position**",
                "**Average Price**",
                "**Latest Price**",
                "**Current Value**",
            ]
            for col, title in zip(cols, titles):
                col.write(title)

            # Display table with edit/delete buttons
            for security in securities:
                cols = st.columns(widths)
                values = [
                    security["Symbol"],
                    security["Target Allocation"],
                    security["Cost Basis"],
                    security["Position"],
                    security["Average Price"],
                    security["Latest Price"],
                    security["Current Value"],
                ]
                for col, value in zip(cols, values):
                    col.write(value)

                # Edit/Delete buttons
                with cols[-1]:
                    rows = st.columns(2)
                    with rows[0]:
                        if st.button(":pencil2:", key=f"edit_{security['id']}"):
                            st.session_state.editing_security = security["id"]
                    with rows[1]:
                        if st.button(":wastebasket:", key=f"delete_{security['id']}"):
                            try:
                                response = self.service.delete_security(
                                    account_id, security["id"]
                                )
                                st.success(response["message"])
                                st.rerun()
                            except Exception as e:
                                handle_error(e)

                # Edit form
                if st.session_state.get("editing_security") == security["id"]:
                    with st.form(f"edit_security_{security['id']}"):
                        new_target_allocation = st.number_input(
                            "New Target Allocation (%)",
                            min_value=0.0,
                            max_value=100.0,
                            value=float(security["Target Allocation"].rstrip("%")),
                            step=0.1,
                            format="%.1f",
                        )

                        col1, col2 = st.columns(2)

                        with col1:
                            if st.form_submit_button("Save Changes"):
                                try:
                                    response = self.service.update_security(
                                        account_id,
                                        security["id"],
                                        new_target_allocation,
                                    )
                                    st.success(response["message"])
                                    del st.session_state.editing_security
                                    st.rerun()
                                except Exception as e:
                                    handle_error(e)

                        with col2:
                            if st.form_submit_button("Cancel"):
                                del st.session_state.editing_security
                                st.rerun()

        except Exception as e:
            handle_error(e)

    def render_securities(self, account_id: str) -> None:
        st.header("Securities")
        self.render_add_security_form(account_id)
        self.render_securities_table(account_id)

    @staticmethod
    @require_auth
    def render_page(service: SecuritiesService) -> None:
        """Entry point for the securities page."""
        view = SecuritiesView(service)
        view.render()

    def render(self) -> None:
        """Render the securities page."""
        accounts_repo = AccountsRepository(self.service.repository.client)
        accounts_service = AccountsService(accounts_repo)
        accounts = accounts_service.get_all_accounts()
        if not accounts:
            st.info("No accounts found. Create an account first to manage securities.")
        else:
            account_names = {str(acc["ID"]): acc["Name"] for acc in accounts}
            selected_account = st.selectbox(
                "Select Account",
                options=list(account_names.keys()),
                format_func=lambda x: account_names[x],
            )

            if selected_account:
                self.render_securities(selected_account)
