from fastapi import APIRouter, Depends, HTTPException, status, Request
from src.database import get_db
from .auth import validate_auth_token
from sqlalchemy.orm import Session
from src.config import COOKIE_NAME
from src.models import Portfolio
from typing import List
from pydantic import BaseModel
from datetime import datetime
from sqlalchemy.orm import joinedload



portfolio_router = APIRouter(prefix="/v1/portfolio", tags=["Portfolio"])



# Modelos Pydantic para la respuesta
class PortfolioStockResponse(BaseModel):
    stock_id: int
    quantity: int
    average_price: float

class BuyOrderResponse(BaseModel):
    id: int
    stock_id: int
    amount: float
    stock_quantity: int
    state: str
    timestamp: datetime

class SellOrderResponse(BaseModel):
    id: int
    stock_id: int
    amount: float
    stock_quantity: int
    state: str
    timestamp: datetime

class PortfolioResponse(BaseModel):
    id: int
    name: str
    stocks: List[PortfolioStockResponse]
    buy_orders: List[BuyOrderResponse]
    sell_orders: List[SellOrderResponse]

@portfolio_router.get("", response_model=List[PortfolioResponse])
def get_user_portfolios(
    request: Request,
    db: Session = Depends(get_db)
):
    # Autenticación
    token = request.cookies.get(COOKIE_NAME)
    user_id = validate_auth_token(token)
    
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No autenticado"
        )
    
    # Obtener todos los portfolios del usuario con sus relaciones
    portfolios = db.query(Portfolio).filter(
        Portfolio.user_id == user_id
    ).options(
        joinedload(Portfolio.portfolio_stocks),
        joinedload(Portfolio.buy_orders),
        joinedload(Portfolio.sell_orders)
    ).all()
    
    if not portfolios:
        return []
    
    # Formatear la respuesta
    response = []
    for portfolio in portfolios:
        portfolio_data = {
            "id": portfolio.id,
            "name": portfolio.portfolio,
            "stocks": [],
            "buy_orders": [],
            "sell_orders": []
        }
        
        # Stocks en el portfolio
        for stock in portfolio.portfolio_stocks:
            portfolio_data["stocks"].append({
                "stock_id": stock.stock_id,
                "quantity": stock.quantity,
                "average_price": stock.average_price
            })
        
        # Órdenes de compra
        for order in portfolio.buy_orders:
            portfolio_data["buy_orders"].append({
                "id": order.id,
                "stock_id": order.stock_id,
                "amount": order.amount,
                "stock_quantity": order.stock_quantity,
                "state": order.state,
                "timestamp": order.timestamp
            })
        
        # Órdenes de venta
        for order in portfolio.sell_orders:
            portfolio_data["sell_orders"].append({
                "id": order.id,
                "stock_id": order.stock_id,
                "amount": order.amount,
                "stock_quantity": order.stock_quantity,
                "state": order.state,
                "timestamp": order.timestamp
            })
        
        response.append(portfolio_data)
    
    return response

class UpdatePortfolioNameRequest(BaseModel):
    new_name: str
    portfolio_id: int

@portfolio_router.patch("/update-name")
def update_portfolio_name(
    request: Request,
    update_data: UpdatePortfolioNameRequest,
    db: Session = Depends(get_db)
):
    # Autenticación
    token = request.cookies.get(COOKIE_NAME)
    user_id = validate_auth_token(token)
    
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No autenticado"
        )
    
    # Verificar que el portfolio pertenece al usuario
    portfolio = db.query(Portfolio).filter(
        Portfolio.id == update_data.portfolio_id,
        Portfolio.user_id == user_id
    ).first()
    
    if not portfolio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Portfolio no encontrado o no pertenece al usuario"
        )
    
    try:
        # Actualizar el nombre
        portfolio.portfolio = update_data.new_name
        db.commit()
        
        return {"message": "Nombre del portfolio actualizado correctamente"}
    
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al actualizar el nombre: {str(e)}"
        )