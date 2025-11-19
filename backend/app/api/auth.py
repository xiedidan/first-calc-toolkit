"""
Authentication API endpoints
"""
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_active_user
from app.models import User
from app.schemas import UserLogin, Token, User as UserSchema
from app.utils.security import verify_password, create_access_token
from app.config import settings


router = APIRouter()


@router.post("/login", response_model=Token)
async def login(
    user_login: UserLogin,
    db: Session = Depends(get_db)
):
    """
    User login
    
    Returns JWT access token
    """
    # Find user by username
    user = db.query(User).filter(User.username == user_login.username).first()
    
    # Verify user exists and password is correct
    if not user or not verify_password(user_login.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Check if user is active
    if user.status != "active":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is not active"
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id), "username": user.username},
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


@router.get("/me", response_model=UserSchema)
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user)
):
    """
    Get current user information
    """
    # 简化角色判断：有admin角色就是管理员，否则是普通用户
    role = "admin" if any(r.code == "admin" for r in current_user.roles) else "user"
    hospital_name = current_user.hospital.name if current_user.hospital else None
    
    return UserSchema(
        id=current_user.id,
        username=current_user.username,
        name=current_user.name,
        email=current_user.email,
        status=current_user.status,
        hospital_id=current_user.hospital_id,
        hospital_name=hospital_name,
        created_at=current_user.created_at,
        updated_at=current_user.updated_at,
        role=role
    )
