import random
import string
from decimal import Decimal

from fastapi.testclient import TestClient
from sqlmodel import Session

from app import crud
from app.core.config import settings
from app.models.accounts import Account, AccountCreate
from app.models.stocks import Stock, StockCreate
from app.models.transactions import Transaction, TransactionCreate, TransactionType
from app.models.users import User, UserCreate


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
    buying_power: Decimal = Decimal("1000000"),
) -> Account:
    account_in = AccountCreate(name=name, buying_power=buying_power)
    account = crud.accounts.create(session, account_in, current_user)
    if not account:
        raise ValueError("Account could not be created")
    return account


def create_stock(
    session: Session,
    *,
    account: Account,
    name: str = "stock_name",
    symbol: str = "SYM",
    target_allocation: Decimal = Decimal(10),
) -> Stock:
    stock_in = StockCreate(
        name=name,
        symbol=symbol,
        target_allocation=target_allocation,
    )
    stock = crud.stocks.create(session, stock_in, account)
    if not stock:
        raise ValueError("Stock could not be created")
    return stock


def create_transaction(
    session: Session,
    *,
    account: Account,
    stock: Stock,
    type: TransactionType = TransactionType.BUY,
    quantity: Decimal = Decimal("1"),
    price: Decimal = Decimal("100"),
):
    transaction_in = TransactionCreate(
        type=type, quantity=quantity, price=price, stock_id=stock.id
    )
    transaction = crud.transactions.create(session, transaction_in, account)
    if not transaction:
        raise ValueError("Transaction could not be created")
    return transaction


def delete_transaction(session: Session, *, transaction: Transaction):
    crud.transactions.delete(session, transaction)


def get_token_headers(
    client: TestClient, *, username: str, password: str
) -> dict[str, str]:
    data = {"username": username, "password": password}

    r = client.post(f"{settings.API_V1_STR}/auth/token", data=data)
    response = r.json()
    auth_token = response["access_token"]
    headers = {"Authorization": f"Bearer {auth_token}"}
    return headers
