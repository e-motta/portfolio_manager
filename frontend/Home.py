import streamlit as st
from init import get_auth_service
from views.main import MainView

st.set_page_config(
    page_title="Portfolio Manager",
    page_icon="📊",
    initial_sidebar_state="expanded",
)

auth_service = get_auth_service()
main_view = MainView(auth_service)

if not st.session_state.get("authenticated", False):
    st.title("Portfolio Manager")
    main_view.render_login_form()

    with st.expander("New user? Register here"):
        main_view.render_register_form()
else:
    st.title("Portfolio Manager")
    st.info("Welcome to your Portfolio Management Dashboard")
