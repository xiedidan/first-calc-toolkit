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
    size: int = Query(10, ge=1, le=10000),
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
        # 简化角色判断：有admin角色就是管理员，否则是普通用户
        role = "admin" if any(r.code == "admin" for r in user.roles) else "user"
        hospital_name = user.hospital.name if user.hospital else None
        items.append(UserSchema(
            id=user.id,
            username=user.username,
            name=user.name,
            email=user.email,
            status=user.status,
            hospital_id=user.hospital_id,
            hospital_name=hospital_name,
            created_at=user.created_at,
            updated_at=user.updated_at,
            role=role
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
    
    # 验证角色
    if user_create.role not in ["admin", "user"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="角色必须是admin或user"
        )
    
    # 普通用户必须指定医疗机构
    if user_create.role == "user" and not user_create.hospital_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="普通用户必须指定所属医疗机构"
        )
    
    # 管理员不能指定医疗机构
    if user_create.role == "admin" and user_create.hospital_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="管理员不能指定所属医疗机构"
        )
    
    # Validate hospital_id if provided
    if user_create.hospital_id is not None:
        from app.models.hospital import Hospital
        hospital = db.query(Hospital).filter(Hospital.id == user_create.hospital_id).first()
        if not hospital:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"医疗机构ID {user_create.hospital_id} 不存在"
            )
    
    # Create user
    user = User(
        username=user_create.username,
        name=user_create.name,
        email=user_create.email,
        hashed_password=get_password_hash(user_create.password),
        hospital_id=user_create.hospital_id,
        status="active"
    )
    
    # 分配角色
    role_obj = db.query(Role).filter(Role.code == user_create.role).first()
    if not role_obj:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"角色 {user_create.role} 不存在"
        )
    user.roles = [role_obj]
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Format response
    role = "admin" if any(r.code == "admin" for r in user.roles) else "user"
    hospital_name = user.hospital.name if user.hospital else None
    return UserSchema(
        id=user.id,
        username=user.username,
        name=user.name,
        email=user.email,
        status=user.status,
        hospital_id=user.hospital_id,
        hospital_name=hospital_name,
        created_at=user.created_at,
        updated_at=user.updated_at,
        role=role
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
    role = "admin" if any(r.code == "admin" for r in user.roles) else "user"
    hospital_name = user.hospital.name if user.hospital else None
    return UserSchema(
        id=user.id,
        username=user.username,
        name=user.name,
        email=user.email,
        status=user.status,
        hospital_id=user.hospital_id,
        hospital_name=hospital_name,
        created_at=user.created_at,
        updated_at=user.updated_at,
        role=role
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
    
    # Update role
    if user_update.role is not None:
        if user_update.role not in ["admin", "user"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="角色必须是admin或user"
            )
        
        role_obj = db.query(Role).filter(Role.code == user_update.role).first()
        if not role_obj:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"角色 {user_update.role} 不存在"
            )
        user.roles = [role_obj]
        
        # 如果改为管理员，清除医疗机构
        if user_update.role == "admin":
            user.hospital_id = None
    
    # Update hospital_id
    if user_update.hospital_id is not None:
        # 获取当前用户角色
        current_role = "admin" if any(r.code == "admin" for r in user.roles) else "user"
        
        # 管理员不能设置医疗机构
        if current_role == "admin":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="管理员不能指定所属医疗机构"
            )
        
        from app.models.hospital import Hospital
        hospital = db.query(Hospital).filter(Hospital.id == user_update.hospital_id).first()
        if not hospital:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"医疗机构ID {user_update.hospital_id} 不存在"
            )
        user.hospital_id = user_update.hospital_id
    
    db.commit()
    db.refresh(user)
    
    # Format response
    role = "admin" if any(r.code == "admin" for r in user.roles) else "user"
    hospital_name = user.hospital.name if user.hospital else None
    return UserSchema(
        id=user.id,
        username=user.username,
        name=user.name,
        email=user.email,
        status=user.status,
        hospital_id=user.hospital_id,
        hospital_name=hospital_name,
        created_at=user.created_at,
        updated_at=user.updated_at,
        role=role
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
