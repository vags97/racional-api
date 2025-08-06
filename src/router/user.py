from fastapi import APIRouter, Depends, HTTPException, status, Request
from src.database import get_db
from .auth import validate_auth_token
from sqlalchemy.orm import Session
from src.config import COOKIE_NAME, pwd_context
from src.models import User
from pydantic import BaseModel, EmailStr



user_router = APIRouter(prefix="/v1/user", tags=["Users"])

@user_router.get("/user")
def protected_route(
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
    
    return {"message": f"Hola {user.username}"}


# Request model for updating user information
class UpdateUserInfoRequest(BaseModel):
    username: str = None          # Optional fields (can be None if not being updated)
    email: EmailStr = None        # Using EmailStr for email validation
    current_password: str = None  # Required if changing password
    new_password: str = None     # New password (if changing)

@user_router.patch("/update-info")
def update_user_info(
    request: Request,
    update_data: UpdateUserInfoRequest,
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
    
    # Get user
    user = db.query(User).get(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    
    try:
        # Update username if provided
        if update_data.username is not None:
            # Check if username already exists (excluding current user)
            existing_user = db.query(User).filter(
                User.username == update_data.username,
                User.id != user_id
            ).first()
            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="El nombre de usuario ya está en uso"
                )
            user.username = update_data.username
        
        # Update email if provided
        if update_data.email is not None:
            # Check if email already exists (excluding current user)
            existing_email = db.query(User).filter(
                User.email == update_data.email,
                User.id != user_id
            ).first()
            if existing_email:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="El correo electrónico ya está en uso"
                )
            user.email = update_data.email
        
        # Update password if provided
        if update_data.new_password is not None:
            if not update_data.current_password:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Se requiere la contraseña actual para cambiarla"
                )
            
            # Verify current password (you'll need to implement this)
            if not pwd_context.verify(update_data.current_password, user.hashed_password):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Contraseña actual incorrecta"
                )
            
            # Hash and update new password (you'll need to implement hash_password)
            user.hashed_password = pwd_context.hash(update_data.new_password)
        
        db.commit()
        
        return {
            "message": "Información actualizada exitosamente",
            "updated_fields": {
                "username": update_data.username is not None,
                "email": update_data.email is not None,
                "password": update_data.new_password is not None
            }
        }
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al actualizar información: {str(e)}"
        )