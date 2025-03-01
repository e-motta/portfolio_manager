from fastapi import APIRouter

from app.api.routes import accounts, auth, stocks, users

api_router = APIRouter()

api_router.include_router(users.router)
api_router.include_router(auth.router)
api_router.include_router(accounts.router)
api_router.include_router(stocks.router)
