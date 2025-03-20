from sqlmodel import Session, col, select

from app.models.accounts import Account
from app.models.securities import Security
from app.models.trades import Trade, TradeCreate, TradeUpdate


def get_all_for_account(session: Session, account: Account):
    statement = (
        select(Trade)
        .where(Trade.account_id == account.id)
        .order_by(col(Trade.created_at))
    )

    trades = session.exec(statement).all()
    return trades


def get_all_for_security(session: Session, account: Account, security: Security):
    statement = (
        select(Trade)
        .where(Trade.account_id == account.id, Trade.security_id == security.id)
        .order_by(col(Trade.created_at))
    )

    trades = session.exec(statement).all()
    return trades


def create(session: Session, trade_in: TradeCreate, account_db: Account):
    trade_db = Trade.model_validate(trade_in, update={"account_id": account_db.id})
    session.add(trade_db)
    session.commit()
    session.refresh(trade_db)
    return trade_db


def update(session: Session, trade_db: Trade, trade_in: TradeUpdate):
    trade_data = trade_in.model_dump(exclude_unset=True)
    trade_db.sqlmodel_update(trade_data)
    session.add(trade_db)
    session.commit()
    session.refresh(trade_db)


def delete(session: Session, trade_db: Trade):
    session.delete(trade_db)
    session.commit()
