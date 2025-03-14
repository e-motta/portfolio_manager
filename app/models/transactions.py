from datetime import datetime
from decimal import Decimal
from enum import Enum
from uuid import UUID

from sqlalchemy import DECIMAL, Column
from sqlmodel import Field, Relationship, SQLModel

from app.models.generic import BaseTableModel


class TransactionType(str, Enum):
    BUY = "buy"
    SELL = "sell"


class TransactionBase(SQLModel):
    type: TransactionType
    quantity: Decimal = Field(sa_column=Column(DECIMAL(14, 4)), ge=0)
    price: Decimal = Field(sa_column=Column(DECIMAL(12, 2)), ge=0)
    stock_id: UUID


class Transaction(BaseTableModel, TransactionBase, table=True):
    __tablename__: str = "transactions"

    account_id: UUID = Field(foreign_key="accounts.id", ondelete="CASCADE")
    account: "Account" = Relationship(back_populates="transactions")  # type: ignore


class TransactionCreate(TransactionBase):
    pass


class TransactionRead(TransactionBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None
    account_id: UUID


class TransactionUpdate(SQLModel):
    quantity: Decimal | None = Field(
        sa_column=Column(DECIMAL(14, 4)), default=None, ge=0
    )
    price: Decimal | None = Field(sa_column=Column(DECIMAL(12, 2)), default=None, ge=0)
    stock_id: UUID | None = None
