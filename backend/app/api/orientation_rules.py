"""
导向规则管理API
"""
from typing import Optional
from urllib.parse import quote
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import or_, desc, asc

from app.api import deps
from app.models.orientation_rule import OrientationRule
from app.schemas.orientation_rule import (
    OrientationRule as OrientationRuleSchema,
    OrientationRuleCreate,
    OrientationRuleUpdate,
    OrientationRuleList,
)
from app.utils.hospital_filter import (
    apply_hospital_filter,
    get_current_hospital_id_or_raise,
    validate_hospital_access,
    set_hospital_id_for_create,
)
from app.services.orientation_rule_service import OrientationRuleService

router = APIRouter()


@router.get("", response_model=OrientationRuleList)
def get_orientation_rules(
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_current_user),
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(10, ge=1, le=1000, description="每页数量"),
    keyword: Optional[str] = Query(None, description="搜索关键词（名称）"),
    category: Optional[str] = Query(None, description="导向类别筛选"),
):
    """获取导向规则列表"""
    query = db.query(OrientationRule)
    
    # 应用医疗机构过滤
    query = apply_hospital_filter(query, OrientationRule, required=True)
    
    # 关键词搜索（按名称）
    if keyword:
        query = query.filter(
            or_(
                OrientationRule.name.contains(keyword),
                OrientationRule.description.contains(keyword),
            )
        )
    
    # 类别筛选
    if category:
        query = query.filter(OrientationRule.category == category)
    
    # 按创建时间倒序排序
    query = query.order_by(desc(OrientationRule.created_at))
    
    # 总数
    total = query.count()
    
    # 分页
    items = query.offset((page - 1) * size).limit(size).all()
    
    return OrientationRuleList(total=total, items=items)


@router.post("", response_model=OrientationRuleSchema)
def create_orientation_rule(
    rule_in: OrientationRuleCreate,
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_current_user),
):
    """创建导向规则"""
    # 获取当前医疗机构ID
    hospital_id = get_current_hospital_id_or_raise()
    
    # 检查导向名称是否已存在（同一医疗机构内）
    query = db.query(OrientationRule).filter(OrientationRule.name == rule_in.name)
    query = apply_hospital_filter(query, OrientationRule, required=True)
    existing = query.first()
    if existing:
        raise HTTPException(status_code=400, detail="导向名称已存在")
    
    # 自动设置hospital_id
    rule_data = rule_in.model_dump()
    rule_data = set_hospital_id_for_create(rule_data, hospital_id)
    
    # 创建导向规则
    rule = OrientationRule(**rule_data)
    db.add(rule)
    db.commit()
    db.refresh(rule)
    
    return rule


@router.post("/{rule_id}/copy", response_model=OrientationRuleSchema)
def copy_orientation_rule(
    rule_id: int,
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_current_user),
):
    """复制导向规则及其关联数据"""
    # 获取当前医疗机构ID
    hospital_id = get_current_hospital_id_or_raise()
    
    # 调用服务层方法复制规则
    new_rule = OrientationRuleService.copy_rule(db, rule_id, hospital_id)
    
    return new_rule


@router.get("/{rule_id}", response_model=OrientationRuleSchema)
def get_orientation_rule(
    rule_id: int,
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_current_user),
):
    """获取导向规则详情"""
    query = db.query(OrientationRule).filter(OrientationRule.id == rule_id)
    query = apply_hospital_filter(query, OrientationRule, required=True)
    rule = query.first()
    if not rule:
        raise HTTPException(status_code=404, detail="导向规则不存在")
    
    return rule


@router.put("/{rule_id}", response_model=OrientationRuleSchema)
def update_orientation_rule(
    rule_id: int,
    rule_in: OrientationRuleUpdate,
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_current_user),
):
    """更新导向规则"""
    query = db.query(OrientationRule).filter(OrientationRule.id == rule_id)
    query = apply_hospital_filter(query, OrientationRule, required=True)
    rule = query.first()
    if not rule:
        raise HTTPException(status_code=404, detail="导向规则不存在")
    
    # 验证数据所属医疗机构
    validate_hospital_access(db, rule)
    
    # 如果更新名称，检查是否与其他规则重复
    if rule_in.name and rule_in.name != rule.name:
        query = db.query(OrientationRule).filter(
            OrientationRule.name == rule_in.name,
            OrientationRule.id != rule_id
        )
        query = apply_hospital_filter(query, OrientationRule, required=True)
        existing = query.first()
        if existing:
            raise HTTPException(status_code=400, detail="导向名称已存在")
    
    # 更新字段
    update_data = rule_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(rule, field, value)
    
    db.commit()
    db.refresh(rule)
    
    return rule


@router.get("/{rule_id}/export")
def export_orientation_rule(
    rule_id: int,
    format: str = Query("markdown", description="导出格式: markdown 或 pdf"),
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_current_user),
):
    """导出导向规则为Markdown或PDF文件"""
    # 获取当前医疗机构ID
    hospital_id = get_current_hospital_id_or_raise()
    
    # 根据格式调用不同的导出方法
    if format.lower() == "pdf":
        buffer, filename = OrientationRuleService.export_rule_pdf(db, rule_id, hospital_id)
        media_type = "application/pdf"
    else:
        buffer, filename = OrientationRuleService.export_rule(db, rule_id, hospital_id)
        media_type = "text/markdown"
    
    # 返回StreamingResponse供下载
    # 使用URL编码处理中文文件名
    encoded_filename = quote(filename)
    
    return StreamingResponse(
        buffer,
        media_type=media_type,
        headers={
            "Content-Disposition": f"attachment; filename*=UTF-8''{encoded_filename}"
        }
    )


@router.delete("/{rule_id}")
def delete_orientation_rule(
    rule_id: int,
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_current_user),
):
    """删除导向规则"""
    query = db.query(OrientationRule).filter(OrientationRule.id == rule_id)
    query = apply_hospital_filter(query, OrientationRule, required=True)
    rule = query.first()
    if not rule:
        raise HTTPException(status_code=404, detail="导向规则不存在")
    
    # 验证数据所属医疗机构
    validate_hospital_access(db, rule)
    
    # 检查是否有模型节点关联该规则
    if rule.model_nodes:
        raise HTTPException(
            status_code=400,
            detail=f"无法删除：有 {len(rule.model_nodes)} 个模型节点关联此导向规则"
        )
    
    # 删除导向规则（级联删除关联的基准和阶梯）
    db.delete(rule)
    db.commit()
    
    return {"message": "导向规则删除成功"}
