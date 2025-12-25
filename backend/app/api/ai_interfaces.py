"""
AI接口配置API路由 - 智能问数系统
支持多AI接口管理，按模块分配不同的AI服务
"""
import time
import logging
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List

from app.api.deps import get_db, get_current_active_user
from app.models import User, AIInterface, AIPromptModule
from app.middleware.hospital_context import require_hospital_id
from app.schemas.ai_interface import (
    AIInterfaceCreate,
    AIInterfaceUpdate,
    AIInterfaceResponse,
    AIInterfaceListResponse,
    AIInterfaceTestRequest,
    AIInterfaceTestConfigRequest,
    AIInterfaceTestResponse,
)
from app.utils.encryption import encrypt_api_key, decrypt_api_key, mask_api_key

logger = logging.getLogger(__name__)

router = APIRouter()


def require_maintainer(current_user: User = Depends(get_current_active_user)) -> User:
    """
    要求维护者权限（AI接口管理仅维护者和管理员可用）
    """
    from app.models.role import RoleType
    
    # 管理员和维护者都可以访问
    is_allowed = any(
        role.role_type in (RoleType.MAINTAINER, RoleType.ADMIN)
        for role in current_user.roles
    )
    if not is_allowed:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="需要维护者或管理员权限"
        )
    return current_user


def _auto_link_to_unconfigured_modules(db: Session, hospital_id: int, interface_id: int) -> int:
    """
    自动将AI接口关联到所有未配置接口的提示词模块
    
    Returns:
        关联的模块数量
    """
    # 确保提示词模块已初始化
    from app.services.ai_prompt_module_service import AIPromptModuleService
    AIPromptModuleService.ensure_modules_initialized(db, hospital_id)
    
    # 查找所有未配置接口的模块
    unconfigured_modules = db.query(AIPromptModule).filter(
        AIPromptModule.hospital_id == hospital_id,
        AIPromptModule.ai_interface_id.is_(None)
    ).all()
    
    # 关联接口
    for module in unconfigured_modules:
        module.ai_interface_id = interface_id
        logger.info(f"自动关联AI接口到模块: interface_id={interface_id}, module={module.module_code}")
    
    if unconfigured_modules:
        db.commit()
    
    return len(unconfigured_modules)


def _build_response(ai_interface: AIInterface, db: Session) -> AIInterfaceResponse:
    """构建AI接口响应对象"""
    # 获取引用此接口的模块列表
    referenced_modules = db.query(AIPromptModule.module_name).filter(
        AIPromptModule.ai_interface_id == ai_interface.id
    ).all()
    module_names = [m[0] for m in referenced_modules]
    
    return AIInterfaceResponse(
        id=ai_interface.id,
        hospital_id=ai_interface.hospital_id,
        name=ai_interface.name,
        api_endpoint=ai_interface.api_endpoint,
        model_name=ai_interface.model_name,
        api_key_masked=mask_api_key(ai_interface.api_key_encrypted),
        call_delay=ai_interface.call_delay,
        daily_limit=ai_interface.daily_limit,
        is_active=ai_interface.is_active,
        created_at=ai_interface.created_at,
        updated_at=ai_interface.updated_at,
        referenced_modules=module_names,
    )



@router.get("", response_model=dict)
def list_ai_interfaces(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_maintainer),
):
    """
    获取AI接口列表
    
    需要维护者权限。返回当前医疗机构的所有AI接口配置。
    """
    hospital_id = require_hospital_id()
    
    interfaces = db.query(AIInterface).filter(
        AIInterface.hospital_id == hospital_id
    ).order_by(AIInterface.created_at.desc()).all()
    
    items = [_build_response(i, db) for i in interfaces]
    
    return {
        "code": 200,
        "message": "success",
        "data": {
            "items": [item.model_dump() for item in items],
            "total": len(items),
        },
    }


@router.post("", response_model=dict)
def create_ai_interface(
    data: AIInterfaceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_maintainer),
):
    """
    创建AI接口配置
    
    需要维护者权限。创建后会自动关联到所有未配置接口的提示词模块。
    """
    hospital_id = require_hospital_id()
    
    # 检查名称是否重复
    existing = db.query(AIInterface).filter(
        AIInterface.hospital_id == hospital_id,
        AIInterface.name == data.name
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"接口名称 '{data.name}' 已存在"
        )
    
    # 加密API密钥
    encrypted_key = encrypt_api_key(data.api_key)
    
    # 创建接口
    ai_interface = AIInterface(
        hospital_id=hospital_id,
        name=data.name,
        api_endpoint=data.api_endpoint,
        model_name=data.model_name,
        api_key_encrypted=encrypted_key,
        call_delay=data.call_delay,
        daily_limit=data.daily_limit,
        is_active=data.is_active,
    )
    
    db.add(ai_interface)
    db.commit()
    db.refresh(ai_interface)
    
    # 自动关联到所有未配置接口的提示词模块
    if ai_interface.is_active:
        _auto_link_to_unconfigured_modules(db, hospital_id, ai_interface.id)
    
    logger.info(f"创建AI接口: id={ai_interface.id}, name={ai_interface.name}")
    
    return {
        "code": 200,
        "message": "创建成功",
        "data": _build_response(ai_interface, db).model_dump(),
    }


