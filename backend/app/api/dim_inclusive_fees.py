"""内含式收费API"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.database import get_db
from app.models.dim_inclusive_fee import DimInclusiveFee
from app.schemas.dim_inclusive_fee import (
    DimInclusiveFeeCreate,
    DimInclusiveFeeUpdate,
    DimInclusiveFeeResponse,
    DimInclusiveFeeListResponse
)

router = APIRouter()


@router.get("", response_model=DimInclusiveFeeListResponse)
def get_inclusive_fees(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=1000),
    keyword: Optional[str] = Query(None, description="搜索关键词（项目代码或名称）"),
    db: Session = Depends(get_db)
):
    """获取内含式收费列表"""
    query = db.query(DimInclusiveFee)
    
    # 关键词搜索
    if keyword:
        query = query.filter(
            or_(
                DimInclusiveFee.item_code.ilike(f"%{keyword}%"),
                DimInclusiveFee.item_name.ilike(f"%{keyword}%")
            )
        )
    
    # 总数
    total = query.count()
    
    # 分页
    items = query.order_by(DimInclusiveFee.id.desc()).offset((page - 1) * size).limit(size).all()
    
    return DimInclusiveFeeListResponse(
        items=items,
        total=total,
        page=page,
        size=size
    )


@router.get("/{id}", response_model=DimInclusiveFeeResponse)
def get_inclusive_fee(id: int, db: Session = Depends(get_db)):
    """获取单个内含式收费"""
    item = db.query(DimInclusiveFee).filter(DimInclusiveFee.id == id).first()
    if not item:
        raise HTTPException(status_code=404, detail="内含式收费项目不存在")
    return item


@router.post("", response_model=DimInclusiveFeeResponse)
def create_inclusive_fee(
    data: DimInclusiveFeeCreate,
    db: Session = Depends(get_db)
):
    """创建内含式收费"""
    # 检查项目代码是否已存在
    existing = db.query(DimInclusiveFee).filter(
        DimInclusiveFee.item_code == data.item_code
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"项目代码 {data.item_code} 已存在")
    
    item = DimInclusiveFee(
        item_code=data.item_code,
        item_name=data.item_name,
        cost=data.cost
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.put("/{id}", response_model=DimInclusiveFeeResponse)
def update_inclusive_fee(
    id: int,
    data: DimInclusiveFeeUpdate,
    db: Session = Depends(get_db)
):
    """更新内含式收费"""
    item = db.query(DimInclusiveFee).filter(DimInclusiveFee.id == id).first()
    if not item:
        raise HTTPException(status_code=404, detail="内含式收费项目不存在")
    
    # 如果更新项目代码，检查是否与其他记录冲突
    if data.item_code and data.item_code != item.item_code:
        existing = db.query(DimInclusiveFee).filter(
            DimInclusiveFee.item_code == data.item_code,
            DimInclusiveFee.id != id
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail=f"项目代码 {data.item_code} 已存在")
    
    # 更新字段
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(item, key, value)
    
    db.commit()
    db.refresh(item)
    return item


@router.delete("/{id}")
def delete_inclusive_fee(id: int, db: Session = Depends(get_db)):
    """删除内含式收费"""
    item = db.query(DimInclusiveFee).filter(DimInclusiveFee.id == id).first()
    if not item:
        raise HTTPException(status_code=404, detail="内含式收费项目不存在")
    
    db.delete(item)
    db.commit()
    return {"message": "删除成功"}
