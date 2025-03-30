from decimal import Decimal

import pytest
from fastapi import Response, status
from fastapi.testclient import TestClient
from sqlmodel import Session

from app import crud
from app.core.config import settings
from app.tests.utils import (
    create_account,
    create_security,
    create_user,
    get_token_headers,
)


@pytest.mark.parametrize(
    "method, endpoint, has_body",
    [
        ("get", "/{security_id}", False),
        ("get", "", False),
        ("post", "", True),
        ("patch", "/{security_id}", True),
        ("delete", "/{security_id}", False),
    ],
)
def test_security_unauthorized(
    client: TestClient,
    session: Session,
    test_username: str,
    test_password: str,
    method: str,
    endpoint: str,
    has_body: bool,
):
    user = create_user(session, username=test_username, password=test_password)
    account = create_account(session, current_user=user)
    security = create_security(session, account=account)

    url = f"{settings.API_V1_STR}/{settings.ACCOUNTS_ROUTE_STR}/{account.id}/{settings.SECURITIES_ROUTE_STR}{endpoint.format(security_id=security.id)}"

    request_kwargs = {}
    if has_body:
        request_kwargs["json"] = {
            "name": "new_name",
            "symbol": "NEW",
            "target_allocation": 50,
        }

    response: Response = getattr(client, method)(url, **request_kwargs)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.parametrize(
    "method, endpoint, has_body",
    [
        ("get", "/{security_id}", False),
        ("get", "", False),
        ("post", "", True),
        ("patch", "/{security_id}", True),
        ("delete", "/{security_id}", False),
    ],
)
def test_security_forbidden(
    client: TestClient,
    session: Session,
    test_username: str,
    test_password: str,
    normal_user_token_headers: dict[str, str],
    method: str,
    endpoint: str,
    has_body: bool,
):
    user = create_user(session, username=test_username, password=test_password)
    account = create_account(session, current_user=user)
    security = create_security(session, account=account)

    url = f"{settings.API_V1_STR}/{settings.ACCOUNTS_ROUTE_STR}/{account.id}/{settings.SECURITIES_ROUTE_STR}{endpoint}".replace(
        "{security_id}", str(security.id)
    )

    request_kwargs: dict = {"headers": normal_user_token_headers}
    if has_body:
        request_kwargs["json"] = {
            "name": "new_name",
            "symbol": "NEW",
            "target_allocation": "0.5",
        }

    response: Response = getattr(client, method)(url, **request_kwargs)

    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_get_security_list(
    client: TestClient, session: Session, test_username: str, test_password: str
):
    user = create_user(session, username=test_username, password=test_password)
    account = create_account(session, current_user=user)
    create_security(session, account=account)
    token_headers = get_token_headers(
        client=client, username=test_username, password=test_password
    )

    r = client.get(
        f"{settings.API_V1_STR}/{settings.ACCOUNTS_ROUTE_STR}/{account.id}/{settings.SECURITIES_ROUTE_STR}",
        headers=token_headers,
    )
    assert r.status_code == status.HTTP_200_OK
    data = r.json()["data"]
    assert len(data) == 1


def test_get_security_detail(
    client: TestClient, session: Session, test_username: str, test_password: str
):
    user = create_user(session, username=test_username, password=test_password)
    account = create_account(session, current_user=user)
    security = create_security(session, account=account)
    token_headers = get_token_headers(
        client=client, username=test_username, password=test_password
    )

    r = client.get(
        f"{settings.API_V1_STR}/{settings.ACCOUNTS_ROUTE_STR}/{account.id}/{settings.SECURITIES_ROUTE_STR}/{security.id}",
        headers=token_headers,
    )
    assert r.status_code == status.HTTP_200_OK
    data = r.json()["data"]
    assert data["id"] == str(security.id)


def test_create_security(
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
        "target_allocation": "0.5",
    }

    r = client.post(
        f"{settings.API_V1_STR}/{settings.ACCOUNTS_ROUTE_STR}/{account.id}/{settings.SECURITIES_ROUTE_STR}/",
        headers=token_headers,
        json=body,
    )
    assert r.status_code == status.HTTP_201_CREATED
    data = r.json()["data"]
    assert data["id"]


def test_create_security_negative_target_allocation(
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
        "target_allocation": -1,
    }

    r = client.post(
        f"{settings.API_V1_STR}/{settings.ACCOUNTS_ROUTE_STR}/{account.id}/{settings.SECURITIES_ROUTE_STR}/",
        headers=token_headers,
        json=body,
    )
    assert r.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_create_security_excessive_target_allocation(
    client: TestClient, session: Session, test_username: str, test_password: str
):
    user = create_user(session, username=test_username, password=test_password)
    account = create_account(session, current_user=user)
    create_security(session, account=account, target_allocation=Decimal("1"))
    token_headers = get_token_headers(
        client=client, username=test_username, password=test_password
    )

    body = {
        "name": "new_name",
        "symbol": "NEW",
        "target_allocation": 10,
    }

    r = client.post(
        f"{settings.API_V1_STR}/{settings.ACCOUNTS_ROUTE_STR}/{account.id}/{settings.SECURITIES_ROUTE_STR}/",
        headers=token_headers,
        json=body,
    )
    assert r.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_update_security(
    client: TestClient, session: Session, test_username: str, test_password: str
):
    user = create_user(session, username=test_username, password=test_password)
    account = create_account(session, current_user=user)
    security = create_security(session, account=account)
    token_headers = get_token_headers(
        client=client, username=test_username, password=test_password
    )

    body = {
        "name": "updated_name",
    }

    r = client.patch(
        f"{settings.API_V1_STR}/{settings.ACCOUNTS_ROUTE_STR}/{account.id}/{settings.SECURITIES_ROUTE_STR}/{security.id}",
        headers=token_headers,
        json=body,
    )
    assert r.status_code == status.HTTP_200_OK
    data = r.json()["data"]
    assert data["name"] == "updated_name"


