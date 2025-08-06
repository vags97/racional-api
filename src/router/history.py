from datetime import datetime
from typing import List
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException, status, Request
from src.models import Portfolio, BuyOrder, Transaction, SellOrder
from src.database import get_db
from src.config import COOKIE_NAME
from sqlalchemy.orm import Session
from .auth import validate_auth_token


history_router = APIRouter(prefix="/v1/history", tags=["Historail"])

# Modelos Pydantic para la respuesta
class TransactionResponse(BaseModel):
    id: int
    type: str
    amount: float
    description: str
    timestamp: datetime

class OrderResponse(BaseModel):
    id: int
    type: str
    stock_symbol: str
    quantity: int
    amount: float
    portfolio_name: str
    timestamp: datetime

class HistoryResponse(BaseModel):
    transactions: List[TransactionResponse]
    orders: List[OrderResponse]

@history_router.get("", response_model=HistoryResponse)
def user_history(
    request: Request,
    db: Session = Depends(get_db),
    limit: int = 10  # Parámetro opcional para limitar resultados
):
    # Autenticación
    token = request.cookies.get(COOKIE_NAME)
    user_id = validate_auth_token(token)
    
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No autenticado"
        )
    
    # Obtener transacciones de dinero
    money_transactions = db.query(Transaction).filter(
        Transaction.user_id == user_id
    ).order_by(
        Transaction.timestamp.desc()
    ).limit(limit).all()
    
    # Obtener órdenes de compra/venta
    buy_orders = db.query(BuyOrder).join(
        BuyOrder.portfolio
    ).filter(
        Portfolio.user_id == user_id
    ).order_by(
        BuyOrder.timestamp.desc()
    ).limit(limit).all()
    
    sell_orders = db.query(SellOrder).join(
        SellOrder.portfolio
    ).filter(
        Portfolio.user_id == user_id
    ).order_by(
        SellOrder.timestamp.desc()
    ).limit(limit).all()
    
    # Formatear respuesta
    formatted_transactions = [
        TransactionResponse(
            id=t.id,
            type="deposit" if t.amount > 0 else "withdrawal",
            amount=abs(t.amount),
            description="Transferencia de fondos",
            timestamp=t.timestamp
        ) for t in money_transactions
    ]
    
    formatted_orders = []
    
    for order in buy_orders + sell_orders:
        order_type = "buy" if isinstance(order, BuyOrder) else "sell"
        formatted_orders.append(
            OrderResponse(
                id=order.id,
                type=order_type,
                stock_symbol=order.stock.stock,
                quantity=order.stock_quantity,
                amount=order.amount,
                portfolio_name=order.portfolio.portfolio,
                timestamp=order.timestamp
            )
        )
    
    # Ordenar todas las órdenes por timestamp (más reciente primero)
    formatted_orders.sort(key=lambda x: x.timestamp, reverse=True)
    
    return HistoryResponse(
        transactions=formatted_transactions,
        orders=formatted_orders[:limit]  # Aplicar límite también a las órdenes combinadas
    )