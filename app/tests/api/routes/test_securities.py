from fastapi import status
from fastapi.testclient import TestClient
from sqlmodel import Session

from app.core.config import settings
from app.tests.utils import (
    create_account,
    create_security,
    create_user,
    get_token_headers,
)


def test_security_unauthorized(
    client: TestClient,
    session: Session,
    test_username: str,
    test_password: str,
):
    user = create_user(session, username=test_username, password=test_password)
    account = create_account(session, current_user=user)
    security = create_security(session, account=account)

    body = {
        "name": "new_name",
        "symbol": "NEW",
        "target_allocation": 50,
    }

    r_get_detail = client.get(
        f"{settings.API_V1_STR}/{settings.ACCOUNTS_ROUTE_STR}/{account.id}/{settings.SECURITIES_ROUTE_STR}/{security.id}",
    )
    assert r_get_detail.status_code == status.HTTP_401_UNAUTHORIZED
    r_get_list = client.get(
        f"{settings.API_V1_STR}/{settings.ACCOUNTS_ROUTE_STR}/{account.id}/{settings.SECURITIES_ROUTE_STR}",
    )
    assert r_get_list.status_code == status.HTTP_401_UNAUTHORIZED
    r_create = client.post(
        f"{settings.API_V1_STR}/{settings.ACCOUNTS_ROUTE_STR}/{account.id}/{settings.SECURITIES_ROUTE_STR}",
        json=body,
    )
    assert r_create.status_code == status.HTTP_401_UNAUTHORIZED
    r_udpate = client.patch(
        f"{settings.API_V1_STR}/{settings.ACCOUNTS_ROUTE_STR}/{account.id}/{settings.SECURITIES_ROUTE_STR}/{security.id}",
        json=body,
    )
    assert r_udpate.status_code == status.HTTP_401_UNAUTHORIZED
    r_delete = client.delete(
        f"{settings.API_V1_STR}/{settings.ACCOUNTS_ROUTE_STR}/{account.id}/{settings.SECURITIES_ROUTE_STR}/{security.id}",
    )
    assert r_delete.status_code == status.HTTP_401_UNAUTHORIZED


def test_security_forbidden(
    client: TestClient,
    session: Session,
    test_username: str,
    test_password: str,
    normal_user_token_headers: dict[str, str],
):
    user = create_user(session, username=test_username, password=test_password)
    account = create_account(session, current_user=user)
    security = create_security(session, account=account)

    body = {
        "name": "new_name",
        "symbol": "NEW",
        "target_allocation": 50,
    }

    r_get_detail = client.get(
        f"{settings.API_V1_STR}/{settings.ACCOUNTS_ROUTE_STR}/{account.id}/{settings.SECURITIES_ROUTE_STR}/{security.id}",
        headers=normal_user_token_headers,
    )
    assert r_get_detail.status_code == status.HTTP_403_FORBIDDEN
    r_get_list = client.get(
        f"{settings.API_V1_STR}/{settings.ACCOUNTS_ROUTE_STR}/{account.id}/{settings.SECURITIES_ROUTE_STR}",
        headers=normal_user_token_headers,
    )
    assert r_get_list.status_code == status.HTTP_403_FORBIDDEN
    r_create = client.post(
        f"{settings.API_V1_STR}/{settings.ACCOUNTS_ROUTE_STR}/{account.id}/{settings.SECURITIES_ROUTE_STR}",
        headers=normal_user_token_headers,
        json=body,
    )
    assert r_create.status_code == status.HTTP_403_FORBIDDEN
    r_udpate = client.patch(
        f"{settings.API_V1_STR}/{settings.ACCOUNTS_ROUTE_STR}/{account.id}/{settings.SECURITIES_ROUTE_STR}/{security.id}",
        headers=normal_user_token_headers,
        json=body,
    )
    assert r_udpate.status_code == status.HTTP_403_FORBIDDEN
    r_delete = client.delete(
        f"{settings.API_V1_STR}/{settings.ACCOUNTS_ROUTE_STR}/{account.id}/{settings.SECURITIES_ROUTE_STR}/{security.id}",
        headers=normal_user_token_headers,
    )
    assert r_delete.status_code == status.HTTP_403_FORBIDDEN


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
        "target_allocation": 50,
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
        "target_allocation": -1,
    }

    r = client.patch(
        f"{settings.API_V1_STR}/{settings.ACCOUNTS_ROUTE_STR}/{account.id}/{settings.SECURITIES_ROUTE_STR}/{security.id}",
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
