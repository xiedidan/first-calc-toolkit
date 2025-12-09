"""
分类预案管理API
"""
import logging
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.middleware.hospital_context import require_hospital_id
from app.services.classification_plan_service import ClassificationPlanService
from app.schemas.classification_plan import (
    ClassificationPlanResponse,
    ClassificationPlanListResponse,
    PlanItemResponse,
    PlanItemListResponse,
    PlanItemQueryParams,
    PlanItemUpdate,
    UpdatePlanRequest,
    SubmitPreviewResponse,
    SubmitPlanRequest,
    SubmitPlanResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("", response_model=ClassificationPlanListResponse)
def get_classification_plans(
    skip: int = Query(0, ge=0, description="跳过记录数"),
    limit: int = Query(20, ge=1, le=100, description="返回记录数"),
    status: Optional[str] = Query(None, description="预案状态筛选"),
    db: Session = Depends(get_db)
):
    """
    获取分类预案列表
    
    - **skip**: 跳过记录数（分页）
    - **limit**: 返回记录数（分页）
    - **status**: 预案状态筛选（draft/submitted）
    """
    hospital_id = require_hospital_id()
    
    logger.info(
        f"[API] 获取分类预案列表: hospital_id={hospital_id}, "
        f"skip={skip}, limit={limit}, status={status}"
    )
    
    try:
        return ClassificationPlanService.get_plans(
            db=db,
            hospital_id=hospital_id,
            skip=skip,
            limit=limit,
            status=status
        )
    except Exception as e:
        logger.error(f"[API] 获取分类预案列表失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"获取预案列表失败: {str(e)}")


@router.get("/{plan_id}", response_model=ClassificationPlanResponse)
def get_classification_plan_detail(
    plan_id: int,
    db: Session = Depends(get_db)
):
    """
    获取分类预案详情
    
    - **plan_id**: 预案ID
    """
    hospital_id = require_hospital_id()
    
    logger.info(f"[API] 获取分类预案详情: plan_id={plan_id}, hospital_id={hospital_id}")
    
    try:
        return ClassificationPlanService.get_plan_detail(
            db=db,
            hospital_id=hospital_id,
            plan_id=plan_id
        )
    except ValueError as e:
        logger.warning(f"[API] 预案不存在: {str(e)}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"[API] 获取预案详情失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"获取预案详情失败: {str(e)}")


@router.put("/{plan_id}", response_model=ClassificationPlanResponse)
def update_classification_plan(
    plan_id: int,
    update_data: UpdatePlanRequest,
    db: Session = Depends(get_db)
):
    """
    更新分类预案（名称、状态）
    
    - **plan_id**: 预案ID
    - **update_data**: 更新数据
    """
    hospital_id = require_hospital_id()
    
    logger.info(
        f"[API] 更新分类预案: plan_id={plan_id}, hospital_id={hospital_id}, "
        f"plan_name={update_data.plan_name}"
    )
    
    try:
        return ClassificationPlanService.update_plan(
            db=db,
            hospital_id=hospital_id,
            plan_id=plan_id,
            update_data=update_data
        )
    except ValueError as e:
        logger.warning(f"[API] 更新预案失败: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"[API] 更新预案失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"更新预案失败: {str(e)}")


@router.delete("/{plan_id}")
def delete_classification_plan(
    plan_id: int,
    db: Session = Depends(get_db)
):
    """
    删除分类预案
    
    - **plan_id**: 预案ID
    """
    hospital_id = require_hospital_id()
    
    logger.info(f"[API] 删除分类预案: plan_id={plan_id}, hospital_id={hospital_id}")
    
    try:
        return ClassificationPlanService.delete_plan(
            db=db,
            hospital_id=hospital_id,
            plan_id=plan_id
        )
    except ValueError as e:
        logger.warning(f"[API] 删除预案失败: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"[API] 删除预案失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"删除预案失败: {str(e)}")


@router.get("/{plan_id}/items", response_model=PlanItemListResponse)
def get_plan_items(
    plan_id: int,
    sort_by: Optional[str] = Query(None, description="排序字段：confidence_asc, confidence_desc"),
    min_confidence: Optional[float] = Query(None, ge=0.0, le=1.0, description="最小确信度"),
    max_confidence: Optional[float] = Query(None, ge=0.0, le=1.0, description="最大确信度"),
    is_adjusted: Optional[bool] = Query(None, description="是否已调整"),
    processing_status: Optional[str] = Query(None, description="处理状态"),
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(50, ge=1, le=1000, description="每页数量"),
    db: Session = Depends(get_db)
):
    """
    获取预案项目列表（支持排序和筛选）
    
    - **plan_id**: 预案ID
    - **sort_by**: 排序字段（confidence_asc/confidence_desc）
    - **min_confidence**: 最小确信度
    - **max_confidence**: 最大确信度
    - **is_adjusted**: 是否已调整
    - **processing_status**: 处理状态
    - **page**: 页码
    - **size**: 每页数量
    """
    hospital_id = require_hospital_id()
    
    logger.info(
        f"[API] 获取预案项目列表: plan_id={plan_id}, hospital_id={hospital_id}, "
        f"sort_by={sort_by}, page={page}, size={size}"
    )
    
    try:
        query_params = PlanItemQueryParams(
            sort_by=sort_by,
            min_confidence=min_confidence,
            max_confidence=max_confidence,
            is_adjusted=is_adjusted,
            processing_status=processing_status,
            page=page,
            size=size
        )
        
        return ClassificationPlanService.get_plan_items(
            db=db,
            hospital_id=hospital_id,
            plan_id=plan_id,
            query_params=query_params
        )
    except ValueError as e:
        logger.warning(f"[API] 获取预案项目失败: {str(e)}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"[API] 获取预案项目失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"获取预案项目失败: {str(e)}")


@router.put("/{plan_id}/items/{item_id}", response_model=PlanItemResponse)
def update_plan_item(
    plan_id: int,
    item_id: int,
    update_data: PlanItemUpdate,
    db: Session = Depends(get_db)
):
    """
    调整预案项目维度
    
    - **plan_id**: 预案ID
    - **item_id**: 项目ID
    - **update_data**: 更新数据（新的维度ID）
    """
    hospital_id = require_hospital_id()
    
    logger.info(
        f"[API] 调整预案项目维度: plan_id={plan_id}, item_id={item_id}, "
        f"hospital_id={hospital_id}, dimension_id={update_data.dimension_id}"
    )
    
    try:
        return ClassificationPlanService.update_plan_item(
            db=db,
            hospital_id=hospital_id,
            plan_id=plan_id,
            item_id=item_id,
            update_data=update_data
        )
    except ValueError as e:
        logger.warning(f"[API] 调整项目维度失败: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"[API] 调整项目维度失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"调整项目维度失败: {str(e)}")


@router.post("/{plan_id}/preview", response_model=SubmitPreviewResponse)
def generate_submit_preview(
    plan_id: int,
    db: Session = Depends(get_db)
):
    """
    生成提交预览（分析新增/覆盖）
    
    - **plan_id**: 预案ID
    """
    hospital_id = require_hospital_id()
    
    logger.info(f"[API] 生成提交预览: plan_id={plan_id}, hospital_id={hospital_id}")
    
    try:
        return ClassificationPlanService.generate_submit_preview(
            db=db,
            hospital_id=hospital_id,
            plan_id=plan_id
        )
    except ValueError as e:
        logger.warning(f"[API] 生成预览失败: {str(e)}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"[API] 生成预览失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"生成预览失败: {str(e)}")


@router.post("/{plan_id}/submit", response_model=SubmitPlanResponse)
def submit_classification_plan(
    plan_id: int,
    submit_data: SubmitPlanRequest,
    db: Session = Depends(get_db)
):
    """
    提交分类预案（批量提交到维度目录）
    
    - **plan_id**: 预案ID
    - **submit_data**: 提交请求数据
    """
    hospital_id = require_hospital_id()
    
    logger.info(f"[API] 提交分类预案: plan_id={plan_id}, hospital_id={hospital_id}")
    
    try:
        return ClassificationPlanService.submit_plan(
            db=db,
            hospital_id=hospital_id,
            plan_id=plan_id,
            submit_data=submit_data
        )
    except ValueError as e:
        logger.warning(f"[API] 提交预案失败: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"[API] 提交预案失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"提交预案失败: {str(e)}")
