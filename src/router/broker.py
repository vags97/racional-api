from fastapi import APIRouter, Depends, HTTPException, status, Request
from src.database import get_db
from .auth import validate_auth_token
from sqlalchemy.orm import Session
from src.config import COOKIE_NAME
from src.models import User, Broker


broker_router = APIRouter(prefix="/v1/broker", tags=["Broker"])

@broker_router.get("/get")
def get_brokers(
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
    
    broker = db.query(Broker).all()
    
    return {"stocks": broker}