"""
系统设置相关的Pydantic模型
"""
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field, field_validator
import re


class SystemSettingBase(BaseModel):
    """系统设置基础模型"""
    key: str = Field(..., max_length=100, description="设置键")
    value: Optional[str] = Field(None, description="设置值")
    description: Optional[str] = Field(None, description="设置描述")


class SystemSettingCreate(SystemSettingBase):
    """创建系统设置"""
    pass


class SystemSettingUpdate(BaseModel):
    """更新系统设置"""
    value: Optional[str] = Field(None, description="设置值")
    description: Optional[str] = Field(None, description="设置描述")


class SystemSettingInDB(SystemSettingBase):
    """数据库中的系统设置"""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class SystemSettingResponse(SystemSettingInDB):
    """系统设置响应模型"""
    pass


class SystemSettingsResponse(BaseModel):
    """系统设置集合响应模型"""
    current_period: Optional[str] = Field(None, description="当期年月(YYYY-MM)")
    system_name: Optional[str] = Field(None, description="系统名称")
    version: Optional[str] = Field(None, description="系统版本")


class SystemSettingsUpdate(BaseModel):
    """系统设置集合更新模型"""
    current_period: Optional[str] = Field(None, description="当期年月(YYYY-MM)")
    system_name: Optional[str] = Field(None, description="系统名称")

    @field_validator('current_period')
    @classmethod
    def validate_current_period(cls, v):
        """验证当期年月格式"""
        if v is not None and v.strip():
            # 验证格式：YYYY-MM（允许空字符串）
            if not re.match(r'^\d{4}-(0[1-9]|1[0-2])$', v):
                raise ValueError('当期年月格式必须为YYYY-MM，例如：2025-10')
        return v
