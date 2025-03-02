from fastapi import status
from fastapi.testclient import TestClient
from sqlmodel import Session

from app.core.config import settings
from app.tests.utils import create_account, create_user, get_token_headers


def test_account_unauthorized(client: TestClient):
    r_get_list = client.get(f"{settings.API_V1_STR}/{settings.ACCOUNTS_ROUTE_STR}/")
    assert r_get_list.status_code == status.HTTP_401_UNAUTHORIZED
    r_get_detail = client.get(f"{settings.API_V1_STR}/{settings.ACCOUNTS_ROUTE_STR}/1")
    assert r_get_detail.status_code == status.HTTP_401_UNAUTHORIZED
    r_post = client.post(f"{settings.API_V1_STR}/{settings.ACCOUNTS_ROUTE_STR}/")
    assert r_post.status_code == status.HTTP_401_UNAUTHORIZED
    r_patch = client.patch(f"{settings.API_V1_STR}/{settings.ACCOUNTS_ROUTE_STR}/1")
    assert r_patch.status_code == status.HTTP_401_UNAUTHORIZED
    r_delete = client.delete(f"{settings.API_V1_STR}/{settings.ACCOUNTS_ROUTE_STR}/1")
    assert r_delete.status_code == status.HTTP_401_UNAUTHORIZED


def test_account_forbidden(
    client: TestClient,
    session: Session,
    normal_user_token_headers: dict[str, str],
    test_username: str,
    test_password: str,
):
    user = create_user(session=session, username=test_username, password=test_password)
    create_account(session=session, current_user=user)

    r_get_detail = client.get(
        f"{settings.API_V1_STR}/{settings.ACCOUNTS_ROUTE_STR}/1",
        headers=normal_user_token_headers,
    )
    assert r_get_detail.status_code == status.HTTP_403_FORBIDDEN
    r_patch = client.patch(
        f"{settings.API_V1_STR}/{settings.ACCOUNTS_ROUTE_STR}/1",
        headers=normal_user_token_headers,
        json={"name": "new_name"},
    )
    assert r_patch.status_code == status.HTTP_403_FORBIDDEN
    r_delete = client.delete(
        f"{settings.API_V1_STR}/{settings.ACCOUNTS_ROUTE_STR}/1",
        headers=normal_user_token_headers,
    )
    assert r_delete.status_code == status.HTTP_403_FORBIDDEN


def test_get_account_list(
    client: TestClient, session: Session, test_username: str, test_password: str
):
    user = create_user(session, username=test_username, password=test_password)
    create_account(session, current_user=user)
    token_headers = get_token_headers(
        client=client, username=test_username, password=test_password
    )

    r = client.get(
        f"{settings.API_V1_STR}/{settings.ACCOUNTS_ROUTE_STR}", headers=token_headers
    )
    assert r.status_code == status.HTTP_200_OK
    data = r.json()
    assert len(data) == 1


def test_get_account_detail(
    client: TestClient, session: Session, test_username: str, test_password: str
):
    user = create_user(session, username=test_username, password=test_password)
    account = create_account(session, current_user=user)
    token_headers = get_token_headers(
        client=client, username=test_username, password=test_password
    )

    r = client.get(
        f"{settings.API_V1_STR}/{settings.ACCOUNTS_ROUTE_STR}/{account.id}",
        headers=token_headers,
    )
    assert r.status_code == status.HTTP_200_OK


def test_create_account(
    client: TestClient, session: Session, test_username: str, test_password: str
):
    create_user(session, username=test_username, password=test_password)
    token_headers = get_token_headers(
        client, username=test_username, password=test_password
    )

    body = {
        "name": "account_name",
        "buying_power": 1000,
    }
    r_post = client.post(
        f"{settings.API_V1_STR}/{settings.ACCOUNTS_ROUTE_STR}/",
        headers=token_headers,
        json=body,
    )
    assert r_post.status_code == status.HTTP_201_CREATED
    data_post = r_post.json()
    assert data_post["id"] == 1

    r_get = client.get(
        f"{settings.API_V1_STR}/{settings.ACCOUNTS_ROUTE_STR}/{data_post['id']}",
        headers=token_headers,
    )
    assert r_get.status_code == status.HTTP_200_OK
    data_get = r_get.json()
    assert data_get["id"] == 1


def test_update_account(
    client: TestClient, session: Session, test_username: str, test_password: str
):
    user = create_user(session, username=test_username, password=test_password)
    account = create_account(session, current_user=user)
    token_headers = get_token_headers(
        client=client, username=test_username, password=test_password
    )

    body = {
        "name": "new_account_name",
    }

    r = client.patch(
        f"{settings.API_V1_STR}/{settings.ACCOUNTS_ROUTE_STR}/{account.id}",
        headers=token_headers,
        json=body,
    )
    assert r.status_code == status.HTTP_200_OK
    data = r.json()
    assert data["name"] == "new_account_name"


def test_delete_account(
    client: TestClient, session: Session, test_username: str, test_password: str
):
    user = create_user(session, username=test_username, password=test_password)
    account = create_account(session, current_user=user)
    token_headers = get_token_headers(
        client=client, username=test_username, password=test_password
    )

    r_delete = client.delete(
        f"{settings.API_V1_STR}/{settings.ACCOUNTS_ROUTE_STR}/{account.id}",
        headers=token_headers,
    )
    assert r_delete.status_code == status.HTTP_204_NO_CONTENT

    r_get = client.get(
        f"{settings.API_V1_STR}/{settings.ACCOUNTS_ROUTE_STR}/{account.id}",
        headers=token_headers,
    )
    assert r_get.status_code == status.HTTP_404_NOT_FOUND


# todo: implement/test that related stocks are deleted (cascade)
