from fastapi import APIRouter, HTTPException, status
from sqlmodel import select

from app.api.dependencies import CurrentUserDepAnnotated, SessionDepAnnotated
from app.models import Account, Stock, StockCreate, StockRead, StockUpdate
from app import services

router = APIRouter(prefix="/accounts/{account_id}/stocks", tags=["stocks"])


@router.get("/", response_model=list[StockRead])
def read_stocks(
    session: SessionDepAnnotated, current_user: CurrentUserDepAnnotated, account_id: int
):
    account = services.accounts.get_by_id(session, account_id)

    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Account not found"
        )

    if current_user.id != account.user_id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions"
        )

    return account.stocks


@router.post("/", response_model=StockRead)
def create_stock(
    session: SessionDepAnnotated,
    current_user: CurrentUserDepAnnotated,
    stock_in: StockCreate,
    account_id: int,
):
    account = services.accounts.get_by_id(session, account_id)

    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Account not found"
        )

    if current_user.id != account.user_id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions"
        )

    stock_db = services.stocks.create(session, stock_in, account_id, current_user)
    return stock_db
