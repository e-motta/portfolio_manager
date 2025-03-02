from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, create_engine
from sqlmodel.pool import StaticPool

from app.api.dependencies import get_session
from app.core.config import settings
from app.main import app
from app.models import SQLModel
from app.tests.utils import create_user, generate_random_string, get_token_headers


@pytest.fixture(scope="function", autouse=True)
def session() -> Generator[Session, None, None]:
    engine = create_engine(
        settings.TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(scope="function")
def client(session) -> Generator[TestClient, None, None]:
    def override_get_session():
        return session

    app.dependency_overrides[get_session] = override_get_session
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def admin_token_headers(client: TestClient, session: Session) -> dict[str, str]:
    username = "admin"
    email = "admin@example.com"
    password = "password"
    create_user(
        session=session,
        username=username,
        email=email,
        password=password,
        is_admin=True,
    )
    token_headers = get_token_headers(
        client=client, username=username, password=password
    )
    return token_headers


@pytest.fixture(scope="function")
def normal_user_token_headers(client: TestClient, session: Session) -> dict[str, str]:
    username = "normal_user"
    email = "normal_user@example.com"
    password = "password"
    create_user(
        session=session,
        username=username,
        email=email,
        password=password,
        is_admin=False,
    )
    token_headers = get_token_headers(
        client=client, username=username, password=password
    )
    return token_headers


@pytest.fixture(scope="function")
def test_username():
    return generate_random_string()


@pytest.fixture(scope="function")
def test_password():
    return generate_random_string()
