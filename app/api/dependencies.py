from collections.abc import Generator
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jwt.exceptions import InvalidTokenError
from sqlmodel import Session, select

from app.api.utils import verify_password
from app.core.config import settings
from app.core.db import engine
from app.models import TokenData, User, UserBase


def get_db() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session


SessionDepAnnotated = Annotated[Session, Depends(get_db)]


def validate_unique_username(session: SessionDepAnnotated, user_in: UserBase):
    statement = select(User).where(User.username == user_in.username)
    user = session.exec(statement).first()
    if user:
        raise (
            HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="Username already in use"
            )
        )


def validate_unique_email(session: SessionDepAnnotated, user_in: UserBase):
    statement = select(User).where(User.email == user_in.email)
    user = session.exec(statement).first()
    if user:
        raise (
            HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="Email already in use"
            )
        )


oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/token")
TokenDep = Depends(oauth2_scheme)

AuthFormDepAnnotated = Annotated[OAuth2PasswordRequestForm, Depends()]


def get_current_user(
    token: Annotated[str, TokenDep], session: SessionDepAnnotated
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.AUTH_ALGORITHM]
        )
        username = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except InvalidTokenError:
        raise credentials_exception

    statement = select(User).where(User.username == token_data.username)
    user = session.exec(statement).first()
    if not user:
        raise credentials_exception
    return user


CurrentUserDepAnnotated = Annotated[User, Depends(get_current_user)]


def authenticate_user(session: SessionDepAnnotated, form_data: AuthFormDepAnnotated):
    statement = select(User).where(User.username == form_data.username)
    user = session.exec(statement).first()
    if not user:
        return False
    if not verify_password(form_data.password, user.password_hash):
        return False
    return user


AuthenticateUserDepAnnotated = Annotated[User, Depends(authenticate_user)]


def is_admin(current_user: CurrentUserDepAnnotated):
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions"
        )


IsAdminDep = Depends(is_admin)
