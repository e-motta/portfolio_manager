from datetime import datetime
from decimal import Decimal
from uuid import UUID

from sqlalchemy import DECIMAL, Column
from sqlmodel import Field, Relationship, SQLModel

from app.models.generic import BaseTableModel
from app.models.stocks import Stock


class AccountBase(SQLModel):
    name: str
    buying_power: Decimal = Field(sa_column=Column(DECIMAL(12, 2)), ge=0)


class Account(BaseTableModel, AccountBase, table=True):
    __tablename__: str = "accounts"

    user_id: UUID = Field(foreign_key="users.id", ondelete="CASCADE")
    user: "User" = Relationship(back_populates="accounts")  # type: ignore
    stocks: list[Stock] = Relationship(back_populates="account", cascade_delete=True)


class AccountCreate(AccountBase):
    pass


class AccountRead(AccountBase):
    user_id: UUID
    stocks: list[Stock]
    id: UUID
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None


class AccountUpdate(SQLModel):
    name: str | None = None
    buying_power: Decimal | None = Field(
        sa_column=Column(DECIMAL(12, 2)), default=None, ge=0
    )
