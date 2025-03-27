from datetime import datetime
from decimal import Decimal
from enum import Enum
from uuid import UUID

from sqlmodel import Field, Relationship, SQLModel

from app.models.generic import BaseTableModel
from app.models.ledger import Ledger
from app.models.securities import Security
from app.models.trades import Trade


class AccountBase(SQLModel):
    name: str


class Account(BaseTableModel, AccountBase, table=True):
    __tablename__: str = "accounts"

    user_id: UUID = Field(foreign_key="users.id", ondelete="CASCADE")
    user: "User" = Relationship(back_populates="accounts")  # type: ignore
    buying_power: Decimal = Field(
        max_digits=12, decimal_places=2, ge=0, default=Decimal("0")
    )
    securities: list[Security] = Relationship(
        back_populates="account", cascade_delete=True
    )
    trades: list[Trade] = Relationship(back_populates="account", cascade_delete=True)
    ledger: list[Ledger] = Relationship(back_populates="account", cascade_delete=True)


class AccountCreate(AccountBase):
    pass


class AccountRead(AccountBase):
    user_id: UUID
    buying_power: Decimal
    securities: list[Security]
    id: UUID
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None


class AccountUpdate(SQLModel):
    name: str | None = None


class AllocationPlanItem(SQLModel):
    security_id: UUID
    symbol: str
    current_value: Decimal = Field(max_digits=18, decimal_places=8, ge=0)
    effective_target_allocation: Decimal = Field(max_digits=12, decimal_places=2, ge=0)
    ideal_value: Decimal = Field(max_digits=18, decimal_places=8, ge=0)
    current_weight: Decimal = Field(max_digits=12, decimal_places=2, ge=0)
    needed_investment: Decimal = Field(max_digits=18, decimal_places=8, ge=0)


class AllocationStrategy(str, Enum):
    SCALE = "scale"
    FIXED = "fixed"


class AllocationPlanCreate(SQLModel):
    new_investment: Decimal = Field(max_digits=18, decimal_places=8, ge=0)
    allocation_strategy: AllocationStrategy | None = None
