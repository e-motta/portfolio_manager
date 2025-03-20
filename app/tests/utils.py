import random
import string
from decimal import Decimal

from fastapi.testclient import TestClient
from sqlmodel import Session

from app import crud
from app.core.config import settings
from app.models.accounts import Account, AccountCreate
from app.models.contexts import LedgerTransactionContext
from app.models.ledger import LedgerCreate, LedgerType
from app.models.securities import Security, SecurityCreate
from app.models.trades import Trade, TradeCreate, TradeType
from app.models.users import User, UserCreate
from app.services import process_transaction


def generate_random_string(length: int = 10):
    return "".join(random.choices(string.ascii_letters + string.digits, k=length))


def generate_random_password(length: int = 10):
    lowercase_letters = string.ascii_lowercase
    uppercase_letters = string.ascii_uppercase
    digits = string.digits
    special_characters = '!@#$%^&*(),.?":{}|<>'

    password = [
        random.choice(lowercase_letters),
        random.choice(uppercase_letters),
        random.choice(digits),
        random.choice(special_characters),
    ]

    all_characters = lowercase_letters + uppercase_letters + digits + special_characters
    password += random.choices(all_characters, k=length - len(password))

    random.shuffle(password)

    return "".join(password)


def create_user(
    session: Session,
    *,
    username: str = "username",
    email: str = "email@example.com",
    password: str = generate_random_password(),
    is_admin: bool = False,
) -> User:
    user_in = UserCreate(
        username=username,
        email=email,
        first_name="first",
        last_name="last",
        password=password,
        is_admin=is_admin,
    )
    user = crud.users.create(session, user_in)
    if not user:
        raise ValueError("User could not be created")
    return user


def create_account(
    session: Session,
    *,
    current_user: User,
    name: str = "account_name",
) -> Account:
    account_in = AccountCreate(name=name)
    account = crud.accounts.create(session, account_in, current_user)
    if not account:
        raise ValueError("Account could not be created")
    return account


def create_security(
    session: Session,
    *,
    account: Account,
    name: str = "security_name",
    symbol: str = "SYM",
    target_allocation: Decimal = Decimal(10),
) -> Security:
    security_in = SecurityCreate(
        name=name,
        symbol=symbol,
        target_allocation=target_allocation,
    )
    security = crud.securities.create(session, security_in, account)
    if not security:
        raise ValueError("Security could not be created")
    return security


def create_trade(
    session: Session,
    *,
    account: Account,
    security: Security,
    type_: TradeType = TradeType.BUY,
    quantity: Decimal = Decimal("1"),
    price: Decimal = Decimal("100"),
):
    trade_in = TradeCreate(
        type=type_, quantity=quantity, price=price, security_id=security.id
    )
    trade = crud.trades.create(session, trade_in, account)
    if not trade:
        raise ValueError("Trade could not be created")
    return trade


def delete_trade(session: Session, *, trade: Trade):
    crud.trades.delete(session, trade)


def create_ledger_item(
    session: Session,
    *,
    account: Account,
    type_: LedgerType = LedgerType.DEPOSIT,
    amount: Decimal = Decimal("1000"),
):
    ledger_in = LedgerCreate(type=type_, amount=amount)
    ledger = crud.ledger.create(session, ledger_in, account)
    if not ledger:
        raise ValueError("Ledger item could not be created")
    return ledger


def create_and_process_ledger(
    session: Session,
    *,
    account: Account,
    type_: LedgerType = LedgerType.DEPOSIT,
    amount: Decimal = Decimal("1000"),
):
    ledger = create_ledger_item(session, account=account, type_=type_, amount=amount)
    ledger_ctx = LedgerTransactionContext(session, account, type_, ledger)
    process_transaction(ledger_ctx)
    return ledger


def get_token_headers(
    client: TestClient, *, username: str, password: str
) -> dict[str, str]:
    data = {"username": username, "password": password}

    r = client.post(f"{settings.API_V1_STR}/auth/token", data=data)
    response = r.json()
    auth_token = response["access_token"]
    headers = {"Authorization": f"Bearer {auth_token}"}
    return headers
