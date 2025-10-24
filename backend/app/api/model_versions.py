"""
模型版本管理API
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.models.model_version import ModelVersion
from app.models.model_node import ModelNode
from app.schemas.model_version import (
    ModelVersionCreate,
    ModelVersionUpdate,
    ModelVersionResponse,
    ModelVersionListResponse,
)

router = APIRouter()


@router.get("", response_model=ModelVersionListResponse)
def get_model_versions(
    skip: int = 0,
    limit: int = 20,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取模型版本列表"""
    query = db.query(ModelVersion)
    
    # 搜索过滤
    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            (ModelVersion.version.ilike(search_pattern)) |
            (ModelVersion.name.ilike(search_pattern)) |
            (ModelVersion.description.ilike(search_pattern))
        )
    
    # 按创建时间倒序排列
    query = query.order_by(ModelVersion.created_at.desc())
    
    total = query.count()
    items = query.offset(skip).limit(limit).all()
    
    return {"total": total, "items": items}


@router.post("", response_model=ModelVersionResponse, status_code=status.HTTP_201_CREATED)
def create_model_version(
    version_in: ModelVersionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """创建模型版本"""
    # 检查版本号是否已存在
    existing = db.query(ModelVersion).filter(ModelVersion.version == version_in.version).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="版本号已存在"
        )
    
    # 创建新版本
    db_version = ModelVersion(
        version=version_in.version,
        name=version_in.name,
        description=version_in.description,
    )
    db.add(db_version)
    db.commit()
    db.refresh(db_version)
    
    # 如果指定了基础版本，复制其结构
    if version_in.base_version_id:
        base_version = db.query(ModelVersion).filter(ModelVersion.id == version_in.base_version_id).first()
        if not base_version:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="基础版本不存在"
            )
        
        # 复制节点结构
        _copy_nodes(db, base_version.id, db_version.id)
    
    return db_version


@router.get("/{version_id}", response_model=ModelVersionResponse)
def get_model_version(
    version_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取模型版本详情"""
    version = db.query(ModelVersion).filter(ModelVersion.id == version_id).first()
    if not version:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="模型版本不存在"
        )
    return version


@router.put("/{version_id}", response_model=ModelVersionResponse)
def update_model_version(
    version_id: int,
    version_in: ModelVersionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """更新模型版本"""
    version = db.query(ModelVersion).filter(ModelVersion.id == version_id).first()
    if not version:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="模型版本不存在"
        )
    
    # 更新字段
    if version_in.name is not None:
        version.name = version_in.name
    if version_in.description is not None:
        version.description = version_in.description
    
    db.commit()
    db.refresh(version)
    return version


@router.delete("/{version_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_model_version(
    version_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """删除模型版本"""
    version = db.query(ModelVersion).filter(ModelVersion.id == version_id).first()
    if not version:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="模型版本不存在"
        )
    
    # 不允许删除激活的版本
    if version.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不能删除激活的版本"
        )
    
    db.delete(version)
    db.commit()


@router.put("/{version_id}/activate", response_model=ModelVersionResponse)
def activate_model_version(
    version_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """激活模型版本"""
    version = db.query(ModelVersion).filter(ModelVersion.id == version_id).first()
    if not version:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="模型版本不存在"
        )
    
    # 取消其他版本的激活状态
    db.query(ModelVersion).update({"is_active": False})
    
    # 激活当前版本
    version.is_active = True
    db.commit()
    db.refresh(version)
    
    return version


def _copy_nodes(db: Session, source_version_id: int, target_version_id: int):
    """复制节点结构"""
    # 获取源版本的所有根节点
    source_nodes = db.query(ModelNode).filter(
        ModelNode.version_id == source_version_id,
        ModelNode.parent_id.is_(None)
    ).all()
    
    # 递归复制节点
    for node in source_nodes:
        _copy_node_recursive(db, node, target_version_id, None)
    
    db.commit()


def _copy_node_recursive(db: Session, source_node: ModelNode, target_version_id: int, target_parent_id: Optional[int]):
    """递归复制节点"""
    # 创建新节点
    new_node = ModelNode(
        version_id=target_version_id,
        parent_id=target_parent_id,
        sort_order=source_node.sort_order,
        name=source_node.name,
        code=source_node.code,
        node_type=source_node.node_type,
        is_leaf=source_node.is_leaf,
        calc_type=source_node.calc_type,
        weight=source_node.weight,
        unit=source_node.unit,
        business_guide=source_node.business_guide,
        script=source_node.script,
        rule=source_node.rule,
    )
    db.add(new_node)
    db.flush()  # 获取新节点的ID
    
    # 递归复制子节点
    for child in source_node.children:
        _copy_node_recursive(db, child, target_version_id, new_node.id)
