"""
系统设置API路由
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.schemas.system_setting import (
    SystemSettingsResponse,
    SystemSettingsUpdate,
)
from app.services.system_setting_service import SystemSettingService

router = APIRouter()


@router.get("", response_model=dict)
def get_system_settings(
    db: Session = Depends(get_db),
):
    """获取系统设置"""
    settings = SystemSettingService.get_all_settings(db)
    
    return {
        "code": 200,
        "message": "success",
        "data": settings,
    }


@router.put("", response_model=dict)
def update_system_settings(
    settings_update: SystemSettingsUpdate,
    db: Session = Depends(get_db),
):
    """
    更新系统设置
    
    注意：此接口需要系统管理员权限（权限控制待实现）
    """
    settings = SystemSettingService.update_settings(db, settings_update)
    
    return {
        "code": 200,
        "message": "更新成功",
        "data": settings,
    }
