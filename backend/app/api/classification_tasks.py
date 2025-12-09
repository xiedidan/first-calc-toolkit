"""
分类任务API路由
"""
import logging
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import distinct

from app.api.deps import get_db, get_current_active_user
from app.models import User
from app.models.charge_item import ChargeItem
from app.models.classification_task import ClassificationTask
from app.middleware.hospital_context import require_hospital_id
from app.schemas.classification_task import (
    ClassificationTaskCreate,
    ClassificationTaskResponse,
    ClassificationTaskListResponse,
    TaskProgressResponse,
    TaskLogResponse,
    ContinueTaskResponse,
)
from app.services.classification_task_service import ClassificationTaskService

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/charge-categories", response_model=dict)
def get_charge_categories(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    获取收费类别列表
    
    从收费项目表中提取去重的收费类别
    """
    try:
        hospital_id = require_hospital_id()
        
        # 从 charge_items 表查询去重的 item_category
        categories = db.query(distinct(ChargeItem.item_category)).filter(
            ChargeItem.hospital_id == hospital_id,
            ChargeItem.item_category.isnot(None),
            ChargeItem.item_category != ''
        ).order_by(ChargeItem.item_category).all()
        
        # 提取类别名称列表
        category_list = [c[0] for c in categories if c[0]]
        
        return {
            "code": 200,
            "message": "success",
            "data": category_list
        }
    except Exception as e:
        logger.error(f"[分类任务API] 获取收费类别失败: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取收费类别失败: {str(e)}"
        )


@router.get("", response_model=dict)
def get_classification_tasks(
    skip: int = Query(0, ge=0, description="跳过记录数"),
    limit: int = Query(20, ge=1, le=100, description="返回记录数"),
    status: str = Query(None, description="任务状态筛选"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    获取分类任务列表
    
    支持分页和状态筛选
    """
    try:
        hospital_id = require_hospital_id()
        
        result = ClassificationTaskService.get_tasks(
            db=db,
            hospital_id=hospital_id,
            skip=skip,
            limit=limit,
            status=status
        )
        
        return {
            "code": 200,
            "message": "success",
            "data": result.model_dump()
        }
    except Exception as e:
        logger.error(f"[分类任务API] 查询任务列表失败: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"查询任务列表失败: {str(e)}"
        )


@router.post("", response_model=dict)
def create_classification_task(
    task_data: ClassificationTaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    创建分类任务
    
    创建任务后会自动启动异步处理
    """
    try:
        hospital_id = require_hospital_id()
        
        task = ClassificationTaskService.create_task(
            db=db,
            hospital_id=hospital_id,
            user_id=current_user.id,
            task_data=task_data
        )
        
        return {
            "code": 200,
            "message": "任务创建成功",
            "data": task.model_dump()
        }
    except ValueError as e:
        logger.warning(f"[分类任务API] 创建任务失败（参数错误）: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"[分类任务API] 创建任务失败: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建任务失败: {str(e)}"
        )


@router.put("/{task_id}", response_model=dict)
def update_classification_task(
    task_id: int,
    task_data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    更新分类任务（仅支持更新任务名称）
    """
    try:
        hospital_id = require_hospital_id()
        
        # 查询任务
        task = db.query(ClassificationTask).filter(
            ClassificationTask.id == task_id,
            ClassificationTask.hospital_id == hospital_id
        ).first()
        
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="任务不存在或不属于当前医疗机构"
            )
        
        # 更新任务名称
        if 'task_name' in task_data:
            task.task_name = task_data['task_name']
            db.commit()
            db.refresh(task)
        
        return {
            "code": 200,
            "message": "更新成功",
            "data": ClassificationTaskService._build_task_response(task).model_dump()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[分类任务API] 更新任务失败: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新任务失败: {str(e)}"
        )


@router.get("/{task_id}", response_model=dict)
def get_classification_task_detail(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    获取分类任务详情
    """
    try:
        hospital_id = require_hospital_id()
        
        task = ClassificationTaskService.get_task_detail(
            db=db,
            hospital_id=hospital_id,
            task_id=task_id
        )
        
        return {
            "code": 200,
            "message": "success",
            "data": task.model_dump()
        }
    except ValueError as e:
        logger.warning(f"[分类任务API] 查询任务详情失败（任务不存在）: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"[分类任务API] 查询任务详情失败: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"查询任务详情失败: {str(e)}"
        )


@router.delete("/{task_id}", response_model=dict)
def delete_classification_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    删除分类任务
    
    注意：正在处理中的任务无法删除
    """
    try:
        hospital_id = require_hospital_id()
        
        result = ClassificationTaskService.delete_task(
            db=db,
            hospital_id=hospital_id,
            task_id=task_id
        )
        
        return {
            "code": 200,
            "message": result["message"],
            "data": None
        }
    except ValueError as e:
        logger.warning(f"[分类任务API] 删除任务失败（参数错误）: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"[分类任务API] 删除任务失败: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"删除任务失败: {str(e)}"
        )


@router.post("/{task_id}/continue", response_model=dict)
def continue_classification_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    继续处理中断的任务
    
    支持断点续传，只处理未完成的项目
    """
    try:
        hospital_id = require_hospital_id()
        
        result = ClassificationTaskService.continue_task(
            db=db,
            hospital_id=hospital_id,
            task_id=task_id
        )
        
        if result.success:
            return {
                "code": 200,
                "message": result.message,
                "data": {
                    "celery_task_id": result.celery_task_id
                }
            }
        else:
            return {
                "code": 500,
                "message": result.message,
                "data": None
            }
    except ValueError as e:
        logger.warning(f"[分类任务API] 继续处理任务失败（参数错误）: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"[分类任务API] 继续处理任务失败: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"继续处理任务失败: {str(e)}"
        )


@router.get("/{task_id}/progress", response_model=dict)
def get_classification_task_progress(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    获取任务实时进度
    
    用于前端轮询显示进度
    """
    try:
        hospital_id = require_hospital_id()
        
        progress = ClassificationTaskService.get_task_progress(
            db=db,
            hospital_id=hospital_id,
            task_id=task_id
        )
        
        return {
            "code": 200,
            "message": "success",
            "data": progress.model_dump()
        }
    except ValueError as e:
        logger.warning(f"[分类任务API] 查询任务进度失败（任务不存在）: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"[分类任务API] 查询任务进度失败: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"查询任务进度失败: {str(e)}"
        )


@router.get("/{task_id}/logs", response_model=dict)
def get_classification_task_logs(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    获取任务处理日志
    
    包含任务执行信息和失败项目列表
    """
    try:
        hospital_id = require_hospital_id()
        
        logs = ClassificationTaskService.get_task_logs(
            db=db,
            hospital_id=hospital_id,
            task_id=task_id
        )
        
        return {
            "code": 200,
            "message": "success",
            "data": logs.model_dump()
        }
    except ValueError as e:
        logger.warning(f"[分类任务API] 查询任务日志失败（任务不存在）: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"[分类任务API] 查询任务日志失败: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"查询任务日志失败: {str(e)}"
        )
