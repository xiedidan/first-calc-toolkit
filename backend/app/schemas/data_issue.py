"""
数据问题记录相关的Schema
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, validator
from enum import Enum


class ProcessingStageEnum(str, Enum):
    """处理阶段枚举"""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CONFIRMED = "confirmed"


class DataIssueBase(BaseModel):
    """数据问题记录基础Schema"""
    title: str = Field(..., min_length=1, max_length=200, description="问题标题")
    description: str = Field(..., min_length=1, description="问题描述")
    reporter: str = Field(..., min_length=1, max_length=100, description="记录人姓名")
    reporter_user_id: Optional[int] = Field(None, description="记录人用户ID")
    assignee: Optional[str] = Field(None, max_length=100, description="负责人姓名")
    assignee_user_id: Optional[int] = Field(None, description="负责人用户ID")
    processing_stage: ProcessingStageEnum = Field(ProcessingStageEnum.NOT_STARTED, description="处理阶段")
    resolution: Optional[str] = Field(None, description="解决方案")

    @validator('resolution', always=True)
    def validate_resolution(cls, v, values):
        """验证：当处理阶段为已解决时，解决方案必填"""
        processing_stage = values.get('processing_stage')
        if processing_stage == ProcessingStageEnum.RESOLVED and not v:
            raise ValueError('处理阶段为"已解决"时，必须填写解决方案')
        return v


class DataIssueCreate(DataIssueBase):
    """创建数据问题记录Schema"""
    pass


class DataIssueUpdate(BaseModel):
    """更新数据问题记录Schema"""
    title: Optional[str] = Field(None, min_length=1, max_length=200, description="问题标题")
    description: Optional[str] = Field(None, min_length=1, description="问题描述")
    reporter: Optional[str] = Field(None, min_length=1, max_length=100, description="记录人姓名")
    reporter_user_id: Optional[int] = Field(None, description="记录人用户ID")
    assignee: Optional[str] = Field(None, max_length=100, description="负责人姓名")
    assignee_user_id: Optional[int] = Field(None, description="负责人用户ID")
    processing_stage: Optional[ProcessingStageEnum] = Field(None, description="处理阶段")
    resolution: Optional[str] = Field(None, description="解决方案")

    @validator('resolution', always=True)
    def validate_resolution(cls, v, values):
        """验证：当处理阶段为已解决时，解决方案必填"""
        processing_stage = values.get('processing_stage')
        if processing_stage == ProcessingStageEnum.RESOLVED and not v:
            raise ValueError('处理阶段为"已解决"时，必须填写解决方案')
        return v



class DataIssue(DataIssueBase):
    """数据问题记录响应Schema"""
    id: int
    hospital_id: int
    created_at: datetime
    resolved_at: Optional[datetime]
    updated_at: datetime

    class Config:
        from_attributes = True


class DataIssueList(BaseModel):
    """数据问题记录列表Schema"""
    total: int
    items: list[DataIssue]
