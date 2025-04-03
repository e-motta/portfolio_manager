import streamlit as st
from repositories.securities import SecuritiesRepository
from services.securities import SecuritiesService
from utils import require_auth
from views.securities import SecuritiesView
from init import get_api_client


st.set_page_config(
    page_title="Securities",
    page_icon="📊",
    layout="wide",
)


@require_auth
def main():
    api_client = get_api_client()
    repository = SecuritiesRepository(api_client)
    service = SecuritiesService(repository)
    SecuritiesView.render_page(service)


if __name__ == "__main__":
    main()
