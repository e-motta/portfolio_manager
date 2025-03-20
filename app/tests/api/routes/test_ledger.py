from decimal import Decimal

from fastapi import status
from fastapi.testclient import TestClient
from sqlmodel import Session

from app.core.config import settings
from app.models.ledger import LedgerType
from app.tests.utils import (
    create_account,
    create_and_process_ledger,
    create_ledger_item,
    create_user,
    get_token_headers,
)


def test_transaction_unauthorized(
    client: TestClient,
    session: Session,
    test_username: str,
    test_password: str,
):
    user = create_user(session, username=test_username, password=test_password)
    account = create_account(session, current_user=user)
    transaction = create_ledger_item(session, account=account)

    body = {
        "type": "deposit",
        "amount": 10,
    }

    r_get_detail = client.get(
        f"{settings.API_V1_STR}/{settings.ACCOUNTS_ROUTE_STR}/{account.id}/{settings.LEDGER_ROUTE_STR}/{transaction.id}",
    )
    assert r_get_detail.status_code == status.HTTP_401_UNAUTHORIZED
    r_get_list = client.get(
        f"{settings.API_V1_STR}/{settings.ACCOUNTS_ROUTE_STR}/{account.id}/{settings.LEDGER_ROUTE_STR}",
    )
    assert r_get_list.status_code == status.HTTP_401_UNAUTHORIZED
    r_create = client.post(
        f"{settings.API_V1_STR}/{settings.ACCOUNTS_ROUTE_STR}/{account.id}/{settings.LEDGER_ROUTE_STR}",
        json=body,
    )
    assert r_create.status_code == status.HTTP_401_UNAUTHORIZED
    r_delete = client.delete(
        f"{settings.API_V1_STR}/{settings.ACCOUNTS_ROUTE_STR}/{account.id}/{settings.LEDGER_ROUTE_STR}/{transaction.id}",
    )
    assert r_delete.status_code == status.HTTP_401_UNAUTHORIZED


def test_transaction_forbidden(
    client: TestClient,
    session: Session,
    test_username: str,
    test_password: str,
    normal_user_token_headers: dict[str, str],
):
    user = create_user(session, username=test_username, password=test_password)
    account = create_account(session, current_user=user)
    transaction = create_ledger_item(session, account=account)

    body = {
        "type": "deposit",
        "amount": 10,
    }

    r_get_detail = client.get(
        f"{settings.API_V1_STR}/{settings.ACCOUNTS_ROUTE_STR}/{account.id}/{settings.LEDGER_ROUTE_STR}/{transaction.id}",
        headers=normal_user_token_headers,
    )
    assert r_get_detail.status_code == status.HTTP_403_FORBIDDEN
    r_get_list = client.get(
        f"{settings.API_V1_STR}/{settings.ACCOUNTS_ROUTE_STR}/{account.id}/{settings.LEDGER_ROUTE_STR}",
        headers=normal_user_token_headers,
    )
    assert r_get_list.status_code == status.HTTP_403_FORBIDDEN
    r_create = client.post(
        f"{settings.API_V1_STR}/{settings.ACCOUNTS_ROUTE_STR}/{account.id}/{settings.LEDGER_ROUTE_STR}",
        headers=normal_user_token_headers,
        json=body,
    )
    assert r_create.status_code == status.HTTP_403_FORBIDDEN
    r_delete = client.delete(
        f"{settings.API_V1_STR}/{settings.ACCOUNTS_ROUTE_STR}/{account.id}/{settings.LEDGER_ROUTE_STR}/{transaction.id}",
        headers=normal_user_token_headers,
    )
    assert r_delete.status_code == status.HTTP_403_FORBIDDEN


def test_get_transaction_list(
    client: TestClient, session: Session, test_username: str, test_password: str
):
    user = create_user(session, username=test_username, password=test_password)
    account = create_account(session, current_user=user)
    create_ledger_item(session, account=account)
    token_headers = get_token_headers(
        client=client, username=test_username, password=test_password
    )

    r = client.get(
        f"{settings.API_V1_STR}/{settings.ACCOUNTS_ROUTE_STR}/{account.id}/{settings.LEDGER_ROUTE_STR}",
        headers=token_headers,
    )
    assert r.status_code == status.HTTP_200_OK
    data = r.json()["data"]
    assert len(data) == 1


def test_get_transaction_detail(
    client: TestClient, session: Session, test_username: str, test_password: str
):
    user = create_user(session, username=test_username, password=test_password)
    account = create_account(session, current_user=user)
    transaction = create_ledger_item(session, account=account)
    token_headers = get_token_headers(
        client=client, username=test_username, password=test_password
    )

    r = client.get(
        f"{settings.API_V1_STR}/{settings.ACCOUNTS_ROUTE_STR}/{account.id}/{settings.LEDGER_ROUTE_STR}/{transaction.id}",
        headers=token_headers,
    )
    assert r.status_code == status.HTTP_200_OK
    data = r.json()["data"]
    assert data["id"] == str(transaction.id)


