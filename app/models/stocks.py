from datetime import datetime
from decimal import Decimal
from uuid import UUID

from sqlalchemy import DECIMAL, Column
from sqlmodel import JSON, Field, Relationship, SQLModel

from app.models.generic import BaseTableModel


class StockBase(SQLModel):
    name: str
    symbol: str
    target_allocation: Decimal = Field(sa_column=Column(DECIMAL(12, 2)), ge=0)


class Stock(BaseTableModel, StockBase, table=True):
    __tablename__: str = "stocks"

    cost_basis: Decimal = Field(sa_column=Column(DECIMAL(18, 8)), default=0, ge=0)
    position: Decimal = Field(sa_column=Column(DECIMAL(14, 4)), default=0, ge=0)
    average_price: Decimal = Field(sa_column=Column(DECIMAL(18, 8)), default=0, ge=0)

    account_id: UUID = Field(foreign_key="accounts.id", ondelete="CASCADE")
    account: list["Account"] = Relationship(back_populates="stocks")  # type: ignore

    fifo_lots: list = Field(sa_column=Column(JSON), default_factory=list)


class StockCreate(StockBase):
    pass


class StockRead(StockBase):
    cost_basis: Decimal
    position: Decimal
    average_price: Decimal
    id: UUID
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None
    account_id: UUID


class StockUpdate(SQLModel):
    symbol: str | None = None
    name: str | None = None
    target_allocation: Decimal | None = Field(
        sa_column=Column(DECIMAL(12, 2)), default=None, ge=0
    )


class StockServiceUpdate(SQLModel):
    cost_basis: Decimal = Field(sa_column=Column(DECIMAL(18, 8)), ge=0)
    position: Decimal = Field(sa_column=Column(DECIMAL(14, 4)), ge=0)
    average_price: Decimal = Field(sa_column=Column(DECIMAL(18, 8)), ge=0)
