from dataclasses import dataclass

from sqlmodel import Session

from app.models.accounts import Account
from app.models.ledger import Ledger, LedgerType
from app.models.stocks import Stock
from app.models.trades import Trade, TradeType


@dataclass
class TradeTransactionContext:
    session: Session
    account: Account
    stock: Stock
    type: TradeType
    trade: Trade
    ledger: None = None


@dataclass
class LedgerTransactionContext:
    session: Session
    account: Account
    type: LedgerType
    ledger: Ledger
    stock: None = None
    trade: None = None


TransactionContext = TradeTransactionContext | LedgerTransactionContext
