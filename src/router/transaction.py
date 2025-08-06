from fastapi import APIRouter, Depends, HTTPException, status, Request
from src.database import get_db
from .auth import validate_auth_token
from sqlalchemy.orm import Session
from src.config import COOKIE_NAME
from src.models import User, Transaction
from datetime import datetime
from pydantic import BaseModel


transaction_router = APIRouter(prefix="/v1/transaction", tags=["Transactions"])

class AddFundsRequest(BaseModel):
    amount: float

@transaction_router.post("/add-funds")
def add_funds(
    request: Request,
    funds_data: AddFundsRequest,
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
    
    # Validate amount
    if funds_data.amount <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El monto debe ser mayor que cero"
        )
    
    # Get user
    db.begin()
    user = db.query(User).get(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no encontrado"
        )
    
    try:
        # Update user balance
        if user.balance is None:
            user.balance = 0.0
        user.balance += funds_data.amount
        
        # Create transaction record
        transaction = Transaction(
            user_id=user_id,
            amount=funds_data.amount,
            timestamp=datetime.utcnow()
        )
        
        db.add(transaction)
        db.commit()
        
        return {
            "message": "Fondos agregados exitosamente",
            "new_balance": user.balance
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al agregar fondos: {str(e)}"
        )
    
class RetireFundsRequest(BaseModel):
    amount: float

@transaction_router.post("/retire-funds")
def retire_funds(
    request: Request,
    funds_data: RetireFundsRequest,
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
    
    # Validate amount
    if funds_data.amount <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El monto debe ser mayor que cero"
        )
    
    # Get user
    db.begin()
    user = db.query(User).get(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    
    # Check sufficient funds
    if user.balance is None or user.balance < funds_data.amount:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Fondos insuficientes"
        )
    
    try:
        # Update user balance
        user.balance -= funds_data.amount
        
        # Create transaction record (negative amount for withdrawal)
        transaction = Transaction(
            user_id=user_id,
            amount=-funds_data.amount,  # Negative amount indicates withdrawal
            timestamp=datetime.utcnow()
        )
        
        db.add(transaction)
        db.commit()
        
        return {
            "message": "Fondos retirados exitosamente",
            "new_balance": user.balance
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al retirar fondos: {str(e)}"
        )