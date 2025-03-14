from collections.abc import Generator
from typing import Annotated
from uuid import UUID

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jwt.exceptions import InvalidTokenError
from sqlalchemy.sql import func
from sqlmodel import Session, select

from app import crud
from app.api.utils import verify_password
from app.core.config import settings
from app.core.db import engine
from app.models import Account, Stock, TokenData, Transaction, User
from app.models.generic import DetailItem


def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session


SessionDepAnnotated = Annotated[Session, Depends(get_session)]


def validate_unique_username(session: SessionDepAnnotated, user_in: User):
    if user_in.username:
        statement = select(User).where(
            func.lower(User.username) == func.lower(user_in.username)
        )
        user = session.exec(statement).first()
        if user:
            raise (
                HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=DetailItem(
                        type="username_in_use",
                        loc=["body", "username"],
                        msg="Username already in use",
                    ).model_dump(),
                )
            )


def validate_unique_email(session: SessionDepAnnotated, user_in: User):
    if user_in.email:
        statement = select(User).where(
            func.lower(User.email) == func.lower(user_in.email)
        )
        user = session.exec(statement).first()
        if user:
            raise (
                HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=DetailItem(
                        type="email_in_use",
                        loc=["body", "email"],
                        msg="Email already in user",
                    ).model_dump(),
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


def get_user_or_404(session: SessionDepAnnotated, user_id: int | UUID):
    user_db = crud.get_by_id(User, session, user_id)
    if not user_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return user_db


def get_account_or_404(session: SessionDepAnnotated, account_id: int | UUID):
    account_db = crud.get_by_id(Account, session, account_id)
    if not account_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Account not found"
        )
    return account_db


def get_stock_or_404(session: SessionDepAnnotated, stock_id: int | UUID):
    stock_db = crud.get_by_id(Stock, session, stock_id)
    if not stock_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Stock not found"
        )
    return stock_db


def get_transaction_or_404(session: SessionDepAnnotated, transaction_id: int | UUID):
    transaction_db = crud.get_by_id(Transaction, session, transaction_id)
    if not transaction_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found"
        )
    return transaction_db
