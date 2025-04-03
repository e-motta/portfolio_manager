import streamlit as st
from utils import require_auth

st.set_page_config(
    page_title="Trades",
    page_icon="📊",
    layout="wide",
)


@require_auth
def main():
    st.header("Trades")
    st.info("Trade management coming soon!")


if __name__ == "__main__":
    main()
