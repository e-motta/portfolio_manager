from fastapi import APIRouter
from sqlmodel import select

from ...models import Account, AccountCreate, AccountRead, AccountUpdate
from ..dependencies import CurrentUserDepAnnotated, SessionDepAnnotated

router = APIRouter(prefix="/accounts", tags=["accounts"])


@router.get("/", response_model=list[AccountRead])
def read_accounts(session: SessionDepAnnotated, current_user: CurrentUserDepAnnotated):
    statement = select(Account).where(Account.user_id == current_user.id)
    accounts = session.exec(statement).all()
    return accounts


@router.post("/", response_model=AccountRead)
def create_account(
    session: SessionDepAnnotated,
    current_user: CurrentUserDepAnnotated,
    account: AccountCreate,
):
    account_db = Account.model_validate(account, update={"user_id": current_user.id})
    session.add(account_db)
    session.commit()
    session.refresh(account_db)
    return account_db
