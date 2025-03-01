from sqlmodel import Session

from app.models import Account, Stock, StockCreate, StockUpdate


def create(session: Session, stock_in: StockCreate, account_db: Account):
    stock_db = Stock.model_validate(stock_in, update={"account_id": account_db.id})
    session.add(stock_db)
    session.commit()
    session.refresh(stock_db)
    return stock_db


def update(session: Session, stock_db: Stock, stock_in: StockUpdate):
    stock_data = stock_in.model_dump(exclude_unset=True)
    stock_db.sqlmodel_update(stock_data)
    session.add(stock_db)
    session.commit()
    session.refresh(stock_db)


def delete(session: Session, stock_db: Stock):
    session.delete(stock_db)
    session.commit()
