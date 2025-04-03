from api_client import APIClient
from repositories.accounts import AccountsRepository
from services.accounts import AccountsService
from views.accounts import AccountsView


def render_accounts_page(client: APIClient):
    repository = AccountsRepository(client)
    service = AccountsService(repository)
    AccountsView.render_page(service)
