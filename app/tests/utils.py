from fastapi.testclient import TestClient
from sqlmodel import Session

from app import crud
from app.core.config import settings
from app.models import User, UserCreate


def create_user(
    *,
    session: Session,
    username: str = "username",
    email: str = "email@example.com",
    password: str = "password",
    is_admin: bool = False,
) -> User:
    user_in_create = UserCreate(
        username=username,
        email=email,
        first_name="first",
        last_name="last",
        password=password,
        is_admin=is_admin,
    )
    user = crud.users.create(session, user_in_create)
    if not user:
        raise ValueError("User could not be created")
    return user


def get_token_headers(
    *, client: TestClient, username: str, password: str
) -> dict[str, str]:
    data = {"username": username, "password": password}

    r = client.post(f"{settings.API_V1_STR}/auth/token", data=data)
    response = r.json()
    auth_token = response["access_token"]
    headers = {"Authorization": f"Bearer {auth_token}"}
    return headers