def test_create_ledger_item(
    client: TestClient, session: Session, test_username: str, test_password: str
):
    user = create_user(session, username=test_username, password=test_password)
    account = create_account(session, current_user=user)
    create_and_process_ledger(
        session, account=account, type_=LedgerType.DEPOSIT, amount=Decimal("1000")
    )

    token_headers = get_token_headers(
        client=client, username=test_username, password=test_password
    )

    body = {
        "type": "deposit",
        "amount": 10,
    }

    r = client.post(
        f"{settings.API_V1_STR}/{settings.ACCOUNTS_ROUTE_STR}/{account.id}/{settings.LEDGER_ROUTE_STR}/",
        headers=token_headers,
        json=body,
    )
    assert r.status_code == status.HTTP_201_CREATED
    data = r.json()["data"]
    assert data["id"]


def test_create_ledger_item_negative_values(
    client: TestClient, session: Session, test_username: str, test_password: str
):
    user = create_user(session, username=test_username, password=test_password)
    account = create_account(session, current_user=user)
    token_headers = get_token_headers(
        client=client, username=test_username, password=test_password
    )

    body_1 = {
        "type": "deposit",
        "amount": -1,
    }

    r_1 = client.post(
        f"{settings.API_V1_STR}/{settings.ACCOUNTS_ROUTE_STR}/{account.id}/{settings.LEDGER_ROUTE_STR}/",
        headers=token_headers,
        json=body_1,
    )
    assert r_1.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    body_2 = {
        "type": "withdrawal",
        "amount": -10,
    }

    r_2 = client.post(
        f"{settings.API_V1_STR}/{settings.ACCOUNTS_ROUTE_STR}/{account.id}/{settings.LEDGER_ROUTE_STR}/",
        headers=token_headers,
        json=body_2,
    )
    assert r_2.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_create_ledger_item_invalid_type(
    client: TestClient, session: Session, test_username: str, test_password: str
):
    user = create_user(session, username=test_username, password=test_password)
    account = create_account(session, current_user=user)
    token_headers = get_token_headers(
        client=client, username=test_username, password=test_password
    )

    body = {
        "type": "invalid_type",
        "amount": 10,
    }

    r = client.post(
        f"{settings.API_V1_STR}/{settings.ACCOUNTS_ROUTE_STR}/{account.id}/{settings.LEDGER_ROUTE_STR}/",
        headers=token_headers,
        json=body,
    )
    assert r.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_delete_transaction(
    client: TestClient, session: Session, test_username: str, test_password: str
):
    user = create_user(session, username=test_username, password=test_password)
    account = create_account(session, current_user=user)
    transaction = create_ledger_item(session, account=account)
    token_headers = get_token_headers(
        client=client, username=test_username, password=test_password
    )

    r_delete = client.delete(
        f"{settings.API_V1_STR}/{settings.ACCOUNTS_ROUTE_STR}/{account.id}/{settings.LEDGER_ROUTE_STR}/{transaction.id}",
        headers=token_headers,
    )
    assert r_delete.status_code == status.HTTP_200_OK

    r_get = client.get(
        f"{settings.API_V1_STR}/{settings.ACCOUNTS_ROUTE_STR}/{account.id}/{settings.LEDGER_ROUTE_STR}/{transaction.id}",
        headers=token_headers,
    )
    assert r_get.status_code == status.HTTP_404_NOT_FOUND


def test_cannot_delete_transaction(
    client: TestClient, session: Session, test_username: str, test_password: str
):
    """Cannot delete deposit if withdrawal would exceed buying power."""
    user = create_user(session, username=test_username, password=test_password)
    account = create_account(session, current_user=user)
    token_headers = get_token_headers(
        client=client, username=test_username, password=test_password
    )

    deposit_transaction = create_ledger_item(
        session, account=account, type_=LedgerType.DEPOSIT
    )
    create_ledger_item(session, account=account, type_=LedgerType.WITHDRAWAL)

    r_delete = client.delete(
        f"{settings.API_V1_STR}/{settings.ACCOUNTS_ROUTE_STR}/{account.id}/{settings.LEDGER_ROUTE_STR}/{deposit_transaction.id}",
        headers=token_headers,
    )
    assert r_delete.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    r_get = client.get(
        f"{settings.API_V1_STR}/{settings.ACCOUNTS_ROUTE_STR}/{account.id}/{settings.LEDGER_ROUTE_STR}/{deposit_transaction.id}",
        headers=token_headers,
    )
    assert r_get.status_code == status.HTTP_200_OK


def test_transactions_deleted_when_account_deleted(
    client: TestClient,
    session: Session,
    test_username: str,
    test_password: str,
    admin_token_headers: dict[str, str],
):
    user = create_user(session, username=test_username, password=test_password)
    account = create_account(session, current_user=user)
    transaction = create_ledger_item(session, account=account)

    r_get = client.get(
        f"{settings.API_V1_STR}/{settings.ACCOUNTS_ROUTE_STR}/{account.id}/{settings.LEDGER_ROUTE_STR}/{transaction.id}",
        headers=admin_token_headers,
    )
    assert r_get.status_code == status.HTTP_200_OK

    session.delete(user)
    session.commit()

    r_get_deleted = client.get(
        f"{settings.API_V1_STR}/{settings.ACCOUNTS_ROUTE_STR}/{account.id}/{settings.LEDGER_ROUTE_STR}/{transaction.id}",
        headers=admin_token_headers,
    )
    assert r_get_deleted.status_code == status.HTTP_404_NOT_FOUND
