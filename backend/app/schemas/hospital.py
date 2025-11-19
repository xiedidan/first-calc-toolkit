"""
医疗机构相关的Schema
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, validator
import re


class HospitalBase(BaseModel):
    """医疗机构基础Schema"""
    code: str = Field(..., min_length=2, max_length=50, description="医疗机构编码")
    name: str = Field(..., min_length=2, max_length=200, description="医疗机构名称")
    is_active: bool = Field(True, description="是否启用")

    @validator('code')
    def validate_code(cls, v):
        """验证医疗机构编码格式：只允许字母、数字和下划线"""
        if not re.match(r'^[a-zA-Z0-9_]+$', v):
            raise ValueError('医疗机构编码只能包含字母、数字和下划线')
        return v.lower()  # 统一转换为小写


class HospitalCreate(HospitalBase):
    """创建医疗机构Schema"""
    pass


class HospitalUpdate(BaseModel):
    """更新医疗机构Schema"""
    name: Optional[str] = Field(None, min_length=2, max_length=200, description="医疗机构名称")
    is_active: Optional[bool] = Field(None, description="是否启用")
    # 注意：不允许修改code字段


class Hospital(HospitalBase):
    """医疗机构响应Schema"""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class HospitalList(BaseModel):
    """医疗机构列表Schema"""
    total: int
    items: list[Hospital]


class HospitalActivate(BaseModel):
    """激活医疗机构响应Schema"""
    hospital_id: int
    hospital_name: str
    message: str = "医疗机构激活成功"
