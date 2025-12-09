"""
模型节点管理API
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.models.model_node import ModelNode
from app.models.model_version import ModelVersion
from app.models.orientation_rule import OrientationRule
from app.schemas.model_node import (
    ModelNodeCreate,
    ModelNodeUpdate,
    ModelNodeResponse,
    ModelNodeListResponse,
    TestCodeRequest,
    TestCodeResponse,
)
from app.utils.hospital_filter import (
    apply_hospital_filter,
    validate_hospital_access,
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
    # 验证版本是否存在且属于当前医疗机构
    query = db.query(ModelVersion).filter(ModelVersion.id == version_id)
    query = apply_hospital_filter(query, ModelVersion, required=True)
    version = query.first()
    if not version:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="模型版本不存在"
        )
    
    # 查询节点，预加载导向规则
    query = db.query(ModelNode).options(joinedload(ModelNode.orientation_rule)).filter(ModelNode.version_id == version_id)
    
    # 如果指定了parent_id，只返回该父节点的子节点
    if parent_id is not None:
        query = query.filter(ModelNode.parent_id == parent_id)
    else:
        # 否则返回根节点
        query = query.filter(ModelNode.parent_id.is_(None))
    
    # 按sort_order排序
    query = query.order_by(ModelNode.sort_order)
    
    items = query.all()
    
    # 递归加载子节点并设置导向规则名称
    for item in items:
        _load_children(db, item)
        item.has_children = len(item.children) > 0
        # 设置导向规则名称列表
        _load_orientation_rule_names(db, item)
    
    return {"total": len(items), "items": items}


@router.post("", response_model=ModelNodeResponse, status_code=status.HTTP_201_CREATED)
def create_model_node(
    node_in: ModelNodeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """创建模型节点"""
    # 验证版本是否存在且属于当前医疗机构
    query = db.query(ModelVersion).filter(ModelVersion.id == node_in.version_id)
    query = apply_hospital_filter(query, ModelVersion, required=True)
    version = query.first()
    if not version:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="模型版本不存在"
        )
    
    # 验证版本所属医疗机构
    validate_hospital_access(db, version)
    
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
    
    # 如果是末级维度，验证必填字段（script不再必填）
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
    
    # 如果指定了 orientation_rule_ids，验证导向规则是否存在且仅末级节点可以关联
    if hasattr(node_in, 'orientation_rule_ids') and node_in.orientation_rule_ids:
        # 检查是否为末级节点
        if not node_in.is_leaf:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="仅末级节点可以关联导向规则"
            )
        
        # 验证所有导向规则是否存在
        for rule_id in node_in.orientation_rule_ids:
            orientation_rule = db.query(OrientationRule).filter(
                OrientationRule.id == rule_id
            ).first()
            if not orientation_rule:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"导向规则ID {rule_id} 不存在"
                )
            # 验证导向规则是否属于同一医疗机构
            if orientation_rule.hospital_id != version.hospital_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"导向规则ID {rule_id} 不属于当前医疗机构"
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
    
    # 重新查询以预加载导向规则
    db_node = db.query(ModelNode).options(joinedload(ModelNode.orientation_rule)).filter(ModelNode.id == db_node.id).first()
    
    # 加载子节点信息
    _load_children(db, db_node)
    db_node.has_children = len(db_node.children) > 0
    
    # 设置导向规则名称列表
    _load_orientation_rule_names(db, db_node)
    
    return db_node


@router.get("/{node_id}", response_model=ModelNodeResponse)
def get_model_node(
    node_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取模型节点详情"""
    node = db.query(ModelNode).options(joinedload(ModelNode.orientation_rule)).filter(ModelNode.id == node_id).first()
    if not node:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="模型节点不存在"
        )
    
    # 验证节点所属的版本是否属于当前医疗机构
    validate_hospital_access(db, node.version)
    
    # 加载子节点
    _load_children(db, node)
    
    # 设置导向规则名称列表
    _load_orientation_rule_names(db, node)
    
    return node


@router.put("/{node_id}", response_model=ModelNodeResponse)
def update_model_node(
    node_id: int,
    node_in: ModelNodeUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """更新模型节点"""
    node = db.query(ModelNode).options(joinedload(ModelNode.orientation_rule)).filter(ModelNode.id == node_id).first()
    if not node:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="模型节点不存在"
        )
    
    # 验证节点所属的版本是否属于当前医疗机构
    validate_hospital_access(db, node.version)
    
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
    
    # 如果更新 orientation_rule_ids，验证导向规则是否存在且仅末级节点可以关联
    if hasattr(node_in, 'orientation_rule_ids') and node_in.orientation_rule_ids is not None:
        # 只有当要关联导向规则（非空列表）时，才检查是否为末级节点
        if node_in.orientation_rule_ids:
            # 检查是否为末级节点
            is_leaf = node_in.is_leaf if node_in.is_leaf is not None else node.is_leaf
            if not is_leaf:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="仅末级节点可以关联导向规则"
                )
            
            # 验证所有导向规则是否存在
            for rule_id in node_in.orientation_rule_ids:
                orientation_rule = db.query(OrientationRule).filter(
                    OrientationRule.id == rule_id
                ).first()
                if not orientation_rule:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"导向规则ID {rule_id} 不存在"
                    )
                # 验证导向规则是否属于同一医疗机构
                if orientation_rule.hospital_id != node.version.hospital_id:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail=f"导向规则ID {rule_id} 不属于当前医疗机构"
                    )
        # 空列表表示清空导向规则，允许任何节点执行此操作
    
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
    
    db.commit()
    db.refresh(node)
    
    # 加载子节点信息
    _load_children(db, node)
    node.has_children = len(node.children) > 0
    
    # 设置导向规则名称列表
    _load_orientation_rule_names(db, node)
    
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
    
    # 验证节点所属的版本是否属于当前医疗机构
    validate_hospital_access(db, node.version)
    
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


