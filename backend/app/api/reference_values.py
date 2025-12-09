"""
参考价值管理API
"""
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.api import deps
from app.models.reference_value import ReferenceValue
from app.utils.hospital_filter import get_current_hospital_id_or_raise
from app.schemas.reference_value import (
    ReferenceValue as ReferenceValueSchema,
    ReferenceValueCreate,
    ReferenceValueUpdate,
    ReferenceValueList,
    RefValueImportParseResponse,
    RefValueImportFieldMapping,
    RefValueImportExtractResponse,
    RefValueImportPreviewRequest,
    RefValueImportPreviewResponse,
    RefValueImportExecuteRequest,
    RefValueImportExecuteResponse,
)
from app.services.reference_value_import_service import ReferenceValueImportService

router = APIRouter()


@router.get("", response_model=ReferenceValueList)
def get_reference_values(
    period: Optional[str] = Query(None, description="年月筛选"),
    department_code: Optional[str] = Query(None, description="科室代码筛选"),
    keyword: Optional[str] = Query(None, description="搜索关键词"),
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(10, ge=1, le=1000, description="每页数量"),
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_current_user),
):
    """获取参考价值列表"""
    hospital_id = get_current_hospital_id_or_raise()
    
    query = db.query(ReferenceValue).filter(
        ReferenceValue.hospital_id == hospital_id
    )
    
    if period:
        query = query.filter(ReferenceValue.period == period)
    
    if department_code:
        query = query.filter(ReferenceValue.department_code == department_code)
    
    if keyword:
        query = query.filter(
            or_(
                ReferenceValue.department_code.contains(keyword),
                ReferenceValue.department_name.contains(keyword),
            )
        )
    
    total = query.count()
    
    items = query.order_by(
        ReferenceValue.period.desc(),
        ReferenceValue.department_code
    ).offset((page - 1) * size).limit(size).all()
    
    return ReferenceValueList(total=total, items=items)


@router.get("/by-period/{period}")
def get_reference_values_by_period(
    period: str,
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_current_user),
):
    """获取指定月份的所有参考价值（用于报表对比）"""
    hospital_id = get_current_hospital_id_or_raise()
    
    items = db.query(ReferenceValue).filter(
        ReferenceValue.hospital_id == hospital_id,
        ReferenceValue.period == period
    ).all()
    
    # 转换为字典，以科室代码为key
    result = {}
    for item in items:
        result[item.department_code] = {
            "reference_value": float(item.reference_value) if item.reference_value else 0,
            "doctor_reference_value": float(item.doctor_reference_value) if item.doctor_reference_value else None,
            "nurse_reference_value": float(item.nurse_reference_value) if item.nurse_reference_value else None,
            "tech_reference_value": float(item.tech_reference_value) if item.tech_reference_value else None,
        }
    
    return result


@router.get("/periods")
def get_available_periods(
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_current_user),
):
    """获取已有参考价值的月份列表"""
    hospital_id = get_current_hospital_id_or_raise()
    
    periods = db.query(ReferenceValue.period).filter(
        ReferenceValue.hospital_id == hospital_id
    ).distinct().order_by(ReferenceValue.period.desc()).all()
    
    return [p[0] for p in periods]


@router.get("/{ref_id}", response_model=ReferenceValueSchema)
def get_reference_value(
    ref_id: int,
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_current_user),
):
    """获取单个参考价值"""
    hospital_id = get_current_hospital_id_or_raise()
    
    ref = db.query(ReferenceValue).filter(
        ReferenceValue.id == ref_id,
        ReferenceValue.hospital_id == hospital_id
    ).first()
    
    if not ref:
        raise HTTPException(status_code=404, detail="参考价值不存在")
    
    return ref


@router.post("", response_model=ReferenceValueSchema)
def create_reference_value(
    ref_in: ReferenceValueCreate,
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_current_user),
):
    """创建参考价值"""
    hospital_id = get_current_hospital_id_or_raise()
    
    # 检查是否已存在
    existing = db.query(ReferenceValue).filter(
        ReferenceValue.hospital_id == hospital_id,
        ReferenceValue.period == ref_in.period,
        ReferenceValue.department_code == ref_in.department_code
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="该科室在该月份的参考价值已存在")
    
    ref = ReferenceValue(
        hospital_id=hospital_id,
        **ref_in.model_dump()
    )
    db.add(ref)
    db.commit()
    db.refresh(ref)
    
    return ref


