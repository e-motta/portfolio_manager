from fastapi import status
from fastapi.testclient import TestClient
from sqlmodel import Session

from app.core.config import settings
from app.tests.utils import create_user


def test_user_unauthorized(client: TestClient):
    r_get_list = client.get(f"{settings.API_V1_STR}/{settings.USERS_ROUTE_STR}/")
    assert r_get_list.status_code == status.HTTP_401_UNAUTHORIZED
    r_get_detail = client.get(f"{settings.API_V1_STR}/{settings.USERS_ROUTE_STR}/1")
    assert r_get_detail.status_code == status.HTTP_401_UNAUTHORIZED
    r_post = client.post(f"{settings.API_V1_STR}/{settings.USERS_ROUTE_STR}/")
    assert r_post.status_code == status.HTTP_401_UNAUTHORIZED
    r_patch = client.patch(f"{settings.API_V1_STR}/{settings.USERS_ROUTE_STR}/1")
    assert r_patch.status_code == status.HTTP_401_UNAUTHORIZED
    r_delete = client.delete(f"{settings.API_V1_STR}/{settings.USERS_ROUTE_STR}/1")
    assert r_delete.status_code == status.HTTP_401_UNAUTHORIZED
    r_recover = client.patch(
        f"{settings.API_V1_STR}/{settings.USERS_ROUTE_STR}/1/recover"
    )
    assert r_recover.status_code == status.HTTP_401_UNAUTHORIZED


def test_user_forbidden(client: TestClient, normal_user_token_headers: dict[str, str]):
    r_get_list = client.get(
        f"{settings.API_V1_STR}/{settings.USERS_ROUTE_STR}/",
        headers=normal_user_token_headers,
    )
    assert r_get_list.status_code == status.HTTP_403_FORBIDDEN
    r_get_detail = client.get(
        f"{settings.API_V1_STR}/{settings.USERS_ROUTE_STR}/1",
        headers=normal_user_token_headers,
    )
    assert r_get_detail.status_code == status.HTTP_403_FORBIDDEN
    r_post = client.post(
        f"{settings.API_V1_STR}/{settings.USERS_ROUTE_STR}/",
        headers=normal_user_token_headers,
    )
    assert r_post.status_code == status.HTTP_403_FORBIDDEN
    r_patch = client.patch(
        f"{settings.API_V1_STR}/{settings.USERS_ROUTE_STR}/1",
        headers=normal_user_token_headers,
    )
    assert r_patch.status_code == status.HTTP_403_FORBIDDEN
    r_delete = client.delete(
        f"{settings.API_V1_STR}/{settings.USERS_ROUTE_STR}/1",
        headers=normal_user_token_headers,
    )
    assert r_delete.status_code == status.HTTP_403_FORBIDDEN
    r_recover = client.patch(
        f"{settings.API_V1_STR}/{settings.USERS_ROUTE_STR}/1/recover",
        headers=normal_user_token_headers,
    )
    assert r_recover.status_code == status.HTTP_403_FORBIDDEN


def test_read_user_list(client: TestClient, admin_token_headers: dict[str, str]):
    r = client.get(
        f"{settings.API_V1_STR}/{settings.USERS_ROUTE_STR}/",
        headers=admin_token_headers,
    )
    assert r.status_code == status.HTTP_200_OK
    data = r.json()
    assert len(data) == 1
    assert "username" in data[0]


def test_read_user_detail(client: TestClient, admin_token_headers: dict[str, str]):
    r = client.get(
        f"{settings.API_V1_STR}/{settings.USERS_ROUTE_STR}/1",
        headers=admin_token_headers,
    )
    assert r.status_code == status.HTTP_200_OK
    data = r.json()
    assert "username" in data


def test_read_user_detail_not_found(
    client: TestClient, admin_token_headers: dict[str, str]
):
    r = client.get(
        f"{settings.API_V1_STR}/{settings.USERS_ROUTE_STR}/99",
        headers=admin_token_headers,
    )
    assert r.status_code == status.HTTP_404_NOT_FOUND


def test_create_user(client: TestClient, admin_token_headers: dict[str, str]):
    body = {
        "username": "new_username",
        "email": "new_email@example.com",
        "first_name": "first",
        "last_name": "last",
        "password": "password",
    }
    r = client.post(
        f"{settings.API_V1_STR}/{settings.USERS_ROUTE_STR}/",
        headers=admin_token_headers,
        json=body,
    )
    assert r.status_code == status.HTTP_201_CREATED
    data = r.json()
    assert data["username"] == "new_username"


def test_update_user(
    client: TestClient, session: Session, admin_token_headers: dict[str, str]
):
    user = create_user(
        session=session,
        username="username",
        email="email@example.com",
        password="password",
    )

    body = {"username": "new_username"}
    r = client.patch(
        f"{settings.API_V1_STR}/{settings.USERS_ROUTE_STR}/{user.id}",
        headers=admin_token_headers,
        json=body,
    )
    assert r.status_code == status.HTTP_200_OK
    data = r.json()
    assert data["username"] == "new_username"


def test_hard_delete_user(
    client: TestClient, session: Session, admin_token_headers: dict[str, str]
):
    user = create_user(session=session)

    r = client.delete(
        f"{settings.API_V1_STR}/{settings.USERS_ROUTE_STR}/{user.id}",
        headers=admin_token_headers,
        params={"hard_delete": True},
    )
    assert r.status_code == status.HTTP_204_NO_CONTENT

    r = client.get(
        f"{settings.API_V1_STR}/{settings.USERS_ROUTE_STR}/{user.id}",
        headers=admin_token_headers,
    )
    assert r.status_code == status.HTTP_404_NOT_FOUND


def test_soft_delete_user(
    client: TestClient, session: Session, admin_token_headers: dict[str, str]
):
    user = create_user(session=session)

    r = client.delete(
        f"{settings.API_V1_STR}/{settings.USERS_ROUTE_STR}/{user.id}",
        headers=admin_token_headers,
    )
    assert r.status_code == status.HTTP_204_NO_CONTENT

    r = client.get(
        f"{settings.API_V1_STR}/{settings.USERS_ROUTE_STR}/{user.id}",
        headers=admin_token_headers,
    )
    assert r.status_code == status.HTTP_200_OK
    data = r.json()
    assert data["is_active"] == False
    assert data["deleted_at"]


def test_recover_soft_deletion(
    client: TestClient, session: Session, admin_token_headers: dict[str, str]
):
    user = create_user(session=session)

    r = client.delete(
        f"{settings.API_V1_STR}/{settings.USERS_ROUTE_STR}/{user.id}",
        headers=admin_token_headers,
    )
    assert r.status_code == status.HTTP_204_NO_CONTENT

    r = client.get(
        f"{settings.API_V1_STR}/{settings.USERS_ROUTE_STR}/{user.id}",
        headers=admin_token_headers,
    )
    assert r.status_code == status.HTTP_200_OK
    data = r.json()
    assert not data["is_active"]
    assert data["deleted_at"]

    r = client.patch(
        f"{settings.API_V1_STR}/{settings.USERS_ROUTE_STR}/{user.id}/recover",
        headers=admin_token_headers,
    )
    assert r.status_code == status.HTTP_200_OK
    data = r.json()
    assert data["is_active"]
    assert not data["deleted_at"]


# todo: add tests for register and /me routes
# todo: add tests for limitations (value lengths, etc.)
# todo: implement that related accounts are deleted (cascade)
