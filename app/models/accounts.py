from datetime import datetime
from decimal import Decimal

from sqlalchemy import DECIMAL, Column
from sqlmodel import Field, Relationship, SQLModel

from .generic import BaseTableModel
from .stocks import Stock


class AccountBase(SQLModel):
    name: str
    buying_power: Decimal = Field(sa_column=Column(DECIMAL(12, 2)))


class Account(BaseTableModel, AccountBase, table=True):
    __tablename__: str = "accounts"

    user_id: int = Field(foreign_key="users.id")
    user: "User" = Relationship(back_populates="accounts")  # type: ignore
    stocks: list[Stock] = Relationship(back_populates="account")


class AccountCreate(AccountBase):
    pass


class AccountRead(AccountBase):
    user_id: int
    stocks: list[Stock]
    id: int
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None


class AccountUpdate(SQLModel):
    name: str | None = None
    buying_power: Decimal | None = Field(sa_column=Column(DECIMAL(12, 2)), default=None)
