from datetime import datetime
from decimal import Decimal
from enum import Enum
from uuid import UUID

from sqlmodel import Field, Relationship, SQLModel

from app.models.generic import BaseTableModel, get_decimal_field


class TradeType(str, Enum):
    BUY = "buy"
    SELL = "sell"


class TradeBase(SQLModel):
    type: TradeType
    quantity: Decimal = get_decimal_field(gt=0)
    price: Decimal = get_decimal_field(gt=0)
    security_id: UUID


class Trade(BaseTableModel, TradeBase, table=True):
    __tablename__: str = "trades"

    account_id: UUID = Field(foreign_key="accounts.id", ondelete="CASCADE")
    account: "Account" = Relationship(back_populates="trades")  # type: ignore
    security_id: UUID = Field(foreign_key="securities.id", ondelete="CASCADE")
    security: "Security" = Relationship(back_populates="trades")  # type: ignore


class TradeCreate(TradeBase):
    pass


class TradeRead(TradeBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None
    account_id: UUID
    security_symbol: str | None = None


class TradeUpdate(SQLModel):
    quantity: Decimal | None = get_decimal_field(gt=0, default=None)
    price: Decimal | None = get_decimal_field(gt=0, default=None)
    security_id: UUID | None = None