@router.put("/{ref_id}", response_model=ReferenceValueSchema)
def update_reference_value(
    ref_id: int,
    ref_in: ReferenceValueUpdate,
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_current_user),
):
    """更新参考价值"""
    hospital_id = get_current_hospital_id_or_raise()
    
    ref = db.query(ReferenceValue).filter(
        ReferenceValue.id == ref_id,
        ReferenceValue.hospital_id == hospital_id
    ).first()
    
    if not ref:
        raise HTTPException(status_code=404, detail="参考价值不存在")
    
    update_data = ref_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(ref, field, value)
    
    db.commit()
    db.refresh(ref)
    
    return ref


@router.delete("/{ref_id}")
def delete_reference_value(
    ref_id: int,
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_current_user),
):
    """删除参考价值"""
    hospital_id = get_current_hospital_id_or_raise()
    
    ref = db.query(ReferenceValue).filter(
        ReferenceValue.id == ref_id,
        ReferenceValue.hospital_id == hospital_id
    ).first()
    
    if not ref:
        raise HTTPException(status_code=404, detail="参考价值不存在")
    
    db.delete(ref)
    db.commit()
    
    return {"message": "删除成功"}


@router.delete("/period/{period}/clear-all")
def clear_period_reference_values(
    period: str,
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_current_user),
):
    """清空指定月份的所有参考价值"""
    hospital_id = get_current_hospital_id_or_raise()
    
    deleted_count = db.query(ReferenceValue).filter(
        ReferenceValue.hospital_id == hospital_id,
        ReferenceValue.period == period
    ).delete()
    
    db.commit()
    
    return {
        "message": f"已清空 {period} 的所有参考价值",
        "deleted_count": deleted_count
    }


@router.delete("/clear-all")
def clear_all_reference_values(
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_current_user),
):
    """清空当前医院的所有参考价值"""
    hospital_id = get_current_hospital_id_or_raise()
    
    deleted_count = db.query(ReferenceValue).filter(
        ReferenceValue.hospital_id == hospital_id
    ).delete()
    
    db.commit()
    
    return {
        "message": "已清空所有参考价值",
        "deleted_count": deleted_count
    }


# 智能导入相关接口

@router.post("/import/parse", response_model=RefValueImportParseResponse)
async def import_parse(
    file: UploadFile = File(..., description="Excel文件"),
    sheet_name: Optional[str] = Query(None, description="工作表名称"),
    skip_rows: int = Query(0, ge=0, description="跳过前N行"),
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_current_user),
):
    """第一步：解析Excel文件，返回列名和预览数据"""
    file_content = await file.read()
    
    try:
        result = ReferenceValueImportService.parse_excel(file_content, sheet_name, skip_rows)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"解析文件失败: {str(e)}")


@router.post("/import/extract-values", response_model=RefValueImportExtractResponse)
def import_extract_values(
    request: RefValueImportFieldMapping,
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_current_user),
):
    """第二步：提取科室名称的唯一值，并提供智能匹配建议（仅在按名称匹配时使用）"""
    hospital_id = get_current_hospital_id_or_raise()
    
    try:
        result = ReferenceValueImportService.extract_unique_values(
            session_id=request.session_id,
            field_mapping=request.field_mapping,
            db=db,
            hospital_id=hospital_id,
            match_by=request.match_by
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"提取唯一值失败: {str(e)}")


@router.post("/import/preview", response_model=RefValueImportPreviewResponse)
def import_preview(
    request: RefValueImportPreviewRequest,
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_current_user),
):
    """第三步：生成导入预览"""
    hospital_id = get_current_hospital_id_or_raise()
    
    try:
        result = ReferenceValueImportService.generate_preview(
            session_id=request.session_id,
            value_mapping=request.value_mapping,
            db=db,
            hospital_id=hospital_id
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"生成预览失败: {str(e)}")


@router.post("/import/execute", response_model=RefValueImportExecuteResponse)
def import_execute(
    request: RefValueImportExecuteRequest,
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_current_user),
):
    """执行导入"""
    hospital_id = get_current_hospital_id_or_raise()
    
    try:
        result = ReferenceValueImportService.execute_import(
            session_id=request.session_id,
            confirmed_items=request.confirmed_items,
            db=db,
            hospital_id=hospital_id
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"执行导入失败: {str(e)}")
