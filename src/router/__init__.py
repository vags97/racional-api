from fastapi import APIRouter
from .auth import auth_router
from .user import user_router
from .transaction import transaction_router
from .stock import stock_router
from .broker import broker_router
from .portfolio import portfolio_router

router = APIRouter()

router.include_router(auth_router)
router.include_router(user_router)
router.include_router(transaction_router)
router.include_router(stock_router)
router.include_router(broker_router)
router.include_router(portfolio_router)