@router.get("/{interface_id}", response_model=dict)
def get_ai_interface(
    interface_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_maintainer),
):
    """
    获取AI接口详情
    
    需要维护者权限。
    """
    hospital_id = require_hospital_id()
    
    ai_interface = db.query(AIInterface).filter(
        AIInterface.id == interface_id,
        AIInterface.hospital_id == hospital_id
    ).first()
    
    if not ai_interface:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="AI接口不存在"
        )
    
    return {
        "code": 200,
        "message": "success",
        "data": _build_response(ai_interface, db).model_dump(),
    }



@router.put("/{interface_id}", response_model=dict)
def update_ai_interface(
    interface_id: int,
    data: AIInterfaceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_maintainer),
):
    """
    更新AI接口配置
    
    需要维护者权限。API密钥留空表示不修改。
    当接口从禁用变为启用时，会自动关联到未配置接口的提示词模块。
    """
    hospital_id = require_hospital_id()
    
    ai_interface = db.query(AIInterface).filter(
        AIInterface.id == interface_id,
        AIInterface.hospital_id == hospital_id
    ).first()
    
    if not ai_interface:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="AI接口不存在"
        )
    
    # 检查名称是否与其他接口重复
    if data.name and data.name != ai_interface.name:
        existing = db.query(AIInterface).filter(
            AIInterface.hospital_id == hospital_id,
            AIInterface.name == data.name,
            AIInterface.id != interface_id
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"接口名称 '{data.name}' 已存在"
            )
    
    # 记录原来的启用状态
    was_active = ai_interface.is_active
    
    # 更新字段
    if data.name is not None:
        ai_interface.name = data.name
    if data.api_endpoint is not None:
        ai_interface.api_endpoint = data.api_endpoint
    if data.model_name is not None:
        ai_interface.model_name = data.model_name
    if data.api_key:  # 只有提供了新密钥才更新
        ai_interface.api_key_encrypted = encrypt_api_key(data.api_key)
    if data.call_delay is not None:
        ai_interface.call_delay = data.call_delay
    if data.daily_limit is not None:
        ai_interface.daily_limit = data.daily_limit
    if data.is_active is not None:
        ai_interface.is_active = data.is_active
    
    db.commit()
    db.refresh(ai_interface)
    
    # 如果接口从禁用变为启用，自动关联到未配置的模块
    if not was_active and ai_interface.is_active:
        _auto_link_to_unconfigured_modules(db, hospital_id, ai_interface.id)
    
    logger.info(f"更新AI接口: id={ai_interface.id}, name={ai_interface.name}")
    
    return {
        "code": 200,
        "message": "更新成功",
        "data": _build_response(ai_interface, db).model_dump(),
    }


@router.delete("/{interface_id}", response_model=dict)
def delete_ai_interface(
    interface_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_maintainer),
):
    """
    删除AI接口配置
    
    需要维护者权限。如果接口被模块引用，则不允许删除。
    """
    hospital_id = require_hospital_id()
    
    ai_interface = db.query(AIInterface).filter(
        AIInterface.id == interface_id,
        AIInterface.hospital_id == hospital_id
    ).first()
    
    if not ai_interface:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="AI接口不存在"
        )
    
    # 检查是否被模块引用
    referenced_modules = db.query(AIPromptModule).filter(
        AIPromptModule.ai_interface_id == interface_id
    ).all()
    
    if referenced_modules:
        module_names = [m.module_name for m in referenced_modules]
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error_code": "AI_INTERFACE_IN_USE",
                "message": "AI接口被引用，无法删除",
                "referenced_by": module_names
            }
        )
    
    interface_name = ai_interface.name
    db.delete(ai_interface)
    db.commit()
    
    logger.info(f"删除AI接口: id={interface_id}, name={interface_name}")
    
    return {
        "code": 200,
        "message": "删除成功",
    }


