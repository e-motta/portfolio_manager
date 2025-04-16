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
from app.constants.messages import Messages
from app.core.config import settings
from app.core.db import engine
from app.models.accounts import Account
from app.models.auth import TokenData
from app.models.generic import DetailItem
from app.models.ledger import Ledger
from app.models.securities import Security
from app.models.trades import Trade
from app.models.users import User


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
                        msg=Messages.User.USERNAME_IN_USE,
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
                        msg=Messages.User.EMAIL_IN_USE,
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
        detail=DetailItem(
            type="unauthorized", loc=[], msg=Messages.Auth.INVALID_CREDENTIALS
        ).model_dump(),
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
            status_code=status.HTTP_403_FORBIDDEN, detail=Messages.Auth.FORBIDDEN
        )


IsAdminDep = Depends(is_admin)


def get_user_or_404(session: SessionDepAnnotated, user_id: int | UUID):
    user_db = crud.get_by_id(User, session, user_id)
    if not user_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=Messages.User.NOT_FOUND
        )
    return user_db


def get_account_or_404(session: SessionDepAnnotated, account_id: int | UUID):
    account_db = crud.get_by_id(Account, session, account_id)
    if not account_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=Messages.Account.NOT_FOUND
        )
    return account_db


def get_security_or_404(session: SessionDepAnnotated, security_id: int | UUID):
    security_db = crud.get_by_id(Security, session, security_id)
    if not security_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=Messages.Security.NOT_FOUND
        )
    return security_db


def get_trade_or_404(session: SessionDepAnnotated, trade_id: int | UUID):
    trade_db = crud.get_by_id(Trade, session, trade_id)
    if not trade_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=Messages.Trade.NOT_FOUND
        )
    return trade_db


def get_ledger_item_or_404(session: SessionDepAnnotated, ledger_id: int | UUID):
    ledger_item_db = crud.get_by_id(Ledger, session, ledger_id)
    if not ledger_item_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=Messages.Ledger.NOT_FOUND
        )
    return ledger_item_db
