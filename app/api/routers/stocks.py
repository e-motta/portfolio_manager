from fastapi import APIRouter, HTTPException, status
from sqlmodel import select

from app.api.dependencies import CurrentUserDepAnnotated, SessionDepAnnotated
from app.models import Account, Stock, StockCreate, StockRead, StockUpdate

router = APIRouter(prefix="/accounts/{account_id}/stocks", tags=["stocks"])


@router.get("/", response_model=list[StockRead])
def read_stocks(
    session: SessionDepAnnotated, current_user: CurrentUserDepAnnotated, account_id: int
):
    account_statement = select(Account).where(Account.user_id == current_user.id)
    accounts = session.exec(account_statement).all()
    if account_id not in [account.id for account in accounts]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions"
        )

    statement = select(Stock).where(Stock.account_id == account_id)
    stocks = session.exec(statement).all()
    return stocks


@router.post("/", response_model=StockRead)
def create_stock(
    session: SessionDepAnnotated,
    current_user: CurrentUserDepAnnotated,
    stock: StockCreate,
    account_id: int,
):
    stock_db = Stock.model_validate(stock, update={"account_id": account_id})
    session.add(stock_db)
    session.commit()
    session.refresh(stock_db)
    return stock_db
