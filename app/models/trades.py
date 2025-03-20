from datetime import datetime
from decimal import Decimal
from enum import Enum
from uuid import UUID

from sqlmodel import Field, Relationship, SQLModel

from app.models.generic import BaseTableModel


class TradeType(str, Enum):
    BUY = "buy"
    SELL = "sell"


class TradeBase(SQLModel):
    type: TradeType
    quantity: Decimal = Field(max_digits=14, decimal_places=4, ge=0)
    price: Decimal = Field(max_digits=12, decimal_places=2, ge=0)
    stock_id: UUID


class Trade(BaseTableModel, TradeBase, table=True):
    __tablename__: str = "trades"

    account_id: UUID = Field(foreign_key="accounts.id", ondelete="CASCADE")
    account: "Account" = Relationship(back_populates="trades")  # type: ignore
    stock_id: UUID = Field(foreign_key="stocks.id", ondelete="CASCADE")
    stock: "Stock" = Relationship(back_populates="trades")  # type: ignore


class TradeCreate(TradeBase):
    pass


class TradeRead(TradeBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None
    account_id: UUID


class TradeUpdate(SQLModel):
    quantity: Decimal | None = Field(
        max_digits=14, decimal_places=4, default=None, ge=0
    )
    price: Decimal | None = Field(max_digits=12, decimal_places=2, default=None, ge=0)
    stock_id: UUID | None = None
