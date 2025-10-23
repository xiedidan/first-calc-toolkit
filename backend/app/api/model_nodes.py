"""
模型节点管理API
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.models.model_node import ModelNode
from app.models.model_version import ModelVersion
from app.schemas.model_node import (
    ModelNodeCreate,
    ModelNodeUpdate,
    ModelNodeResponse,
    ModelNodeListResponse,
    TestCodeRequest,
    TestCodeResponse,
)

router = APIRouter()


@router.get("", response_model=ModelNodeListResponse)
def get_model_nodes(
    version_id: int,
    parent_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取模型节点列表"""
    # 验证版本是否存在
    version = db.query(ModelVersion).filter(ModelVersion.id == version_id).first()
    if not version:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="模型版本不存在"
        )
    
    # 查询节点
    query = db.query(ModelNode).filter(ModelNode.version_id == version_id)
    
    # 如果指定了parent_id，只返回该父节点的子节点
    if parent_id is not None:
        query = query.filter(ModelNode.parent_id == parent_id)
    else:
        # 否则返回根节点
        query = query.filter(ModelNode.parent_id.is_(None))
    
    # 按sort_order排序
    query = query.order_by(ModelNode.sort_order)
    
    items = query.all()
    
    # 递归加载子节点
    for item in items:
        _load_children(db, item)
        item.has_children = len(item.children) > 0
    
    return {"total": len(items), "items": items}


@router.post("", response_model=ModelNodeResponse, status_code=status.HTTP_201_CREATED)
def create_model_node(
    node_in: ModelNodeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """创建模型节点"""
    # 验证版本是否存在
    version = db.query(ModelVersion).filter(ModelVersion.id == node_in.version_id).first()
    if not version:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="模型版本不存在"
        )
    
    # 如果指定了父节点，验证父节点是否存在
    if node_in.parent_id:
        parent = db.query(ModelNode).filter(
            ModelNode.id == node_in.parent_id,
            ModelNode.version_id == node_in.version_id
        ).first()
        if not parent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="父节点不存在"
            )
        
        # 检查父节点是否被标记为末级维度
        if parent.is_leaf:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="父节点已被标记为末级维度，不能添加子节点"
            )
    
    # 检查同一版本下节点编码是否重复
    existing = db.query(ModelNode).filter(
        ModelNode.version_id == node_in.version_id,
        ModelNode.code == node_in.code
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="节点编码已存在"
        )
    
    # 如果是末级维度，验证必填字段
    if node_in.is_leaf:
        if not node_in.calc_type:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="末级维度必须指定算法类型"
            )
        if node_in.weight is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="末级维度必须指定权重/单价"
            )
        if not node_in.unit:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="末级维度必须指定单位"
            )
        if not node_in.script:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="末级维度必须指定计算脚本"
            )
    
    # 如果没有指定sort_order，自动设置为最大值+1
    if node_in.sort_order is None or node_in.sort_order == 0:
        max_order = db.query(ModelNode).filter(
            ModelNode.version_id == node_in.version_id,
            ModelNode.parent_id == node_in.parent_id
        ).count()
        node_in.sort_order = max_order + 1
    
    # 创建节点
    db_node = ModelNode(**node_in.model_dump())
    db.add(db_node)
    db.commit()
    db.refresh(db_node)
    
    # 加载子节点信息
    _load_children(db, db_node)
    db_node.has_children = len(db_node.children) > 0
    
    return db_node


@router.get("/{node_id}", response_model=ModelNodeResponse)
def get_model_node(
    node_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取模型节点详情"""
    node = db.query(ModelNode).filter(ModelNode.id == node_id).first()
    if not node:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="模型节点不存在"
        )
    
    # 加载子节点
    _load_children(db, node)
    
    return node


@router.put("/{node_id}", response_model=ModelNodeResponse)
def update_model_node(
    node_id: int,
    node_in: ModelNodeUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """更新模型节点"""
    node = db.query(ModelNode).filter(ModelNode.id == node_id).first()
    if not node:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="模型节点不存在"
        )
    
    # 如果更新编码，检查是否重复
    if node_in.code and node_in.code != node.code:
        existing = db.query(ModelNode).filter(
            ModelNode.version_id == node.version_id,
            ModelNode.code == node_in.code,
            ModelNode.id != node_id
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="节点编码已存在"
            )
    
    # 如果要设置为末级维度，检查是否有子节点
    if node_in.is_leaf is True:
        children_count = db.query(ModelNode).filter(ModelNode.parent_id == node_id).count()
        if children_count > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="该节点有子节点，不能设置为末级维度"
            )
    
    # 更新字段
    update_data = node_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(node, field, value)
    
    # 如果更新后是末级维度，验证必填字段
    if node.is_leaf:
        if not node.calc_type:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="末级维度必须指定算法类型"
            )
        if node.weight is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="末级维度必须指定权重/单价"
            )
        if not node.unit:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="末级维度必须指定单位"
            )
        if not node.script:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="末级维度必须指定计算脚本"
            )
    
    db.commit()
    db.refresh(node)
    
    # 加载子节点信息
    _load_children(db, node)
    node.has_children = len(node.children) > 0
    
    return node


@router.delete("/{node_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_model_node(
    node_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """删除模型节点"""
    node = db.query(ModelNode).filter(ModelNode.id == node_id).first()
    if not node:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="模型节点不存在"
        )
    
    # 删除节点（会级联删除子节点）
    db.delete(node)
    db.commit()


@router.post("/{node_id}/test-code", response_model=TestCodeResponse)
def test_node_code(
    node_id: int,
    test_in: TestCodeRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """测试节点代码"""
    node = db.query(ModelNode).filter(ModelNode.id == node_id).first()
    if not node:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="模型节点不存在"
        )
    
    try:
        # TODO: 实现代码测试逻辑
        # 这里需要根据脚本类型（SQL/Python）执行相应的测试
        # 暂时返回模拟结果
        return {
            "success": True,
            "result": {
                "message": "代码测试功能待实现",
                "script": test_in.script[:100] + "..." if len(test_in.script) > 100 else test_in.script
            }
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def _load_children(db: Session, node: ModelNode):
    """递归加载子节点"""
    children = db.query(ModelNode).filter(ModelNode.parent_id == node.id).order_by(ModelNode.sort_order).all()
    node.children = children
    for child in children:
        _load_children(db, child)
        child.has_children = len(child.children) > 0
