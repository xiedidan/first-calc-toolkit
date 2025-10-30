"""
科室管理API
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, desc, asc, func

from app.api import deps
from app.models.department import Department
from app.schemas.department import (
    Department as DepartmentSchema,
    DepartmentCreate,
    DepartmentUpdate,
    DepartmentList,
)

router = APIRouter()


@router.get("", response_model=DepartmentList)
def get_departments(
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_current_user),
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(10, ge=1, le=10000, description="每页数量"),
    keyword: Optional[str] = Query(None, description="搜索关键词"),
    is_active: Optional[bool] = Query(None, description="是否激活"),
    sort_by: Optional[str] = Query("sort_order", description="排序字段"),
    sort_order: Optional[str] = Query("asc", description="排序方向"),
):
    """获取科室列表"""
    query = db.query(Department)
    
    # 关键词搜索
    if keyword:
        query = query.filter(
            or_(
                Department.his_code.contains(keyword),
                Department.his_name.contains(keyword),
                Department.cost_center_code.contains(keyword),
                Department.cost_center_name.contains(keyword),
            )
        )
    
    # 状态筛选
    if is_active is not None:
        query = query.filter(Department.is_active == is_active)
    
    # 排序
    sort_column = getattr(Department, sort_by, Department.sort_order)
    if sort_order == "desc":
        query = query.order_by(desc(sort_column))
    else:
        query = query.order_by(asc(sort_column))
    
    # 总数
    total = query.count()
    
    # 分页
    items = query.offset((page - 1) * size).limit(size).all()
    
    return DepartmentList(total=total, items=items)


@router.post("", response_model=DepartmentSchema)
def create_department(
    department_in: DepartmentCreate,
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_current_user),
):
    """创建科室"""
    # 检查HIS代码是否已存在
    existing = db.query(Department).filter(
        Department.his_code == department_in.his_code
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="HIS科室代码已存在")
    
    # 如果没有指定排序序号，自动设置为最大序号+1
    department_data = department_in.model_dump()
    if department_data.get("sort_order") is None:
        max_order = db.query(func.max(Department.sort_order)).scalar()
        department_data["sort_order"] = (max_order or 0) + 1
    
    # 创建科室
    department = Department(**department_data)
    db.add(department)
    db.commit()
    db.refresh(department)
    
    return department


@router.get("/{department_id}", response_model=DepartmentSchema)
def get_department(
    department_id: int,
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_current_user),
):
    """获取科室详情"""
    department = db.query(Department).filter(Department.id == department_id).first()
    if not department:
        raise HTTPException(status_code=404, detail="科室不存在")
    
    return department


@router.put("/{department_id}", response_model=DepartmentSchema)
def update_department(
    department_id: int,
    department_in: DepartmentUpdate,
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_current_user),
):
    """更新科室信息"""
    department = db.query(Department).filter(Department.id == department_id).first()
    if not department:
        raise HTTPException(status_code=404, detail="科室不存在")
    
    # 更新字段
    update_data = department_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(department, field, value)
    
    db.commit()
    db.refresh(department)
    
    return department


@router.delete("/{department_id}")
def delete_department(
    department_id: int,
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_current_user),
):
    """删除科室"""
    department = db.query(Department).filter(Department.id == department_id).first()
    if not department:
        raise HTTPException(status_code=404, detail="科室不存在")
    
    db.delete(department)
    db.commit()
    
    return {"message": "科室删除成功"}


@router.put("/{department_id}/toggle-evaluation")
def toggle_evaluation(
    department_id: int,
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_current_user),
):
    """切换科室评估状态"""
    department = db.query(Department).filter(Department.id == department_id).first()
    if not department:
        raise HTTPException(status_code=404, detail="科室不存在")
    
    department.is_active = not department.is_active
    db.commit()
    
    return {"is_active": department.is_active}
