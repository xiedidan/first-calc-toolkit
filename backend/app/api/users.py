"""
User management API endpoints
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_active_user
from app.models import User, Role, RoleType, Department
from app.models.hospital import Hospital
from app.schemas import User as UserSchema, UserCreate, UserUpdate
from app.utils.security import get_password_hash


router = APIRouter()


def get_current_user_role_type(user: User) -> RoleType:
    """获取当前用户的角色类型"""
    if user.roles:
        return user.roles[0].role_type
    return RoleType.HOSPITAL_USER


def check_user_permission(current_user: User, target_user: User = None, target_role: Role = None):
    """检查当前用户是否有权限操作目标用户"""
    current_role_type = get_current_user_role_type(current_user)
    
    # 科室用户和全院用户不能管理用户
    if current_role_type in [RoleType.DEPARTMENT_USER, RoleType.HOSPITAL_USER]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权限管理用户"
        )
    
    # 检查目标用户的角色类型
    if target_user and target_user.roles:
        target_role_type = target_user.roles[0].role_type
        # 管理员不能操作维护者
        if target_role_type == RoleType.MAINTAINER and current_role_type != RoleType.MAINTAINER:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="只有维护者可以管理维护者用户"
            )
    
    # 检查目标角色类型
    if target_role:
        if target_role.role_type == RoleType.MAINTAINER and current_role_type != RoleType.MAINTAINER:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="只有维护者可以分配维护者角色"
            )


def validate_user_data(role: Role, hospital_id: int = None, department_id: int = None, db: Session = None):
    """验证用户数据与角色类型的一致性"""
    role_type = role.role_type
    
    if role_type == RoleType.DEPARTMENT_USER:
        if not hospital_id:
            raise HTTPException(status_code=400, detail="科室用户必须指定所属医疗机构")
        if not department_id:
            raise HTTPException(status_code=400, detail="科室用户必须指定所属科室")
        # 验证科室属于该医疗机构
        if db:
            dept = db.query(Department).filter(
                Department.id == department_id,
                Department.hospital_id == hospital_id
            ).first()
            if not dept:
                raise HTTPException(status_code=400, detail="所选科室不属于该医疗机构")
    
    elif role_type == RoleType.HOSPITAL_USER:
        if not hospital_id:
            raise HTTPException(status_code=400, detail="全院用户必须指定所属医疗机构")
        if department_id:
            raise HTTPException(status_code=400, detail="全院用户不能指定所属科室")
    
    elif role_type in [RoleType.ADMIN, RoleType.MAINTAINER]:
        if hospital_id:
            raise HTTPException(status_code=400, detail="管理员和维护者不能指定所属医疗机构")
        if department_id:
            raise HTTPException(status_code=400, detail="管理员和维护者不能指定所属科室")


def format_user_response(user: User) -> UserSchema:
    """格式化用户响应"""
    role = user.roles[0] if user.roles else None
    return UserSchema(
        id=user.id,
        username=user.username,
        name=user.name,
        email=user.email,
        status=user.status,
        hospital_id=user.hospital_id,
        department_id=user.department_id,
        hospital_name=user.hospital.name if user.hospital else None,
        department_name=user.department.his_name if user.department else None,
        created_at=user.created_at,
        updated_at=user.updated_at,
        role_id=role.id if role else 0,
        role_name=role.name if role else "",
        role_type=role.role_type if role else RoleType.HOSPITAL_USER,
        menu_permissions=role.menu_permissions if role else None
    )


@router.get("", response_model=dict)
async def get_users(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=10000),
    keyword: str = Query(None),
    role_id: int = Query(None, description="按角色筛选"),
    hospital_id: int = Query(None, description="按医疗机构筛选"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取用户列表"""
    current_role_type = get_current_user_role_type(current_user)
    
    # 科室用户和全院用户不能查看用户列表
    if current_role_type in [RoleType.DEPARTMENT_USER, RoleType.HOSPITAL_USER]:
        raise HTTPException(status_code=403, detail="无权限查看用户列表")
    
    query = db.query(User)
    
    # 管理员不能看到维护者用户
    if current_role_type != RoleType.MAINTAINER:
        # 排除拥有维护者角色的用户
        maintainer_role = db.query(Role).filter(Role.role_type == RoleType.MAINTAINER).first()
        if maintainer_role:
            from app.models.associations import user_roles
            maintainer_user_ids = db.query(user_roles.c.user_id).filter(
                user_roles.c.role_id == maintainer_role.id
            ).subquery()
            query = query.filter(~User.id.in_(maintainer_user_ids))
    
    # 关键字搜索
    if keyword:
        query = query.filter(
            (User.username.ilike(f"%{keyword}%")) |
            (User.name.ilike(f"%{keyword}%")) |
            (User.email.ilike(f"%{keyword}%"))
        )
    
    # 按角色筛选
    if role_id:
        from app.models.associations import user_roles
        query = query.join(user_roles).filter(user_roles.c.role_id == role_id)
    
    # 按医疗机构筛选
    if hospital_id:
        query = query.filter(User.hospital_id == hospital_id)
    
    total = query.count()
    users = query.offset((page - 1) * size).limit(size).all()
    
    items = [format_user_response(user) for user in users]
    
    return {"total": total, "items": items}


