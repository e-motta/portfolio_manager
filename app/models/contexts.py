from dataclasses import dataclass

from sqlmodel import Session

from app.models.accounts import Account
from app.models.stocks import Stock
from app.models.transactions import Transaction


@dataclass
class TransactionContext:
    session: Session
    account: Account
    stock: Stock
    transaction: Transaction
