"""
学科规则API
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.discipline_rule import DisciplineRule
from app.models.model_version import ModelVersion
from app.models.user import User
from app.schemas.discipline_rule import (
    DisciplineRuleCreate,
    DisciplineRuleUpdate,
    DisciplineRuleResponse,
    DisciplineRuleListResponse,
)
from app.api.deps import get_current_user
from app.utils.hospital_filter import (
    apply_hospital_filter,
    get_current_hospital_id_or_raise,
    validate_hospital_access,
)

router = APIRouter()


@router.get("", response_model=DisciplineRuleListResponse)
def get_discipline_rules(
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=1000, description="每页数量"),
    version_id: Optional[int] = Query(None, description="模型版本ID"),
    department_code: Optional[str] = Query(None, description="科室代码"),
    dimension_code: Optional[str] = Query(None, description="维度代码"),
    keyword: Optional[str] = Query(None, description="关键词搜索"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取学科规则列表"""
    query = db.query(DisciplineRule)
    query = apply_hospital_filter(query, DisciplineRule, required=True)
    
    # 筛选条件
    if version_id:
        query = query.filter(DisciplineRule.version_id == version_id)
    if department_code:
        query = query.filter(DisciplineRule.department_code == department_code)
    if dimension_code:
        query = query.filter(DisciplineRule.dimension_code == dimension_code)
    if keyword:
        keyword_filter = f"%{keyword}%"
        query = query.filter(
            (DisciplineRule.department_name.ilike(keyword_filter)) |
            (DisciplineRule.dimension_name.ilike(keyword_filter)) |
            (DisciplineRule.rule_description.ilike(keyword_filter))
        )
    
    # 统计总数
    total = query.count()
    
    # 分页
    query = query.order_by(DisciplineRule.id.desc())
    items = query.offset((page - 1) * size).limit(size).all()
    
    # 预加载版本名称
    version_ids = list(set(item.version_id for item in items))
    versions = {v.id: v.name for v in db.query(ModelVersion).filter(ModelVersion.id.in_(version_ids)).all()}
    
    result_items = []
    for item in items:
        item_dict = {
            "id": item.id,
            "department_code": item.department_code,
            "department_name": item.department_name,
            "version_id": item.version_id,
            "version_name": versions.get(item.version_id, ""),
            "dimension_code": item.dimension_code,
            "dimension_name": item.dimension_name,
            "rule_description": item.rule_description,
            "rule_coefficient": item.rule_coefficient,
            "created_at": item.created_at,
            "updated_at": item.updated_at,
        }
        result_items.append(item_dict)
    
    return {"items": result_items, "total": total}


@router.post("", response_model=DisciplineRuleResponse, status_code=status.HTTP_201_CREATED)
def create_discipline_rule(
    rule_in: DisciplineRuleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """创建学科规则"""
    hospital_id = get_current_hospital_id_or_raise()
    
    # 验证模型版本存在
    version = db.query(ModelVersion).filter(ModelVersion.id == rule_in.version_id).first()
    if not version:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="模型版本不存在"
        )
    validate_hospital_access(db, version, hospital_id)
    
    # 检查是否已存在相同的规则
    existing = db.query(DisciplineRule).filter(
        DisciplineRule.hospital_id == hospital_id,
        DisciplineRule.version_id == rule_in.version_id,
        DisciplineRule.department_code == rule_in.department_code,
        DisciplineRule.dimension_code == rule_in.dimension_code,
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该科室和维度的学科规则已存在"
        )
    
    # 创建规则
    db_rule = DisciplineRule(
        hospital_id=hospital_id,
        version_id=rule_in.version_id,
        department_code=rule_in.department_code,
        department_name=rule_in.department_name,
        dimension_code=rule_in.dimension_code,
        dimension_name=rule_in.dimension_name,
        rule_description=rule_in.rule_description,
        rule_coefficient=rule_in.rule_coefficient,
    )
    db.add(db_rule)
    db.commit()
    db.refresh(db_rule)
    
    return {
        **db_rule.__dict__,
        "version_name": version.name,
    }


@router.get("/{rule_id}", response_model=DisciplineRuleResponse)
def get_discipline_rule(
    rule_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取学科规则详情"""
    query = db.query(DisciplineRule).filter(DisciplineRule.id == rule_id)
    query = apply_hospital_filter(query, DisciplineRule, required=True)
    rule = query.first()
    
    if not rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="学科规则不存在"
        )
    
    version = db.query(ModelVersion).filter(ModelVersion.id == rule.version_id).first()
    
    return {
        **rule.__dict__,
        "version_name": version.name if version else "",
    }


@router.put("/{rule_id}", response_model=DisciplineRuleResponse)
def update_discipline_rule(
    rule_id: int,
    rule_in: DisciplineRuleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """更新学科规则"""
    query = db.query(DisciplineRule).filter(DisciplineRule.id == rule_id)
    query = apply_hospital_filter(query, DisciplineRule, required=True)
    rule = query.first()
    
    if not rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="学科规则不存在"
        )
    
    validate_hospital_access(db, rule)
    
    # 更新字段
    update_data = rule_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(rule, field, value)
    
    db.commit()
    db.refresh(rule)
    
    version = db.query(ModelVersion).filter(ModelVersion.id == rule.version_id).first()
    
    return {
        **rule.__dict__,
        "version_name": version.name if version else "",
    }


@router.delete("/{rule_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_discipline_rule(
    rule_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """删除学科规则"""
    query = db.query(DisciplineRule).filter(DisciplineRule.id == rule_id)
    query = apply_hospital_filter(query, DisciplineRule, required=True)
    rule = query.first()
    
    if not rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="学科规则不存在"
        )
    
    validate_hospital_access(db, rule)
    
    db.delete(rule)
    db.commit()
