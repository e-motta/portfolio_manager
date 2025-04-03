import streamlit as st
from services.auth import AuthService


class MainView:
    def __init__(self, auth_service: AuthService):
        self.auth_service = auth_service

    def _render_login_form(self) -> None:
        """Render the login form."""
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submit = st.form_submit_button("Login")

            if submit:
                if self.auth_service.login(username, password):
                    st.success("Logged in successfully!")
                    st.rerun()
                else:
                    st.error("Invalid credentials")

    def _render_register_form(self) -> None:
        """Render the registration form."""
        with st.form("register_form"):
            new_username = st.text_input("Username")
            new_email = st.text_input("Email")
            new_first_name = st.text_input("First Name")
            new_last_name = st.text_input("Last Name")
            new_password = st.text_input("Password", type="password")
            confirm_password = st.text_input("Confirm Password", type="password")
            register_submit = st.form_submit_button("Register")

            if register_submit:
                if not all(
                    [
                        new_username,
                        new_email,
                        new_first_name,
                        new_last_name,
                        new_password,
                    ]
                ):
                    st.error("Please fill in all fields")
                elif new_password != confirm_password:
                    st.error("Passwords do not match")
                else:
                    self.auth_service.register(
                        new_username,
                        new_email,
                        new_password,
                        new_first_name,
                        new_last_name,
                    )

    def _render_navigation(self, pages: dict) -> None:
        """Render the navigation sidebar."""
        st.sidebar.title("Navigation")
        page = st.sidebar.radio("", list(pages.keys()))
        pages[page]()

        if st.sidebar.button("Logout"):
            self.auth_service.logout()
            st.rerun()

    def render(self, pages: dict) -> None:
        """Render the main application view."""
        st.title("Portfolio Manager")

        if not self.auth_service.is_authenticated():
            tab1, tab2 = st.tabs(["Login", "Register"])
            with tab1:
                self._render_login_form()
            with tab2:
                self._render_register_form()
        else:
            self._render_navigation(pages)
