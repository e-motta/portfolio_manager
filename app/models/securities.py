from datetime import datetime
from decimal import Decimal
from uuid import UUID

from sqlalchemy import Column
from sqlmodel import JSON, Field, Relationship, SQLModel

from app.models.generic import BaseTableModel, get_decimal_field
from app.models.trades import Trade


class SecurityBase(SQLModel):
    name: str
    symbol: str
    target_allocation: Decimal = get_decimal_field(le=1)


class Security(BaseTableModel, SecurityBase, table=True):
    __tablename__: str = "securities"

    cost_basis: Decimal = get_decimal_field(default=0)
    position: Decimal = get_decimal_field(default=0)
    average_price: Decimal = get_decimal_field(default=0)
    latest_price: Decimal = get_decimal_field(default=0)

    account_id: UUID = Field(foreign_key="accounts.id", ondelete="CASCADE")
    account: list["Account"] = Relationship(back_populates="securities")  # type: ignore
    trades: list[Trade] = Relationship(back_populates="security", cascade_delete=True)

    fifo_lots: list = Field(sa_column=Column(JSON), default_factory=list)


class SecurityCreate(SecurityBase):
    pass


class SecurityRead(SecurityBase):
    cost_basis: Decimal
    position: Decimal
    average_price: Decimal
    latest_price: Decimal
    id: UUID
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None
    account_id: UUID


class SecurityUpdate(SQLModel):
    symbol: str | None = None
    name: str | None = None
    target_allocation: Decimal | None = get_decimal_field(le=1, default=None)


class SecurityServiceUpdate(SQLModel):
    cost_basis: Decimal = get_decimal_field()
    position: Decimal = get_decimal_field()
    average_price: Decimal = get_decimal_field()
    latest_price: Decimal = get_decimal_field()
