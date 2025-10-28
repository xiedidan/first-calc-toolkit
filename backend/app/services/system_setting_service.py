"""
系统设置服务
"""
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.system_setting import SystemSetting
from app.schemas.system_setting import (
    SystemSettingCreate,
    SystemSettingUpdate,
    SystemSettingsResponse,
    SystemSettingsUpdate,
)


class SystemSettingService:
    """系统设置服务"""
    
    # 预定义的系统设置键
    KEY_CURRENT_PERIOD = "current_period"
    KEY_SYSTEM_NAME = "system_name"
    KEY_SYSTEM_VERSION = "system_version"
    
    @staticmethod
    def get_setting(db: Session, key: str) -> Optional[SystemSetting]:
        """
        获取单个系统设置
        
        Args:
            db: 数据库会话
            key: 设置键
            
        Returns:
            系统设置对象，如果不存在则返回None
        """
        return db.query(SystemSetting).filter(SystemSetting.key == key).first()
    
    @staticmethod
    def get_setting_value(db: Session, key: str, default: Optional[str] = None) -> Optional[str]:
        """
        获取系统设置值
        
        Args:
            db: 数据库会话
            key: 设置键
            default: 默认值
            
        Returns:
            设置值，如果不存在则返回默认值
        """
        setting = SystemSettingService.get_setting(db, key)
        return setting.value if setting else default
    
    @staticmethod
    def set_setting(db: Session, key: str, value: Optional[str], description: Optional[str] = None) -> SystemSetting:
        """
        设置系统设置
        
        Args:
            db: 数据库会话
            key: 设置键
            value: 设置值
            description: 设置描述
            
        Returns:
            系统设置对象
        """
        setting = db.query(SystemSetting).filter(SystemSetting.key == key).first()
        
        if setting:
            # 更新现有设置
            setting.value = value
            if description is not None:
                setting.description = description
        else:
            # 创建新设置
            setting = SystemSetting(
                key=key,
                value=value,
                description=description
            )
            db.add(setting)
        
        db.commit()
        db.refresh(setting)
        
        return setting
    
    @staticmethod
    def get_all_settings(db: Session) -> SystemSettingsResponse:
        """
        获取所有系统设置
        
        Args:
            db: 数据库会话
            
        Returns:
            系统设置响应对象
        """
        current_period = SystemSettingService.get_setting_value(db, SystemSettingService.KEY_CURRENT_PERIOD)
        system_name = SystemSettingService.get_setting_value(db, SystemSettingService.KEY_SYSTEM_NAME, "医院科室业务价值评估工具")
        system_version = SystemSettingService.get_setting_value(db, SystemSettingService.KEY_SYSTEM_VERSION, "1.0.0")
        
        return SystemSettingsResponse(
            current_period=current_period,
            system_name=system_name,
            version=system_version,
        )
    
    @staticmethod
    def update_settings(db: Session, settings_update: SystemSettingsUpdate) -> SystemSettingsResponse:
        """
        批量更新系统设置
        
        Args:
            db: 数据库会话
            settings_update: 系统设置更新数据
            
        Returns:
            更新后的系统设置响应对象
        """
        # 更新当期年月
        if settings_update.current_period is not None:
            SystemSettingService.set_setting(
                db,
                SystemSettingService.KEY_CURRENT_PERIOD,
                settings_update.current_period,
                "当期年月，用于计算任务的默认计算周期"
            )
        
        # 更新系统名称
        if settings_update.system_name is not None:
            SystemSettingService.set_setting(
                db,
                SystemSettingService.KEY_SYSTEM_NAME,
                settings_update.system_name,
                "系统名称"
            )
        
        # 返回更新后的设置
        return SystemSettingService.get_all_settings(db)
    
    @staticmethod
    def initialize_default_settings(db: Session):
        """
        初始化默认系统设置
        
        Args:
            db: 数据库会话
        """
        # 检查是否已经初始化
        existing_count = db.query(SystemSetting).count()
        if existing_count > 0:
            return
        
        # 初始化默认设置
        default_settings = [
            {
                "key": SystemSettingService.KEY_SYSTEM_NAME,
                "value": "医院科室业务价值评估工具",
                "description": "系统名称"
            },
            {
                "key": SystemSettingService.KEY_SYSTEM_VERSION,
                "value": "1.0.0",
                "description": "系统版本"
            },
        ]
        
        for setting_data in default_settings:
            setting = SystemSetting(**setting_data)
            db.add(setting)
        
        db.commit()
