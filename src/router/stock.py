from fastapi import APIRouter, Depends, HTTPException, status, Request
from src.database import get_db
from .auth import validate_auth_token
from sqlalchemy.orm import Session
from src.config import COOKIE_NAME
from src.models import User, Stock, Portfolio, BuyOrder, SellOrder
from pydantic import BaseModel
from datetime import datetime

stock_router = APIRouter(prefix="/v1/stock", tags=["Stocks"])

@stock_router.get("/get")
def get_stocks(
    request: Request,
    db: Session = Depends(get_db)
):
    token = request.cookies.get(COOKIE_NAME)
    user_id = validate_auth_token(token)
    
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No autenticado"
        )
    
    user = db.query(User).get(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no encontrado"
        )
    
    stocks = db.query(Stock).all()
    
    return {"stocks": stocks}

class RegisterOrderOrder(BaseModel):
    stockId: int
    portfolioId: int
    ammount: float
    stock_quantity: float

# Request Models
class RegisterOrderRequest(BaseModel):
    portfolio_id: int
    stock_id: int
    stock_quantity: float
    amount: float

# Buy Order Endpoint
@stock_router.post("/register-buy-order")
def register_buy_order(
    request: Request,
    order_data: RegisterOrderRequest,
    db: Session = Depends(get_db)
):
    # Authentication
    token = request.cookies.get(COOKIE_NAME)
    user_id = validate_auth_token(token)
    
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No autenticado"
        )
    
    # Get user and validate portfolio ownership
    db.begin()
    user = db.query(User).get(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    
    portfolio = db.query(Portfolio).filter(
        Portfolio.id == order_data.portfolio_id,
        Portfolio.user_id == user_id
    ).first()
    
    if not portfolio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Portfolio no encontrado o no pertenece al usuario"
        )
    
    # Get stock and calculate total amount
    stock = db.query(Stock).get(order_data.stock_id)
    if not stock:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Acción no encontrada"
        )
    
    total_amount = stock.unit_value * order_data.stock_quantity
    
    # Check sufficient funds
    if user.balance is None or user.balance < total_amount:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Fondos insuficientes para completar la compra"
        )
    
    try:
        # Deduct from user balance
        user.balance -= total_amount
        
        # Create buy order
        buy_order = BuyOrder(
            portfolio_id=order_data.portfolio_id,
            broker_id=None,
            stock_id=order_data.stock_id,
            amount=total_amount,
            stock_quantity=order_data.stock_quantity,
            state="completed",
            timestamp=datetime.utcnow()
        )
        
        db.add(buy_order)
        
        db.commit()
        
        return {
            "message": "Orden de compra registrada exitosamente",
            "new_balance": user.balance,
            "order_id": buy_order.id
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al registrar orden de compra: {str(e)}"
        )

# Sell Order Endpoint
@stock_router.post("/register-sell-order")
def register_sell_order(
    request: Request,
    order_data: RegisterOrderRequest,
    db: Session = Depends(get_db)
):
    # Authentication
    token = request.cookies.get(COOKIE_NAME)
    user_id = validate_auth_token(token)
    
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No autenticado"
        )
    
    # Get user and validate portfolio ownership
    user = db.query(User).get(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    
    portfolio = db.query(Portfolio).filter(
        Portfolio.id == order_data.portfolio_id,
        Portfolio.user_id == user_id
    ).first()
    
    if not portfolio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Portfolio no encontrado o no pertenece al usuario"
        )
    
    # Get stock and calculate total amount
    stock = db.query(Stock).get(order_data.stock_id)
    if not stock:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Acción no encontrada"
        )
    
    total_amount = stock.unit_value * order_data.stock_quantity
    
    try:
        # Add to user balance
        user.balance += total_amount
        
        # Create sell order
        sell_order = SellOrder(
            portfolio_id=order_data.portfolio_id,
            broker_id=None,
            stock_id=order_data.stock_id,
            amount=total_amount,
            stock_quantity=order_data.stock_quantity,
            state="completed",
            timestamp=datetime.utcnow()
        )
        
        db.add(sell_order)
        
        db.commit()
        
        return {
            "message": "Orden de venta registrada exitosamente",
            "new_balance": user.balance,
            "order_id": sell_order.id
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al registrar orden de venta: {str(e)}"
        )