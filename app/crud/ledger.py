from sqlmodel import Session, col, select

from app.models.accounts import Account
from app.models.ledger import Ledger, LedgerCreate, LedgerUpdate


def get_all_for_account(session: Session, account: Account):
    statement = (
        select(Ledger)
        .where(Ledger.account_id == account.id)
        .order_by(col(Ledger.created_at))
    )

    ledger = session.exec(statement).all()
    return ledger


def create(session: Session, trade_in: LedgerCreate, account_db: Account):
    trade_db = Ledger.model_validate(trade_in, update={"account_id": account_db.id})
    session.add(trade_db)
    session.commit()
    session.refresh(trade_db)
    return trade_db


def update(session: Session, trade_db: Ledger, trade_in: LedgerUpdate):
    trade_data = trade_in.model_dump(exclude_unset=True)
    trade_db.sqlmodel_update(trade_data)
    session.add(trade_db)
    session.commit()
    session.refresh(trade_db)


def delete(session: Session, trade_db: Ledger):
    session.delete(trade_db)
    session.commit()
