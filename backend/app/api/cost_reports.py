"""
成本报表管理API
"""
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.api import deps
from app.models.cost_report import CostReport
from app.utils.hospital_filter import get_current_hospital_id_or_raise
from app.schemas.cost_report import (
    CostReport as CostReportSchema,
    CostReportCreate,
    CostReportUpdate,
    CostReportList,
    CostReportImportParseResponse,
    CostReportImportFieldMapping,
    CostReportImportExtractResponse,
    CostReportImportPreviewRequest,
    CostReportImportPreviewResponse,
    CostReportImportExecuteRequest,
    CostReportImportExecuteResponse,
)
from app.services.cost_report_import_service import CostReportImportService

router = APIRouter()


@router.get("", response_model=CostReportList)
def get_cost_reports(
    period: Optional[str] = Query(None, description="年月筛选"),
    department_code: Optional[str] = Query(None, description="科室代码筛选"),
    keyword: Optional[str] = Query(None, description="搜索关键词"),
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=1000, description="每页数量"),
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_current_user),
):
    """获取成本报表列表"""
    hospital_id = get_current_hospital_id_or_raise()
    
    query = db.query(CostReport).filter(
        CostReport.hospital_id == hospital_id
    )
    
    if period:
        query = query.filter(CostReport.period == period)
    
    if department_code:
        query = query.filter(CostReport.department_code == department_code)
    
    if keyword:
        query = query.filter(
            or_(
                CostReport.department_code.contains(keyword),
                CostReport.department_name.contains(keyword),
            )
        )
    
    total = query.count()
    
    items = query.order_by(
        CostReport.period.desc(),
        CostReport.department_code
    ).offset((page - 1) * size).limit(size).all()
    
    return CostReportList(total=total, items=items)


@router.get("/periods")
def get_available_periods(
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_current_user),
):
    """获取已有成本报表的月份列表"""
    hospital_id = get_current_hospital_id_or_raise()
    
    periods = db.query(CostReport.period).filter(
        CostReport.hospital_id == hospital_id
    ).distinct().order_by(CostReport.period.desc()).all()
    
    return [p[0] for p in periods]


@router.delete("/clear-filtered/batch")
def clear_filtered_cost_reports(
    period: Optional[str] = Query(None, description="年月筛选"),
    department_code: Optional[str] = Query(None, description="科室代码筛选"),
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_current_user),
):
    """清空筛选出来的成本报表记录"""
    hospital_id = get_current_hospital_id_or_raise()
    
    query = db.query(CostReport).filter(
        CostReport.hospital_id == hospital_id
    )
    
    if period:
        query = query.filter(CostReport.period == period)
    
    if department_code:
        query = query.filter(CostReport.department_code == department_code)
    
    deleted_count = query.delete()
    db.commit()
    
    return {
        "message": "清空成功",
        "deleted_count": deleted_count
    }


@router.delete("/clear-all")
def clear_all_cost_reports(
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_current_user),
):
    """清空当前医院的所有成本报表"""
    hospital_id = get_current_hospital_id_or_raise()
    
    deleted_count = db.query(CostReport).filter(
        CostReport.hospital_id == hospital_id
    ).delete()
    
    db.commit()
    
    return {
        "message": "已清空所有成本报表",
        "deleted_count": deleted_count
    }


@router.get("/{report_id}", response_model=CostReportSchema)
def get_cost_report(
    report_id: int,
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_current_user),
):
    """获取单个成本报表"""
    hospital_id = get_current_hospital_id_or_raise()
    
    report = db.query(CostReport).filter(
        CostReport.id == report_id,
        CostReport.hospital_id == hospital_id
    ).first()
    
    if not report:
        raise HTTPException(status_code=404, detail="成本报表不存在")
    
    return report


@router.post("", response_model=CostReportSchema)
def create_cost_report(
    report_in: CostReportCreate,
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_current_user),
):
    """创建成本报表"""
    hospital_id = get_current_hospital_id_or_raise()
    
    # 检查是否已存在
    existing = db.query(CostReport).filter(
        CostReport.hospital_id == hospital_id,
        CostReport.period == report_in.period,
        CostReport.department_code == report_in.department_code
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="该科室在该月份的成本报表已存在")
    
    report = CostReport(
        hospital_id=hospital_id,
        **report_in.model_dump()
    )
    db.add(report)
    db.commit()
    db.refresh(report)
    
    return report


@router.put("/{report_id}", response_model=CostReportSchema)
def update_cost_report(
    report_id: int,
    report_in: CostReportUpdate,
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_current_user),
):
    """更新成本报表"""
    hospital_id = get_current_hospital_id_or_raise()
    
    report = db.query(CostReport).filter(
        CostReport.id == report_id,
        CostReport.hospital_id == hospital_id
    ).first()
    
    if not report:
        raise HTTPException(status_code=404, detail="成本报表不存在")
    
    update_data = report_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(report, field, value)
    
    db.commit()
    db.refresh(report)
    
    return report


@router.delete("/{report_id}")
def delete_cost_report(
    report_id: int,
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_current_user),
):
    """删除成本报表"""
    hospital_id = get_current_hospital_id_or_raise()
    
    report = db.query(CostReport).filter(
        CostReport.id == report_id,
        CostReport.hospital_id == hospital_id
    ).first()
    
    if not report:
        raise HTTPException(status_code=404, detail="成本报表不存在")
    
    db.delete(report)
    db.commit()
    
    return {"message": "删除成功"}


# 智能导入相关接口

@router.post("/import/parse", response_model=CostReportImportParseResponse)
async def import_parse(
    file: UploadFile = File(..., description="Excel文件"),
    sheet_name: Optional[str] = Query(None, description="工作表名称"),
    skip_rows: int = Query(0, ge=0, description="跳过前N行"),
    header_row: Optional[int] = Query(None, ge=1, description="标题行位置（默认为跳过行数+1）"),
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_current_user),
):
    """第一步：解析Excel文件，返回列名和预览数据"""
    file_content = await file.read()
    
    # 如果未指定标题行，默认为跳过行数+1
    actual_header_row = header_row if header_row is not None else (skip_rows + 1)
    
    try:
        result = CostReportImportService.parse_excel(file_content, sheet_name, skip_rows, actual_header_row)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"解析文件失败: {str(e)}")


@router.post("/import/extract-values", response_model=CostReportImportExtractResponse)
def import_extract_values(
    request: CostReportImportFieldMapping,
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_current_user),
):
    """第二步：提取科室名称的唯一值，并提供智能匹配建议（仅在按名称匹配时使用）"""
    hospital_id = get_current_hospital_id_or_raise()
    
    try:
        result = CostReportImportService.extract_unique_values(
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


@router.post("/import/preview", response_model=CostReportImportPreviewResponse)
def import_preview(
    request: CostReportImportPreviewRequest,
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_current_user),
):
    """第三步：生成导入预览"""
    hospital_id = get_current_hospital_id_or_raise()
    
    try:
        result = CostReportImportService.generate_preview(
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


@router.post("/import/execute", response_model=CostReportImportExecuteResponse)
def import_execute(
    request: CostReportImportExecuteRequest,
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_current_user),
):
    """执行导入"""
    hospital_id = get_current_hospital_id_or_raise()
    
    try:
        result = CostReportImportService.execute_import(
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
