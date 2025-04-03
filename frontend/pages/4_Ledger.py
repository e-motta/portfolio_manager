import streamlit as st
from utils import require_auth

st.set_page_config(
    page_title="Ledger",
    page_icon="📊",
    layout="wide",
)


@require_auth
def main():
    st.header("Ledger")
    st.info("Ledger management coming soon!")


if __name__ == "__main__":
    main()
