"""
AI提示词模块配置API路由 - 智能问数系统
支持按功能模块配置独立的提示词，优化不同场景的AI响应质量
"""
import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional

from app.api.deps import get_db, get_current_active_user
from app.models import User, AIInterface, AIPromptModule
from app.models.ai_prompt_module import PromptModuleCode
from app.middleware.hospital_context import require_hospital_id
from app.schemas.ai_prompt_module import (
    AIPromptModuleUpdate,
    AIPromptModuleResponse,
    AIPromptModuleListResponse,
    AIInterfaceInfo,
)

logger = logging.getLogger(__name__)

router = APIRouter()


def require_maintainer(current_user: User = Depends(get_current_active_user)) -> User:
    """
    要求维护者权限（提示词模块管理仅维护者可用）
    """
    from app.models.role import RoleType
    
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


def _build_response(module: AIPromptModule, db: Session) -> AIPromptModuleResponse:
    """构建提示词模块响应对象"""
    # 获取关联的AI接口信息
    ai_interface_info = None
    if module.ai_interface_id:
        ai_interface = db.query(AIInterface).filter(
            AIInterface.id == module.ai_interface_id
        ).first()
        if ai_interface:
            ai_interface_info = AIInterfaceInfo(
                id=ai_interface.id,
                name=ai_interface.name,
                model_name=ai_interface.model_name,
                is_active=ai_interface.is_active,
            )
    
    return AIPromptModuleResponse(
        id=module.id,
        hospital_id=module.hospital_id,
        module_code=module.module_code,
        module_name=module.module_name,
        description=module.description,
        ai_interface_id=module.ai_interface_id,
        ai_interface=ai_interface_info,
        temperature=module.temperature,
        placeholders=module.placeholders or [],
        system_prompt=module.system_prompt,
        user_prompt=module.user_prompt,
        created_at=module.created_at,
        updated_at=module.updated_at,
        is_configured=module.ai_interface_id is not None,
    )


@router.get("", response_model=dict)
def list_prompt_modules(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_maintainer),
):
    """
    获取所有提示词模块配置
    
    需要维护者权限。返回当前医疗机构的所有提示词模块配置。
    如果模块不存在，会自动初始化默认配置。
    """
    hospital_id = require_hospital_id()
    
    # 确保模块已初始化
    from app.services.ai_prompt_module_service import AIPromptModuleService
    AIPromptModuleService.ensure_modules_initialized(db, hospital_id)
    
    # 查询所有模块
    modules = db.query(AIPromptModule).filter(
        AIPromptModule.hospital_id == hospital_id
    ).order_by(AIPromptModule.module_code).all()
    
    items = [_build_response(m, db) for m in modules]
    
    return {
        "code": 200,
        "message": "success",
        "data": {
            "items": [item.model_dump() for item in items],
            "total": len(items),
        },
    }


@router.get("/{module_code}", response_model=dict)
def get_prompt_module(
    module_code: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_maintainer),
):
    """
    获取指定模块的提示词配置
    
    需要维护者权限。
    """
    hospital_id = require_hospital_id()
    
    # 确保模块已初始化
    from app.services.ai_prompt_module_service import AIPromptModuleService
    AIPromptModuleService.ensure_modules_initialized(db, hospital_id)
    
    module = db.query(AIPromptModule).filter(
        AIPromptModule.hospital_id == hospital_id,
        AIPromptModule.module_code == module_code
    ).first()
    
    if not module:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"模块 '{module_code}' 不存在"
        )
    
    return {
        "code": 200,
        "message": "success",
        "data": _build_response(module, db).model_dump(),
    }


@router.put("/{module_code}", response_model=dict)
def update_prompt_module(
    module_code: str,
    data: AIPromptModuleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_maintainer),
):
    """
    更新提示词模块配置
    
    需要维护者权限。可更新AI接口关联、温度、系统提示词和用户提示词。
    """
    hospital_id = require_hospital_id()
    
    # 确保模块已初始化
    from app.services.ai_prompt_module_service import AIPromptModuleService
    AIPromptModuleService.ensure_modules_initialized(db, hospital_id)
    
    module = db.query(AIPromptModule).filter(
        AIPromptModule.hospital_id == hospital_id,
        AIPromptModule.module_code == module_code
    ).first()
    
    if not module:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"模块 '{module_code}' 不存在"
        )
    
    # 验证AI接口是否存在且属于当前医疗机构
    if data.ai_interface_id is not None:
        if data.ai_interface_id > 0:  # 正数表示设置接口
            ai_interface = db.query(AIInterface).filter(
                AIInterface.id == data.ai_interface_id,
                AIInterface.hospital_id == hospital_id
            ).first()
            if not ai_interface:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="指定的AI接口不存在或不属于当前医疗机构"
                )
            module.ai_interface_id = data.ai_interface_id
        else:  # 0或负数表示取消关联
            module.ai_interface_id = None
    
    # 更新其他字段
    if data.temperature is not None:
        module.temperature = data.temperature
    if data.system_prompt is not None:
        module.system_prompt = data.system_prompt if data.system_prompt else None
    if data.user_prompt is not None:
        module.user_prompt = data.user_prompt
    
    db.commit()
    db.refresh(module)
    
    logger.info(f"更新提示词模块: module_code={module_code}, hospital_id={hospital_id}")
    
    return {
        "code": 200,
        "message": "更新成功",
        "data": _build_response(module, db).model_dump(),
    }
