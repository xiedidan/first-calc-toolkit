"""
AI配置API路由
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_active_user
from app.models import User
from app.middleware.hospital_context import require_hospital_id
from app.schemas.ai_config import (
    AIConfigCreate,
    AIConfigResponse,
    AIConfigTest,
    APIUsageStatsResponse,
)
from app.services.ai_config_service import AIConfigService

router = APIRouter()


def require_maintainer(current_user: User = Depends(get_current_active_user)) -> User:
    """
    要求维护者权限（AI接口管理仅维护者可用）
    
    Args:
        current_user: 当前用户
        
    Returns:
        当前用户
        
    Raises:
        HTTPException: 如果用户不是维护者
    """
    from app.models.role import RoleType
    
    # 检查用户是否有maintainer角色
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


@router.get("", response_model=dict)
def get_ai_config(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_maintainer),
):
    """
    获取AI配置（密钥掩码）
    
    需要管理员权限。如果配置不存在，会自动创建默认配置。
    """
    hospital_id = require_hospital_id()
    
    config = AIConfigService.get_config(db, hospital_id)
    
    return {
        "code": 200,
        "message": "success",
        "data": config,
    }


@router.post("", response_model=dict)
def create_or_update_ai_config(
    config_data: AIConfigCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_maintainer),
):
    """
    创建或更新AI配置
    
    需要管理员权限
    """
    hospital_id = require_hospital_id()
    
    config = AIConfigService.create_or_update_config(db, hospital_id, config_data)
    
    return {
        "code": 200,
        "message": "保存成功",
        "data": config,
    }


@router.post("/test", response_model=dict)
def test_ai_config(
    test_data: AIConfigTest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_maintainer),
):
    """
    测试AI配置
    
    需要管理员权限
    """
    hospital_id = require_hospital_id()
    
    result = AIConfigService.test_config(db, hospital_id, test_data)
    
    return {
        "code": 200,
        "message": "测试完成",
        "data": result,
    }


@router.get("/usage-stats", response_model=dict)
def get_usage_stats(
    days: int = 30,
    cost_per_call: float = 0.001,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_maintainer),
):
    """
    获取API使用统计
    
    需要管理员权限
    
    Args:
        days: 统计天数，默认30天
        cost_per_call: 每次调用成本（元），默认0.001元
    """
    hospital_id = require_hospital_id()
    
    stats = AIConfigService.get_usage_stats(db, hospital_id, days, cost_per_call)
    
    return {
        "code": 200,
        "message": "success",
        "data": stats,
    }