@router.post("", response_model=UserSchema, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_create: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """创建用户"""
    # 获取目标角色
    role = db.query(Role).filter(Role.id == user_create.role_id).first()
    if not role:
        raise HTTPException(status_code=400, detail=f"角色ID {user_create.role_id} 不存在")
    
    check_user_permission(current_user, target_role=role)
    
    # 验证用户数据
    validate_user_data(role, user_create.hospital_id, user_create.department_id, db)
    
    # 检查用户名是否已存在
    if db.query(User).filter(User.username == user_create.username).first():
        raise HTTPException(status_code=400, detail="用户名已存在")
    
    # 检查邮箱是否已存在
    if user_create.email:
        if db.query(User).filter(User.email == user_create.email).first():
            raise HTTPException(status_code=400, detail="邮箱已存在")
    
    # 验证医疗机构
    if user_create.hospital_id:
        hospital = db.query(Hospital).filter(Hospital.id == user_create.hospital_id).first()
        if not hospital:
            raise HTTPException(status_code=400, detail=f"医疗机构ID {user_create.hospital_id} 不存在")
    
    # 创建用户
    user = User(
        username=user_create.username,
        name=user_create.name,
        email=user_create.email,
        hashed_password=get_password_hash(user_create.password),
        hospital_id=user_create.hospital_id,
        department_id=user_create.department_id,
        status="active"
    )
    user.roles = [role]
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    return format_user_response(user)


@router.get("/{user_id}", response_model=UserSchema)
async def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取用户详情"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    check_user_permission(current_user, target_user=user)
    
    return format_user_response(user)


@router.put("/{user_id}", response_model=UserSchema)
async def update_user(
    user_id: int,
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """更新用户"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    check_user_permission(current_user, target_user=user)
    
    # 如果要修改角色
    new_role = None
    if user_update.role_id is not None:
        new_role = db.query(Role).filter(Role.id == user_update.role_id).first()
        if not new_role:
            raise HTTPException(status_code=400, detail=f"角色ID {user_update.role_id} 不存在")
        check_user_permission(current_user, target_role=new_role)
    
    # 确定最终的角色、医疗机构、科室
    final_role = new_role if new_role else (user.roles[0] if user.roles else None)
    final_hospital_id = user_update.hospital_id if user_update.hospital_id is not None else user.hospital_id
    final_department_id = user_update.department_id if user_update.department_id is not None else user.department_id
    
    # 如果角色类型变更，可能需要清除医疗机构和科室
    if new_role:
        if new_role.role_type in [RoleType.ADMIN, RoleType.MAINTAINER]:
            final_hospital_id = None
            final_department_id = None
        elif new_role.role_type == RoleType.HOSPITAL_USER:
            final_department_id = None
    
    # 验证数据一致性
    if final_role:
        validate_user_data(final_role, final_hospital_id, final_department_id, db)
    
    # 更新字段
    if user_update.name is not None:
        user.name = user_update.name
    
    if user_update.email is not None:
        existing = db.query(User).filter(User.email == user_update.email, User.id != user_id).first()
        if existing:
            raise HTTPException(status_code=400, detail="邮箱已存在")
        user.email = user_update.email
    
    if user_update.password is not None:
        user.hashed_password = get_password_hash(user_update.password)
    
    if user_update.status is not None:
        user.status = user_update.status
    
    if new_role:
        user.roles = [new_role]
    
    user.hospital_id = final_hospital_id
    user.department_id = final_department_id
    
    db.commit()
    db.refresh(user)
    
    return format_user_response(user)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """删除用户"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    if user.id == current_user.id:
        raise HTTPException(status_code=400, detail="不能删除自己")
    
    check_user_permission(current_user, target_user=user)
    
    db.delete(user)
    db.commit()
    
    return None
