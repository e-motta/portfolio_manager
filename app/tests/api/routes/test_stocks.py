from fastapi import status
from fastapi.testclient import TestClient
from sqlmodel import Session

from app.core.config import settings
from app.tests.utils import create_user, create_account, create_stock, get_token_headers


def test_get_stock_list(
    client: TestClient, session: Session, test_username: str, test_password: str
):
    user = create_user(session, username=test_username, password=test_password)
    account = create_account(session, current_user=user)
    create_stock(session, account=account)
    token_headers = get_token_headers(
        client=client, username=test_username, password=test_password
    )

    r = client.get(
        f"{settings.API_V1_STR}/accounts/{account.id}/stocks",
        headers=token_headers,
    )
    assert r.status_code == status.HTTP_200_OK
    data = r.json()
    assert len(data) == 1


def test_get_stock_detail(
    client: TestClient, session: Session, test_username: str, test_password: str
):
    user = create_user(session, username=test_username, password=test_password)
    account = create_account(session, current_user=user)
    stock = create_stock(session, account=account)
    token_headers = get_token_headers(
        client=client, username=test_username, password=test_password
    )

    r = client.get(
        f"{settings.API_V1_STR}/accounts/{account.id}/stocks/{stock.id}",
        headers=token_headers,
    )
    assert r.status_code == status.HTTP_200_OK
    data = r.json()
    assert data["id"] == stock.id


def test_create_stock(
    client: TestClient, session: Session, test_username: str, test_password: str
):
    user = create_user(session, username=test_username, password=test_password)
    account = create_account(session, current_user=user)
    token_headers = get_token_headers(
        client=client, username=test_username, password=test_password
    )

    body = {
        "name": "new_name",
        "symbol": "NEW",
        "target_allocation": 50,
    }

    r = client.post(
        f"{settings.API_V1_STR}/accounts/{account.id}/stocks/",
        headers=token_headers,
        json=body,
    )
    assert r.status_code == status.HTTP_201_CREATED
    data = r.json()
    assert data["id"] == 1


def test_update_stock(
    client: TestClient, session: Session, test_username: str, test_password: str
):
    user = create_user(session, username=test_username, password=test_password)
    account = create_account(session, current_user=user)
    stock = create_stock(session, account=account)
    token_headers = get_token_headers(
        client=client, username=test_username, password=test_password
    )

    body = {
        "name": "updated_name",
    }

    r = client.patch(
        f"{settings.API_V1_STR}/accounts/{account.id}/stocks/{stock.id}",
        headers=token_headers,
        json=body,
    )
    assert r.status_code == status.HTTP_200_OK
    data = r.json()
    assert data["name"] == "updated_name"


def test_delete_stock(
    client: TestClient, session: Session, test_username: str, test_password: str
):
    user = create_user(session, username=test_username, password=test_password)
    account = create_account(session, current_user=user)
    stock = create_stock(session, account=account)
    token_headers = get_token_headers(
        client=client, username=test_username, password=test_password
    )

    r_delete = client.delete(
        f"{settings.API_V1_STR}/accounts/{account.id}/stocks/{stock.id}",
        headers=token_headers,
    )
    assert r_delete.status_code == status.HTTP_204_NO_CONTENT

    r_get = client.get(
        f"{settings.API_V1_STR}/accounts/{account.id}/stocks/{stock.id}",
        headers=token_headers,
    )
    assert r_get.status_code == status.HTTP_404_NOT_FOUND


# todo: test get existing stock from wrong account
