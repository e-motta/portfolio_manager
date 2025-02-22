from datetime import datetime
from decimal import Decimal

from sqlalchemy import DECIMAL, Column
from sqlmodel import Field, SQLModel

from .generic import BaseTableModel


class StockBase(SQLModel):
    name: str
    symbol: str
    cost_basis: Decimal = Field(sa_column=Column(DECIMAL(18, 8)))
    position: Decimal = Field(sa_column=Column(DECIMAL(14, 4)))
    average_price: Decimal = Field(sa_column=Column(DECIMAL(18, 8)))
    target_allocation: Decimal = Field(sa_column=Column(DECIMAL(12, 2)))


class Stock(BaseTableModel, StockBase, table=True):
    account_id: int = Field(foreign_key="accounts.id")


class StockCreate(StockBase):
    pass


class StockRead(StockBase):
    id: int
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None
    account_id: int


class StockUpdate(SQLModel):
    symbol: str | None = None
    name: str | None = None
    cost_basis: Decimal | None = Field(sa_column=Column(DECIMAL(18, 8)), default=None)
    position: Decimal | None = Field(sa_column=Column(DECIMAL(14, 4)), default=None)
    average_price: Decimal | None = Field(
        sa_column=Column(DECIMAL(18, 8)), default=None
    )
    target_allocation: Decimal | None = Field(
        sa_column=Column(DECIMAL(12, 2)), default=None
    )
