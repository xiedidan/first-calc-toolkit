"""
Role management API endpoints
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.api.deps import get_db, get_current_active_user
from app.models import User, Role, RoleType
from app.models.associations import user_roles
from app.schemas import Role as RoleSchema, RoleCreate, RoleUpdate, RoleListItem, ROLE_TYPE_DISPLAY

router = APIRouter()


# 系统菜单定义（用于角色权限配置）
SYSTEM_MENUS = [
    {"path": "/dashboard", "name": "首页", "children": None},
    {"path": "/data-template-publish", "name": "数据模板发布", "children": None},
    {"path": "/data-quality", "name": "数据质量报告", "children": [
        {"path": "/data-issues", "name": "数据问题记录", "children": None},
    ]},
    {"path": "/intelligent-classification", "name": "智能分类分级", "children": [
        {"path": "/classification-tasks", "name": "医技分类任务", "children": None},
        {"path": "/classification-plans", "name": "分类预案管理", "children": None},
    ]},
    {"path": "/model", "name": "评估模型管理", "children": [
        {"path": "/model-versions", "name": "模型版本管理", "children": None},
        {"path": "/dimension-items", "name": "维度目录管理", "children": None},
        {"path": "/cost-benchmarks", "name": "成本基准管理", "children": None},
        {"path": "/calculation-workflows", "name": "计算流程管理", "children": None},
    ]},
    {"path": "/orientation", "name": "业务导向管理", "children": [
        {"path": "/orientation-rules", "name": "导向规则管理", "children": None},
        {"path": "/orientation-benchmarks", "name": "导向基准管理", "children": None},
        {"path": "/orientation-ladders", "name": "导向阶梯管理", "children": None},
    ]},
    {"path": "/calculation-tasks", "name": "计算任务管理", "children": None},
    {"path": "/results", "name": "业务价值报表", "children": None},
    {"path": "/adv-modeling", "name": "ADV自动建模（规划中）", "children": None},
    {"path": "/intelligent-query", "name": "智能问数系统（规划中）", "children": None},
    {"path": "/operation-analysis", "name": "运营分析报告（规划中）", "children": None},
    {"path": "/base-data", "name": "基础数据管理", "children": [
        {"path": "/departments", "name": "科室对照管理", "children": None},
        {"path": "/charge-items", "name": "收费项目管理", "children": None},
        {"path": "/reference-values", "name": "参考价值管理", "children": None},
        {"path": "/data-templates", "name": "数据模板管理", "children": None},
    ]},
    {"path": "/data-sources", "name": "数据源管理", "children": None},
    {"path": "/system", "name": "系统设置", "children": [
        {"path": "/system-settings", "name": "参数管理", "children": None},
        {"path": "/users", "name": "用户管理", "children": None},
        {"path": "/roles", "name": "用户角色管理", "children": None},
        {"path": "/ai-config", "name": "AI接口管理", "children": None},
        {"path": "/hospitals", "name": "医疗机构管理", "children": None},
    ]},
]


def get_current_user_role_type(user: User) -> RoleType:
    """获取当前用户的角色类型"""
    if user.roles:
        return user.roles[0].role_type
    return RoleType.HOSPITAL_USER


def check_role_permission(current_user: User, target_role_type: RoleType = None):
    """检查当前用户是否有权限操作目标角色类型"""
    current_role_type = get_current_user_role_type(current_user)
    
    # 只有管理员和维护者可以管理角色
    if current_role_type not in [RoleType.ADMIN, RoleType.MAINTAINER]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有管理员和维护者可以管理角色"
        )
    
    # 管理员不能操作维护者角色
    if target_role_type == RoleType.MAINTAINER and current_role_type != RoleType.MAINTAINER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有维护者可以管理维护者角色"
        )


@router.get("/menus", response_model=List[dict])
async def get_system_menus(
    current_user: User = Depends(get_current_active_user)
):
    """获取系统菜单列表（用于角色权限配置）"""
    check_role_permission(current_user)
    return SYSTEM_MENUS


@router.get("", response_model=dict)
async def get_roles(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    keyword: str = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取角色列表"""
    check_role_permission(current_user)
    
    current_role_type = get_current_user_role_type(current_user)
    
    # 构建查询
    query = db.query(Role)
    
    # 管理员不能看到维护者角色
    if current_role_type != RoleType.MAINTAINER:
        query = query.filter(Role.role_type != RoleType.MAINTAINER)
    
    # 关键字搜索
    if keyword:
        query = query.filter(
            (Role.name.ilike(f"%{keyword}%")) |
            (Role.code.ilike(f"%{keyword}%"))
        )
    
    total = query.count()
    roles = query.offset((page - 1) * size).limit(size).all()
    
    # 统计每个角色的用户数
    items = []
    for role in roles:
        user_count = db.query(func.count(user_roles.c.user_id)).filter(
            user_roles.c.role_id == role.id
        ).scalar()
        
        items.append(RoleListItem(
            id=role.id,
            name=role.name,
            code=role.code,
            role_type=role.role_type,
            role_type_display=ROLE_TYPE_DISPLAY.get(role.role_type, str(role.role_type)),
            description=role.description,
            user_count=user_count,
            created_at=role.created_at
        ))
    
    return {"total": total, "items": items}


