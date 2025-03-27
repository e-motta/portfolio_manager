from decimal import Decimal

import pytest
from fastapi import Response, status
from fastapi.testclient import TestClient
from sqlmodel import Session

from app.core.config import settings
from app.tests.utils import (
    create_account,
    create_security,
    create_user,
    get_token_headers,
)


@pytest.mark.parametrize(
    "method, endpoint",
    [
        ("get", "/"),
        ("get", "/1"),
        ("post", "/"),
        ("patch", "/1"),
        ("delete", "/1"),
        ("post", "/1/plan"),
    ],
)
def test_account_unauthorized(client: TestClient, method: str, endpoint: str):
    url = f"{settings.API_V1_STR}/{settings.ACCOUNTS_ROUTE_STR}{endpoint}"
    response: Response = getattr(client, method)(url)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.parametrize(
    "method, endpoint, data",
    [
        ("get", "/{account_id}", None),
        ("patch", "/{account_id}", {"name": "new_name"}),
        ("delete", "/{account_id}", None),
        ("post", "/{account_id}/plan", {"new_investment": 1000}),
    ],
)
def test_account_forbidden(
    client: TestClient,
    session: Session,
    normal_user_token_headers: dict[str, str],
    test_username: str,
    test_password: str,
    method: str,
    endpoint: str,
    data: dict | None,
):
    user = create_user(session=session, username=test_username, password=test_password)
    account = create_account(session=session, current_user=user)

    url = f"{settings.API_V1_STR}/{settings.ACCOUNTS_ROUTE_STR}{endpoint.format(account_id=account.id)}"

    request_kwargs = {"headers": normal_user_token_headers}
    if data is not None:
        request_kwargs["json"] = data

    response: Response = getattr(client, method)(url, **request_kwargs)

    assert response.status_code == status.HTTP_403_FORBIDDEN


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
    data = r.json()["data"]
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
    data = r.json()["data"]
    assert data["id"] == str(account.id)


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
    data_post = r_post.json()["data"]
    assert data_post["id"]

    r_get = client.get(
        f"{settings.API_V1_STR}/{settings.ACCOUNTS_ROUTE_STR}/{data_post['id']}",
        headers=token_headers,
    )
    assert r_get.status_code == status.HTTP_200_OK
    data_get = r_get.json()["data"]
    assert data_get["id"] == data_post["id"]


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
    data = r.json()["data"]
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
    assert r_delete.status_code == status.HTTP_200_OK

    r_get = client.get(
        f"{settings.API_V1_STR}/{settings.ACCOUNTS_ROUTE_STR}/{account.id}",
        headers=token_headers,
    )
    assert r_get.status_code == status.HTTP_404_NOT_FOUND


def test_account_deleted_when_user_deleted(
    client: TestClient,
    session: Session,
    test_username: str,
    test_password: str,
    admin_token_headers: dict[str, str],
):
    user = create_user(session, username=test_username, password=test_password)
    account = create_account(session, current_user=user)

    r_get = client.get(
        f"{settings.API_V1_STR}/{settings.ACCOUNTS_ROUTE_STR}/{account.id}",
        headers=admin_token_headers,
    )
    assert r_get.status_code == status.HTTP_200_OK

    session.delete(user)
    session.commit()

    r_get_deleted = client.get(
        f"{settings.API_V1_STR}/{settings.ACCOUNTS_ROUTE_STR}/{account.id}",
        headers=admin_token_headers,
    )
    assert r_get_deleted.status_code == status.HTTP_404_NOT_FOUND


def test_create_allocation_plan(
    client: TestClient, session: Session, test_username: str, test_password: str
):
    user = create_user(session, username=test_username, password=test_password)
    account = create_account(session, current_user=user)
    token_headers = get_token_headers(
        client=client, username=test_username, password=test_password
    )
    create_security(session, account=account, target_allocation=Decimal("100"))

    body = {
        "new_investment": 1000,
    }

    r = client.post(
        f"{settings.API_V1_STR}/{settings.ACCOUNTS_ROUTE_STR}/{account.id}/plan",
        headers=token_headers,
        json=body,
    )

    assert r.status_code == status.HTTP_200_OK
    data = r.json()["data"]
    assert data[0]["needed_investment"] == "1000.00000000"
