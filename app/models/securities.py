from datetime import datetime
from decimal import Decimal
from uuid import UUID

from sqlalchemy import Column
from sqlmodel import JSON, Field, Relationship, SQLModel

from app.models.generic import BaseTableModel
from app.models.trades import Trade


class SecurityBase(SQLModel):
    name: str
    symbol: str
    target_allocation: Decimal = Field(max_digits=12, decimal_places=2, ge=0)


class Security(BaseTableModel, SecurityBase, table=True):
    __tablename__: str = "securities"

    cost_basis: Decimal = Field(max_digits=18, decimal_places=8, default=0, ge=0)
    position: Decimal = Field(max_digits=14, decimal_places=4, default=0, ge=0)
    average_price: Decimal = Field(max_digits=18, decimal_places=8, default=0, ge=0)

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
    id: UUID
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None
    account_id: UUID


class SecurityUpdate(SQLModel):
    symbol: str | None = None
    name: str | None = None
    target_allocation: Decimal | None = Field(
        max_digits=12, decimal_places=2, default=None, ge=0
    )


class SecurityServiceUpdate(SQLModel):
    cost_basis: Decimal = Field(max_digits=18, decimal_places=8, ge=0)
    position: Decimal = Field(max_digits=14, decimal_places=4, ge=0)
    average_price: Decimal = Field(max_digits=18, decimal_places=8, ge=0)
