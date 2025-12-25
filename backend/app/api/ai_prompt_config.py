"""
AI提示词配置API路由
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional

from app.api.deps import get_db, get_current_active_user
from app.models import User
from app.middleware.hospital_context import require_hospital_id
from app.schemas.ai_prompt_config import (
    AIPromptConfigCreate,
    AIPromptConfigUpdate,
    AIPromptConfigResponse,
    AIPromptConfigListResponse,
    AIPromptCategoriesResponse,
    AIPromptCategoryInfo,
    ReportAIGenerateRequest,
    ReportAIGenerateResponse,
    ReportAIPreviewGenerateRequest,
)
from app.services.ai_report_service import AIReportService
from app.models.role import RoleType

router = APIRouter()


def require_maintainer(current_user: User = Depends(get_current_active_user)) -> User:
    """
    要求维护者权限（AI接口管理仅维护者可用）
    """
    is_maintainer = any(
        role.role_type == RoleType.MAINTAINER 
        for role in current_user.roles
    )
    if not is_maintainer:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="需要维护者权限"
        )
    return current_user


@router.get("/categories", response_model=AIPromptCategoriesResponse)
def get_prompt_categories(
    current_user: User = Depends(require_maintainer),
):
    """
    获取所有提示词分类信息
    """
    categories = AIReportService.get_category_info()
    return AIPromptCategoriesResponse(
        categories=[AIPromptCategoryInfo(**cat) for cat in categories]
    )


@router.post("/generate/report", response_model=dict)
def generate_report_content(
    request: ReportAIGenerateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    使用AI生成报告内容
    
    - category: report_issues（当前存在问题）或 report_plans（未来发展计划）
    """
    hospital_id = require_hospital_id()
    
    result = AIReportService.generate_report_content(
        db=db,
        hospital_id=hospital_id,
        report_id=request.report_id,
        category=request.category,
    )
    
    return {
        "code": 200,
        "message": "生成完成" if result["success"] else "生成失败",
        "data": result,
    }


@router.post("/generate/preview", response_model=dict)
def generate_report_content_preview(
    request: ReportAIPreviewGenerateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    使用AI生成报告内容（预览模式，用于创建报告时）
    
    - department_id: 科室ID
    - period: 统计周期
    - task_id: 计算任务ID
    - category: report_issues（当前存在问题）或 report_plans（未来发展计划）
    """
    hospital_id = require_hospital_id()
    
    result = AIReportService.generate_report_content_preview(
        db=db,
        hospital_id=hospital_id,
        department_id=request.department_id,
        period=request.period,
        task_id=request.task_id,
        category=request.category,
    )
    
    return {
        "code": 200,
        "message": "生成完成" if result["success"] else "生成失败",
        "data": result,
    }


@router.get("", response_model=dict)
def get_all_prompt_configs(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_maintainer),
):
    """
    获取所有分类的提示词配置
    """
    hospital_id = require_hospital_id()
    configs = AIReportService.get_all_prompt_configs(db, hospital_id)
    
    return {
        "code": 200,
        "message": "success",
        "data": configs,
    }


@router.get("/{category}", response_model=dict)
def get_prompt_config(
    category: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_maintainer),
):
    """
    获取指定分类的提示词配置
    """
    hospital_id = require_hospital_id()
    config = AIReportService.get_prompt_config(db, hospital_id, category)
    
    return {
        "code": 200,
        "message": "success",
        "data": config,
    }


@router.post("/{category}", response_model=dict)
def save_prompt_config(
    category: str,
    config_data: AIPromptConfigUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_maintainer),
):
    """
    保存指定分类的提示词配置
    """
    hospital_id = require_hospital_id()
    
    if not config_data.user_prompt:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户提示词不能为空"
        )
    
    config = AIReportService.save_prompt_config(
        db=db,
        hospital_id=hospital_id,
        category=category,
        system_prompt=config_data.system_prompt,
        user_prompt=config_data.user_prompt,
    )
    
    return {
        "code": 200,
        "message": "保存成功",
        "data": config,
    }
