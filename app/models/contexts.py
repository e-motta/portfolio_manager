from dataclasses import dataclass

from sqlmodel import Session

from app.models.accounts import Account
from app.models.ledger import Ledger, LedgerType
from app.models.securities import Security
from app.models.trades import Trade, TradeType


@dataclass
class TradeTransactionContext:
    session: Session
    account: Account
    security: Security
    type: TradeType
    trade: Trade
    ledger: None = None


@dataclass
class LedgerTransactionContext:
    session: Session
    account: Account
    type: LedgerType
    ledger: Ledger
    security: None = None
    trade: None = None


TransactionContext = TradeTransactionContext | LedgerTransactionContext
