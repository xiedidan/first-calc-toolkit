"""
User management API endpoints
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_active_user
from app.models import User, Role
from app.schemas import User as UserSchema, UserCreate, UserUpdate
from app.utils.security import get_password_hash


router = APIRouter()


@router.get("", response_model=dict)
async def get_users(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    keyword: str = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get user list with pagination
    """
    # Build query
    query = db.query(User)
    
    # Apply keyword filter
    if keyword:
        query = query.filter(
            (User.username.ilike(f"%{keyword}%")) |
            (User.name.ilike(f"%{keyword}%")) |
            (User.email.ilike(f"%{keyword}%"))
        )
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    users = query.offset((page - 1) * size).limit(size).all()
    
    # Format response
    items = []
    for user in users:
        role_codes = [role.code for role in user.roles]
        items.append(UserSchema(
            id=user.id,
            username=user.username,
            name=user.name,
            email=user.email,
            status=user.status,
            created_at=user.created_at,
            updated_at=user.updated_at,
            roles=role_codes
        ))
    
    return {
        "total": total,
        "items": items
    }


@router.post("", response_model=UserSchema, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_create: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Create new user
    """
    # Check if username already exists
    existing_user = db.query(User).filter(User.username == user_create.username).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists"
        )
    
    # Check if email already exists
    if user_create.email:
        existing_email = db.query(User).filter(User.email == user_create.email).first()
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already exists"
            )
    
    # Create user
    user = User(
        username=user_create.username,
        name=user_create.name,
        email=user_create.email,
        hashed_password=get_password_hash(user_create.password),
        status="active"
    )
    
    # Assign roles
    if user_create.role_ids:
        roles = db.query(Role).filter(Role.id.in_(user_create.role_ids)).all()
        user.roles = roles
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Format response
    role_codes = [role.code for role in user.roles]
    return UserSchema(
        id=user.id,
        username=user.username,
        name=user.name,
        email=user.email,
        status=user.status,
        created_at=user.created_at,
        updated_at=user.updated_at,
        roles=role_codes
    )


@router.get("/{user_id}", response_model=UserSchema)
async def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get user by ID
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Format response
    role_codes = [role.code for role in user.roles]
    return UserSchema(
        id=user.id,
        username=user.username,
        name=user.name,
        email=user.email,
        status=user.status,
        created_at=user.created_at,
        updated_at=user.updated_at,
        roles=role_codes
    )


@router.put("/{user_id}", response_model=UserSchema)
async def update_user(
    user_id: int,
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Update user
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Update fields
    if user_update.name is not None:
        user.name = user_update.name
    
    if user_update.email is not None:
        # Check if email already exists
        existing_email = db.query(User).filter(
            User.email == user_update.email,
            User.id != user_id
        ).first()
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already exists"
            )
        user.email = user_update.email
    
    if user_update.password is not None:
        user.hashed_password = get_password_hash(user_update.password)
    
    if user_update.status is not None:
        user.status = user_update.status
    
    # Update roles
    if user_update.role_ids is not None:
        roles = db.query(Role).filter(Role.id.in_(user_update.role_ids)).all()
        user.roles = roles
    
    db.commit()
    db.refresh(user)
    
    # Format response
    role_codes = [role.code for role in user.roles]
    return UserSchema(
        id=user.id,
        username=user.username,
        name=user.name,
        email=user.email,
        status=user.status,
        created_at=user.created_at,
        updated_at=user.updated_at,
        roles=role_codes
    )


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Delete user
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Prevent deleting yourself
    if user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete yourself"
        )
    
    db.delete(user)
    db.commit()
    
    return None
