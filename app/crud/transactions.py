from sqlmodel import Session, col, select

from app.models.accounts import Account
from app.models.stocks import Stock
from app.models.transactions import Transaction, TransactionCreate, TransactionUpdate


def get_all_for_stock(session: Session, account: Account, stock: Stock):
    statement = (
        select(Transaction)
        .where(Transaction.account_id == account.id, Transaction.stock_id == stock.id)
        .order_by(col(Transaction.created_at))
    )

    transactions = session.exec(statement).all()
    return transactions


def create(session: Session, transaction_in: TransactionCreate, account_db: Account):
    transaction_db = Transaction.model_validate(
        transaction_in, update={"account_id": account_db.id}
    )
    session.add(transaction_db)
    session.commit()
    session.refresh(transaction_db)
    return transaction_db


def update(
    session: Session, transaction_db: Transaction, transaction_in: TransactionUpdate
):
    transaction_data = transaction_in.model_dump(exclude_unset=True)
    transaction_db.sqlmodel_update(transaction_data)
    session.add(transaction_db)
    session.commit()
    session.refresh(transaction_db)


def delete(session: Session, transaction_db: Transaction):
    session.delete(transaction_db)
    session.commit()