def test_update_security_negative_target_allocation(
    client: TestClient, session: Session, test_username: str, test_password: str
):
    user = create_user(session, username=test_username, password=test_password)
    account = create_account(session, current_user=user)
    security = create_security(session, account=account)
    token_headers = get_token_headers(
        client=client, username=test_username, password=test_password
    )

    body = {
        "target_allocation": "-1",
    }

    r = client.patch(
        f"{settings.API_V1_STR}/{settings.ACCOUNTS_ROUTE_STR}/{account.id}/{settings.SECURITIES_ROUTE_STR}/{security.id}",
        headers=token_headers,
        json=body,
    )
    assert r.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_update_security_excessive_target_allocation(
    client: TestClient, session: Session, test_username: str, test_password: str
):
    user = create_user(session, username=test_username, password=test_password)
    account = create_account(session, current_user=user)
    create_security(
        session, account=account, symbol="ONE", target_allocation=Decimal("0.9")
    )
    new_sec = create_security(
        session, account=account, symbol="TWO", target_allocation=Decimal("0.1")
    )
    token_headers = get_token_headers(
        client=client, username=test_username, password=test_password
    )

    body = {
        "target_allocation": "0.15",
    }

    r = client.patch(
        f"{settings.API_V1_STR}/{settings.ACCOUNTS_ROUTE_STR}/{account.id}/{settings.SECURITIES_ROUTE_STR}/{new_sec.id}",
        headers=token_headers,
        json=body,
    )
    assert r.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_delete_security(
    client: TestClient, session: Session, test_username: str, test_password: str
):
    user = create_user(session, username=test_username, password=test_password)
    account = create_account(session, current_user=user)
    security = create_security(session, account=account)
    token_headers = get_token_headers(
        client=client, username=test_username, password=test_password
    )

    r_delete = client.delete(
        f"{settings.API_V1_STR}/{settings.ACCOUNTS_ROUTE_STR}/{account.id}/{settings.SECURITIES_ROUTE_STR}/{security.id}",
        headers=token_headers,
    )
    assert r_delete.status_code == status.HTTP_200_OK

    r_get = client.get(
        f"{settings.API_V1_STR}/{settings.ACCOUNTS_ROUTE_STR}/{account.id}/{settings.SECURITIES_ROUTE_STR}/{security.id}",
        headers=token_headers,
    )
    assert r_get.status_code == status.HTTP_404_NOT_FOUND


def test_securities_deleted_when_account_deleted(
    client: TestClient,
    session: Session,
    test_username: str,
    test_password: str,
    admin_token_headers: dict[str, str],
):
    user = create_user(session, username=test_username, password=test_password)
    account = create_account(session, current_user=user)
    security = create_security(session, account=account)

    r_get = client.get(
        f"{settings.API_V1_STR}/{settings.ACCOUNTS_ROUTE_STR}/{account.id}/{settings.SECURITIES_ROUTE_STR}/{security.id}",
        headers=admin_token_headers,
    )
    assert r_get.status_code == status.HTTP_200_OK

    session.delete(account)
    session.commit()

    r_get_deleted = client.get(
        f"{settings.API_V1_STR}/{settings.ACCOUNTS_ROUTE_STR}/{account.id}/{settings.SECURITIES_ROUTE_STR}/{security.id}",
        headers=admin_token_headers,
    )
    assert r_get_deleted.status_code == status.HTTP_404_NOT_FOUND


def test_securities_deleted_when_user_deleted(
    client: TestClient,
    session: Session,
    test_username: str,
    test_password: str,
    admin_token_headers: dict[str, str],
):
    user = create_user(session, username=test_username, password=test_password)
    account = create_account(session, current_user=user)
    security = create_security(session, account=account)

    r_get = client.get(
        f"{settings.API_V1_STR}/{settings.ACCOUNTS_ROUTE_STR}/{account.id}/{settings.SECURITIES_ROUTE_STR}/{security.id}",
        headers=admin_token_headers,
    )
    assert r_get.status_code == status.HTTP_200_OK

    session.delete(user)
    session.commit()

    r_get_deleted = client.get(
        f"{settings.API_V1_STR}/{settings.ACCOUNTS_ROUTE_STR}/{account.id}/{settings.SECURITIES_ROUTE_STR}/{security.id}",
        headers=admin_token_headers,
    )
    assert r_get_deleted.status_code == status.HTTP_404_NOT_FOUND


def test_get_total_target_allocation(session: Session):
    user = create_user(session)
    account = create_account(session, current_user=user)
    create_security(
        session, account=account, symbol="ONE", target_allocation=Decimal("0.1")
    )
    create_security(
        session, account=account, symbol="TWO", target_allocation=Decimal("0.2")
    )
    total = crud.securities.get_total_target_allocation(session, account)

    assert total == Decimal("0.3")