@router.post("", response_model=RoleSchema, status_code=status.HTTP_201_CREATED)
async def create_role(
    role_create: RoleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """创建角色"""
    check_role_permission(current_user, role_create.role_type)
    
    # 检查code是否已存在
    existing = db.query(Role).filter(Role.code == role_create.code).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"角色代码 {role_create.code} 已存在"
        )
    
    role = Role(
        name=role_create.name,
        code=role_create.code,
        role_type=role_create.role_type,
        menu_permissions=role_create.menu_permissions,
        description=role_create.description
    )
    
    db.add(role)
    db.commit()
    db.refresh(role)
    
    return RoleSchema(
        id=role.id,
        name=role.name,
        code=role.code,
        role_type=role.role_type,
        menu_permissions=role.menu_permissions,
        description=role.description,
        created_at=role.created_at,
        updated_at=role.updated_at
    )


@router.get("/{role_id}", response_model=RoleSchema)
async def get_role(
    role_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取角色详情"""
    check_role_permission(current_user)
    
    role = db.query(Role).filter(Role.id == role_id).first()
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="角色不存在"
        )
    
    current_role_type = get_current_user_role_type(current_user)
    if role.role_type == RoleType.MAINTAINER and current_role_type != RoleType.MAINTAINER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权查看维护者角色"
        )
    
    return RoleSchema(
        id=role.id,
        name=role.name,
        code=role.code,
        role_type=role.role_type,
        menu_permissions=role.menu_permissions,
        description=role.description,
        created_at=role.created_at,
        updated_at=role.updated_at
    )


@router.put("/{role_id}", response_model=RoleSchema)
async def update_role(
    role_id: int,
    role_update: RoleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """更新角色"""
    role = db.query(Role).filter(Role.id == role_id).first()
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="角色不存在"
        )
    
    check_role_permission(current_user, role.role_type)
    
    # 如果要修改role_type，也需要检查新类型的权限
    if role_update.role_type and role_update.role_type != role.role_type:
        check_role_permission(current_user, role_update.role_type)
    
    # 更新字段
    if role_update.name is not None:
        role.name = role_update.name
    if role_update.role_type is not None:
        role.role_type = role_update.role_type
    if role_update.menu_permissions is not None:
        role.menu_permissions = role_update.menu_permissions
    if role_update.description is not None:
        role.description = role_update.description
    
    db.commit()
    db.refresh(role)
    
    return RoleSchema(
        id=role.id,
        name=role.name,
        code=role.code,
        role_type=role.role_type,
        menu_permissions=role.menu_permissions,
        description=role.description,
        created_at=role.created_at,
        updated_at=role.updated_at
    )


@router.delete("/{role_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_role(
    role_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """删除角色"""
    role = db.query(Role).filter(Role.id == role_id).first()
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="角色不存在"
        )
    
    check_role_permission(current_user, role.role_type)
    
    # 检查是否有用户使用此角色
    user_count = db.query(func.count(user_roles.c.user_id)).filter(
        user_roles.c.role_id == role_id
    ).scalar()
    
    if user_count > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"该角色下有 {user_count} 个用户，无法删除"
        )
    
    db.delete(role)
    db.commit()
    
    return None
