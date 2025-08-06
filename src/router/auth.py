from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException, status, Response

from datetime import datetime, timedelta
from src.models import User
from sqlalchemy.orm import Session
from src.database import get_db
from src.config import SECRET_KEY, COOKIE_NAME, TOKEN_EXPIRE_MINUTES, pwd_context
import hmac
import hashlib

auth_router = APIRouter(prefix="/v1/auth", tags=["Auth"])

class LoginData(BaseModel):
    username: str = 'john_doe'
    password: str = '123456'

def verify_user(db: Session, username: str, password: str):
    user = db.query(User).filter(User.username == username).first()
    if not user or not pwd_context.verify(password, user.hashed_password):
        return None
    return user

def sign_token(data: str) -> str:
    return hmac.new(SECRET_KEY.encode(), data.encode(), hashlib.sha256).hexdigest()

def create_auth_token(user_id: int) -> str:
    # Token simple: user_id:firma
    token_data = f"{user_id}:{datetime.utcnow().timestamp()}"
    signature = sign_token(token_data)
    return f"{token_data}:{signature}"

def validate_auth_token(token: str) -> int:
    """Valida el token y devuelve el user_id si es válido"""
    if not token:
        return None
    
    try:
        # Dividir el token en sus partes
        parts = token.split(':')
        if len(parts) != 3:
            return None
        
        data_part = f"{parts[0]}:{parts[1]}"
        received_signature = parts[2]
        
        # 1. Verificar que la firma coincida
        expected_signature = sign_token(data_part)
        if not hmac.compare_digest(received_signature, expected_signature):
            return None
        
        # 2. Verificar expiración (opcional)
        timestamp = float(parts[1])
        if datetime.utcnow() > datetime.fromtimestamp(timestamp) + timedelta(minutes=TOKEN_EXPIRE_MINUTES):
            return None
        
        # 3. Devolver el user_id si todo es válido
        return int(parts[0])
    
    except (ValueError, IndexError):
        return None

# Endpoints
@auth_router.post("/login")
def login(
    response: Response,
    login_data: LoginData,
    db: Session = Depends(get_db)
):
    user = verify_user(db, login_data.username, login_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas"
        )
    
    token = create_auth_token(user.id)
    
    response.set_cookie(
        key=COOKIE_NAME,
        value=token,
        httponly=True,
        max_age=TOKEN_EXPIRE_MINUTES * 60,
        secure=False,  # True en producción con HTTPS
        samesite="lax"
    )
    
    return {"message": "Login exitoso"}

@auth_router.post("/logout")
def logout(response: Response):
    response.delete_cookie(COOKIE_NAME)
    return {"message": "Logout exitoso"}