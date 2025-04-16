import streamlit as st
from services.auth import AuthService
from utils import handle_error


class MainView:
    def __init__(self, auth_service: AuthService):
        self.auth_service = auth_service

    def render_login_form(self) -> None:
        """Render the login form."""
        try:
            with st.form("login_form"):
                username = st.text_input("Username")
                password = st.text_input("Password", type="password")
                submit = st.form_submit_button("Login")

                if submit:
                    if self.auth_service.login(username, password):
                        st.session_state.authenticated = True
                        st.success("Logged in successfully!")
                        st.rerun()
                    else:
                        st.error("Invalid credentials")
        except Exception as e:
            handle_error(e)

    def render_register_form(self) -> None:
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
                if new_password != confirm_password:
                    st.error("Passwords do not match")
                else:
                    self.auth_service.register(
                        new_username,
                        new_email,
                        new_password,
                        new_first_name,
                        new_last_name,
                    )
