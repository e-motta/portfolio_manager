from api_client import APIClient
from repositories.securities import SecuritiesRepository
from services.securities import SecuritiesService
from utils import require_auth
from views.securities import SecuritiesView


@require_auth
def render_securities_page(client: APIClient):
    repository = SecuritiesRepository(client)
    service = SecuritiesService(repository)
    SecuritiesView.render_page(service)
