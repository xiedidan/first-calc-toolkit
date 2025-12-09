"""
导向阶梯管理API
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_, desc, asc

from app.api import deps
from app.models.orientation_ladder import OrientationLadder
from app.models.orientation_rule import OrientationRule, OrientationCategory
from app.schemas.orientation_ladder import (
    OrientationLadder as OrientationLadderSchema,
    OrientationLadderCreate,
    OrientationLadderUpdate,
    OrientationLadderList,
)
from app.utils.hospital_filter import (
    apply_hospital_filter,
    get_current_hospital_id_or_raise,
    validate_hospital_access,
    set_hospital_id_for_create,
)

router = APIRouter()


@router.get("", response_model=OrientationLadderList)
def get_orientation_ladders(
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_current_user),
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(10, ge=1, le=1000, description="每页数量"),
    rule_id: Optional[int] = Query(None, description="按导向规则ID筛选"),
):
    """获取导向阶梯列表"""
    query = db.query(OrientationLadder)
    
    # 应用医疗机构过滤
    query = apply_hospital_filter(query, OrientationLadder, required=True)
    
    # 按导向规则筛选
    if rule_id:
        query = query.filter(OrientationLadder.rule_id == rule_id)
    
    # 预加载导向规则信息
    query = query.options(joinedload(OrientationLadder.rule))
    
    # 按阶梯次序升序排序
    query = query.order_by(asc(OrientationLadder.ladder_order))
    
    # 总数
    total = query.count()
    
    # 分页
    items = query.offset((page - 1) * size).limit(size).all()
    
    # 预加载 rule_name 字段
    for item in items:
        item.rule_name = item.rule.name if item.rule else None
    
    return OrientationLadderList(total=total, items=items)


@router.post("", response_model=OrientationLadderSchema)
def create_orientation_ladder(
    ladder_in: OrientationLadderCreate,
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_current_user),
):
    """创建导向阶梯"""
    # 获取当前医疗机构ID
    hospital_id = get_current_hospital_id_or_raise()
    
    # 验证导向规则存在且属于当前医疗机构
    rule_query = db.query(OrientationRule).filter(OrientationRule.id == ladder_in.rule_id)
    rule_query = apply_hospital_filter(rule_query, OrientationRule, required=True)
    rule = rule_query.first()
    if not rule:
        raise HTTPException(status_code=404, detail="导向规则不存在")
    
    # 验证导向类别必须为"基准阶梯"或"直接阶梯"
    if rule.category not in [OrientationCategory.benchmark_ladder, OrientationCategory.direct_ladder]:
        raise HTTPException(
            status_code=400,
            detail="只有'基准阶梯'或'直接阶梯'类别的导向规则可以创建阶梯"
        )
    
    # 检查同一导向下阶梯次序是否已存在
    existing_query = db.query(OrientationLadder).filter(
        OrientationLadder.rule_id == ladder_in.rule_id,
        OrientationLadder.ladder_order == ladder_in.ladder_order
    )
    existing_query = apply_hospital_filter(existing_query, OrientationLadder, required=True)
    existing = existing_query.first()
    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"该导向规则下阶梯次序'{ladder_in.ladder_order}'已存在"
        )
    
    # 自动设置hospital_id
    ladder_data = ladder_in.model_dump()
    ladder_data = set_hospital_id_for_create(ladder_data, hospital_id)
    
    # 创建导向阶梯
    ladder = OrientationLadder(**ladder_data)
    db.add(ladder)
    db.commit()
    db.refresh(ladder)
    
    # 预加载 rule_name
    ladder.rule_name = rule.name
    
    return ladder


@router.get("/{ladder_id}", response_model=OrientationLadderSchema)
def get_orientation_ladder(
    ladder_id: int,
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_current_user),
):
    """获取导向阶梯详情"""
    query = db.query(OrientationLadder).filter(OrientationLadder.id == ladder_id)
    query = apply_hospital_filter(query, OrientationLadder, required=True)
    query = query.options(joinedload(OrientationLadder.rule))
    ladder = query.first()
    if not ladder:
        raise HTTPException(status_code=404, detail="导向阶梯不存在")
    
    # 预加载 rule_name
    ladder.rule_name = ladder.rule.name if ladder.rule else None
    
    return ladder


@router.put("/{ladder_id}", response_model=OrientationLadderSchema)
def update_orientation_ladder(
    ladder_id: int,
    ladder_in: OrientationLadderUpdate,
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_current_user),
):
    """更新导向阶梯"""
    query = db.query(OrientationLadder).filter(OrientationLadder.id == ladder_id)
    query = apply_hospital_filter(query, OrientationLadder, required=True)
    ladder = query.first()
    if not ladder:
        raise HTTPException(status_code=404, detail="导向阶梯不存在")
    
    # 验证数据所属医疗机构
    validate_hospital_access(db, ladder)
    
    # 如果更新导向规则ID，验证新规则存在且类别正确
    if ladder_in.rule_id and ladder_in.rule_id != ladder.rule_id:
        rule_query = db.query(OrientationRule).filter(OrientationRule.id == ladder_in.rule_id)
        rule_query = apply_hospital_filter(rule_query, OrientationRule, required=True)
        rule = rule_query.first()
        if not rule:
            raise HTTPException(status_code=404, detail="导向规则不存在")
        
        if rule.category not in [OrientationCategory.benchmark_ladder, OrientationCategory.direct_ladder]:
            raise HTTPException(
                status_code=400,
                detail="只有'基准阶梯'或'直接阶梯'类别的导向规则可以创建阶梯"
            )
    
    # 如果更新阶梯次序，检查是否与其他阶梯重复
    if ladder_in.ladder_order and ladder_in.ladder_order != ladder.ladder_order:
        rule_id = ladder_in.rule_id if ladder_in.rule_id else ladder.rule_id
        existing_query = db.query(OrientationLadder).filter(
            OrientationLadder.rule_id == rule_id,
            OrientationLadder.ladder_order == ladder_in.ladder_order,
            OrientationLadder.id != ladder_id
        )
        existing_query = apply_hospital_filter(existing_query, OrientationLadder, required=True)
        existing = existing_query.first()
        if existing:
            raise HTTPException(
                status_code=400,
                detail=f"该导向规则下阶梯次序'{ladder_in.ladder_order}'已存在"
            )
    
    # 更新字段
    update_data = ladder_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(ladder, field, value)
    
    db.commit()
    db.refresh(ladder)
    
    # 预加载 rule_name
    db_rule = db.query(OrientationRule).filter(OrientationRule.id == ladder.rule_id).first()
    ladder.rule_name = db_rule.name if db_rule else None
    
    return ladder


@router.delete("/{ladder_id}")
def delete_orientation_ladder(
    ladder_id: int,
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_current_user),
):
    """删除导向阶梯"""
    query = db.query(OrientationLadder).filter(OrientationLadder.id == ladder_id)
    query = apply_hospital_filter(query, OrientationLadder, required=True)
    ladder = query.first()
    if not ladder:
        raise HTTPException(status_code=404, detail="导向阶梯不存在")
    
    # 验证数据所属医疗机构
    validate_hospital_access(db, ladder)
    
    # 删除导向阶梯
    db.delete(ladder)
    db.commit()
    
    return {"message": "导向阶梯删除成功"}
