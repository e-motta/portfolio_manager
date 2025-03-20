from datetime import datetime
from decimal import Decimal
from enum import Enum
from uuid import UUID

from sqlmodel import Field, Relationship, SQLModel

from app.models.generic import BaseTableModel


class LedgerType(str, Enum):
    DEPOSIT = "deposit"
    WITHDRAWAL = "withdrawal"


class LedgerBase(SQLModel):
    type: LedgerType
    amount: Decimal = Field(max_digits=12, decimal_places=2, ge=0)


class Ledger(BaseTableModel, LedgerBase, table=True):
    __tablename__: str = "ledger"

    account_id: UUID = Field(foreign_key="accounts.id", ondelete="CASCADE")
    account: "Account" = Relationship(back_populates="ledger")  # type: ignore


class LedgerCreate(LedgerBase):
    pass


class LedgerRead(LedgerBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None
    account_id: UUID


class LedgerUpdate(SQLModel):
    amount: Decimal | None = Field(max_digits=12, decimal_places=2, default=None, ge=0)