@router.post("/test-config", response_model=dict)
def test_ai_interface_config(
    test_data: AIInterfaceTestConfigRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_maintainer),
):
    """
    使用自定义配置测试AI接口（用于保存前测试）
    
    需要维护者权限。直接使用传入的配置参数进行测试，无需先保存。
    如果没有提供 api_key 但提供了 interface_id，则从数据库获取已保存的密钥。
    """
    hospital_id = require_hospital_id()
    
    # 确定要使用的 API 密钥
    api_key = test_data.api_key
    
    if not api_key:
        # 没有提供新密钥，尝试从数据库获取
        if not test_data.interface_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="请提供API密钥或现有接口ID"
            )
        
        # 从数据库获取现有接口的密钥
        ai_interface = db.query(AIInterface).filter(
            AIInterface.id == test_data.interface_id,
            AIInterface.hospital_id == hospital_id
        ).first()
        
        if not ai_interface:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="AI接口不存在"
            )
        
        try:
            api_key = decrypt_api_key(ai_interface.api_key_encrypted)
        except Exception as e:
            logger.error(f"解密API密钥失败: {str(e)}")
            return {
                "code": 200,
                "message": "测试完成",
                "data": AIInterfaceTestResponse(
                    success=False,
                    error_message="API密钥解密失败，请重新配置密钥"
                ).model_dump(),
            }
    
    # 调用AI接口测试
    start_time = time.time()
    try:
        from app.utils.ai_interface import _call_openai_compatible_api
        
        response_data = _call_openai_compatible_api(
            api_endpoint=test_data.api_endpoint,
            api_key=api_key,
            model_name=test_data.model_name,
            messages=[
                {"role": "user", "content": test_data.test_message}
            ],
            temperature=0.7,
            max_retries=1,
            retry_delay=1.0,
            timeout=30.0
        )
        
        response_time = time.time() - start_time
        
        # 提取响应内容
        choices = response_data.get("choices", [])
        response_content = ""
        if choices:
            response_content = choices[0].get("message", {}).get("content", "")
        
        logger.info(f"AI接口配置测试成功: endpoint={test_data.api_endpoint}, model={test_data.model_name}, response_time={response_time:.2f}s")
        
        return {
            "code": 200,
            "message": "测试完成",
            "data": AIInterfaceTestResponse(
                success=True,
                response_content=response_content[:500] if response_content else None,
                response_time=round(response_time, 2),
            ).model_dump(),
        }
        
    except Exception as e:
        response_time = time.time() - start_time
        error_message = str(e)
        logger.error(f"AI接口配置测试失败: endpoint={test_data.api_endpoint}, error={error_message}")
        
        return {
            "code": 200,
            "message": "测试完成",
            "data": AIInterfaceTestResponse(
                success=False,
                response_time=round(response_time, 2),
                error_message=error_message,
            ).model_dump(),
        }


@router.post("/{interface_id}/test", response_model=dict)
def test_ai_interface(
    interface_id: int,
    test_data: AIInterfaceTestRequest = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_maintainer),
):
    """
    测试AI接口连接
    
    需要维护者权限。发送测试消息验证接口是否正常工作。
    """
    hospital_id = require_hospital_id()
    
    ai_interface = db.query(AIInterface).filter(
        AIInterface.id == interface_id,
        AIInterface.hospital_id == hospital_id
    ).first()
    
    if not ai_interface:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="AI接口不存在"
        )
    
    # 使用默认测试消息
    if test_data is None:
        test_data = AIInterfaceTestRequest()
    
    # 解密API密钥
    try:
        api_key = decrypt_api_key(ai_interface.api_key_encrypted)
    except Exception as e:
        logger.error(f"解密API密钥失败: {str(e)}")
        return {
            "code": 200,
            "message": "测试完成",
            "data": AIInterfaceTestResponse(
                success=False,
                error_message="API密钥解密失败，请重新配置密钥"
            ).model_dump(),
        }
    
    # 调用AI接口测试
    start_time = time.time()
    try:
        from app.utils.ai_interface import _call_openai_compatible_api
        
        response_data = _call_openai_compatible_api(
            api_endpoint=ai_interface.api_endpoint,
            api_key=api_key,
            model_name=ai_interface.model_name,
            messages=[
                {"role": "user", "content": test_data.test_message}
            ],
            temperature=0.7,
            max_retries=1,
            retry_delay=1.0,
            timeout=30.0
        )
        
        response_time = time.time() - start_time
        
        # 提取响应内容
        choices = response_data.get("choices", [])
        response_content = ""
        if choices:
            response_content = choices[0].get("message", {}).get("content", "")
        
        logger.info(f"AI接口测试成功: id={interface_id}, response_time={response_time:.2f}s")
        
        return {
            "code": 200,
            "message": "测试完成",
            "data": AIInterfaceTestResponse(
                success=True,
                response_content=response_content[:500] if response_content else None,  # 限制长度
                response_time=round(response_time, 2),
            ).model_dump(),
        }
        
    except Exception as e:
        response_time = time.time() - start_time
        error_message = str(e)
        logger.error(f"AI接口测试失败: id={interface_id}, error={error_message}")
        
        return {
            "code": 200,
            "message": "测试完成",
            "data": AIInterfaceTestResponse(
                success=False,
                response_time=round(response_time, 2),
                error_message=error_message,
            ).model_dump(),
        }
