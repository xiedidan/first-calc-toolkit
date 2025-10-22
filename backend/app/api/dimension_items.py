"""
维度目录管理API
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.api import deps
from app.models.dimension_item_mapping import DimensionItemMapping
from app.models.charge_item import ChargeItem
from app.schemas.dimension_item import (
    DimensionItemMapping as DimensionItemMappingSchema,
    DimensionItemMappingCreate,
    DimensionItemList,
    ChargeItem as ChargeItemSchema,
)

router = APIRouter()


@router.get("", response_model=DimensionItemList)
def get_dimension_items(
    dimension_id: int = Query(..., description="维度节点ID"),
    keyword: Optional[str] = Query(None, description="搜索关键词"),
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(10, ge=1, le=100, description="每页数量"),
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_current_user),
):
    """获取维度的收费项目目录"""
    query = db.query(
        DimensionItemMapping.id,
        DimensionItemMapping.dimension_id,
        DimensionItemMapping.item_code,
        DimensionItemMapping.created_at,
        ChargeItem.item_name,
        ChargeItem.item_category
    ).join(
        ChargeItem,
        DimensionItemMapping.item_code == ChargeItem.item_code
    ).filter(
        DimensionItemMapping.dimension_id == dimension_id
    )
    
    # 关键词搜索
    if keyword:
        query = query.filter(
            or_(
                ChargeItem.item_code.contains(keyword),
                ChargeItem.item_name.contains(keyword),
                ChargeItem.item_category.contains(keyword),
            )
        )
    
    # 总数
    total = query.count()
    
    # 分页
    results = query.offset((page - 1) * size).limit(size).all()
    
    # 转换为Schema
    items = [
        DimensionItemMappingSchema(
            id=r.id,
            dimension_id=r.dimension_id,
            item_code=r.item_code,
            item_name=r.item_name,
            item_category=r.item_category,
            created_at=r.created_at
        )
        for r in results
    ]
    
    return DimensionItemList(total=total, items=items)


@router.post("", response_model=dict)
def create_dimension_items(
    mapping_in: DimensionItemMappingCreate,
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_current_user),
):
    """为维度添加收费项目"""
    added_count = 0
    skipped_count = 0
    
    for item_code in mapping_in.item_codes:
        # 检查收费项目是否存在
        charge_item = db.query(ChargeItem).filter(
            ChargeItem.item_code == item_code
        ).first()
        if not charge_item:
            skipped_count += 1
            continue
        
        # 检查是否已经关联
        existing = db.query(DimensionItemMapping).filter(
            DimensionItemMapping.dimension_id == mapping_in.dimension_id,
            DimensionItemMapping.item_code == item_code
        ).first()
        if existing:
            skipped_count += 1
            continue
        
        # 创建映射
        mapping = DimensionItemMapping(
            dimension_id=mapping_in.dimension_id,
            item_code=item_code
        )
        db.add(mapping)
        added_count += 1
    
    db.commit()
    
    return {
        "message": f"成功添加 {added_count} 个项目，跳过 {skipped_count} 个项目",
        "added_count": added_count,
        "skipped_count": skipped_count
    }


@router.delete("/{mapping_id}")
def delete_dimension_item(
    mapping_id: int,
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_current_user),
):
    """删除维度关联的收费项目"""
    mapping = db.query(DimensionItemMapping).filter(
        DimensionItemMapping.id == mapping_id
    ).first()
    if not mapping:
        raise HTTPException(status_code=404, detail="映射关系不存在")
    
    db.delete(mapping)
    db.commit()
    
    return {"message": "删除成功"}


@router.get("/charge-items/search", response_model=list[ChargeItemSchema])
def search_charge_items(
    keyword: str = Query(..., description="搜索关键词"),
    dimension_id: Optional[int] = Query(None, description="排除已关联的维度ID"),
    limit: int = Query(20, ge=1, le=100, description="返回数量"),
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_current_user),
):
    """搜索收费项目（用于添加时搜索）"""
    query = db.query(ChargeItem).filter(
        or_(
            ChargeItem.item_code.contains(keyword),
            ChargeItem.item_name.contains(keyword),
            ChargeItem.item_category.contains(keyword),
        )
    )
    
    # 如果指定了维度ID，排除已关联的项目
    if dimension_id:
        linked_codes = db.query(DimensionItemMapping.item_code).filter(
            DimensionItemMapping.dimension_id == dimension_id
        ).all()
        linked_codes = [code[0] for code in linked_codes]
        if linked_codes:
            query = query.filter(~ChargeItem.item_code.in_(linked_codes))
    
    items = query.limit(limit).all()
    return items