def _load_orientation_rule_names(db: Session, node: ModelNode):
    """加载节点的导向规则名称列表"""
    if node.orientation_rule_ids:
        rules = db.query(OrientationRule).filter(
            OrientationRule.id.in_(node.orientation_rule_ids)
        ).all()
        node.orientation_rule_names = [rule.name for rule in rules]
    else:
        node.orientation_rule_names = []


def _load_children(db: Session, node: ModelNode):
    """递归加载子节点"""
    children = db.query(ModelNode).options(joinedload(ModelNode.orientation_rule)).filter(ModelNode.parent_id == node.id).order_by(ModelNode.sort_order).all()
    node.children = children
    for child in children:
        _load_children(db, child)
        child.has_children = len(child.children) > 0
        # 设置导向规则名称列表
        _load_orientation_rule_names(db, child)


@router.get("/version/{version_id}/leaf")
def get_leaf_nodes(
    version_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取指定版本的所有末级维度（叶子节点）"""
    # 验证版本是否存在
    version = db.query(ModelVersion).filter(ModelVersion.id == version_id).first()
    if not version:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="模型版本不存在"
        )
    
    # 查询所有末级节点
    leaf_nodes = db.query(ModelNode).filter(
        ModelNode.version_id == version_id,
        ModelNode.is_leaf == True
    ).order_by(ModelNode.sort_order).all()
    
    # 构建完整路径
    result = []
    for node in leaf_nodes:
        full_path = _build_node_path(node, db)
        result.append({
            "id": node.id,
            "name": node.name,
            "code": node.code,
            "full_path": full_path
        })
    
    return result


@router.get("/version/{version_id}/cost-dimensions")
def get_cost_dimensions(
    version_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取指定版本中所有序列下成本维度的末级维度"""
    # 验证版本是否存在且属于当前医疗机构
    query = db.query(ModelVersion).filter(ModelVersion.id == version_id)
    query = apply_hospital_filter(query, ModelVersion, required=True)
    version = query.first()
    if not version:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="模型版本不存在或不属于当前医疗机构"
        )
    
    # 查找所有序列节点（node_type='sequence'）
    sequences = db.query(ModelNode).filter(
        ModelNode.version_id == version_id,
        ModelNode.node_type == 'sequence'
    ).all()
    
    if not sequences:
        return {"total": 0, "items": []}
    
    # 收集所有序列下名为"成本"的维度
    all_leaf_nodes = []
    for sequence in sequences:
        # 查找该序列下名为"成本"的一级维度
        cost_dimension = db.query(ModelNode).filter(
            ModelNode.version_id == version_id,
            ModelNode.parent_id == sequence.id,
            ModelNode.name == '成本'
        ).first()
        
        if cost_dimension:
            # 递归查找成本维度下的所有末级维度
            leaf_nodes = _find_leaf_nodes_recursive(db, cost_dimension.id, version_id)
            all_leaf_nodes.extend(leaf_nodes)
    
    # 构建返回结果，包含序列信息以便区分
    result = []
    for node in all_leaf_nodes:
        # 获取节点所属的序列信息
        sequence_name = _get_sequence_name(db, node, version_id)
        result.append({
            "id": node.id,
            "name": f"{node.name}（{sequence_name}）",  # 在名称中显示所属序列
            "code": node.code
        })
    
    return {"total": len(result), "items": result}


def _build_node_path(node: ModelNode, db: Session) -> str:
    """构建节点的完整路径"""
    path_parts = [node.name]
    current = node
    
    while current.parent_id:
        parent = db.query(ModelNode).filter(ModelNode.id == current.parent_id).first()
        if parent:
            path_parts.insert(0, parent.name)
            current = parent
        else:
            break
    
    return " > ".join(path_parts)


def _find_leaf_nodes_recursive(db: Session, parent_id: int, version_id: int) -> list:
    """递归查找指定父节点下的所有末级维度"""
    # 查找直接子节点
    children = db.query(ModelNode).filter(
        ModelNode.version_id == version_id,
        ModelNode.parent_id == parent_id
    ).order_by(ModelNode.sort_order).all()
    
    leaf_nodes = []
    for child in children:
        if child.is_leaf:
            # 如果是末级维度，直接添加
            leaf_nodes.append(child)
        else:
            # 如果不是末级维度，递归查找其子节点
            leaf_nodes.extend(_find_leaf_nodes_recursive(db, child.id, version_id))
    
    return leaf_nodes


def _get_sequence_name(db: Session, node: ModelNode, version_id: int) -> str:
    """获取节点所属的序列名称"""
    current = node
    # 向上查找直到找到序列节点
    while current.parent_id:
        parent = db.query(ModelNode).filter(ModelNode.id == current.parent_id).first()
        if not parent:
            break
        if parent.node_type == 'sequence':
            return parent.name
        current = parent
    return "未知序列"
