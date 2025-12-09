"""
分类任务相关的Pydantic模型
"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import datetime
from decimal import Decimal


class ClassificationTaskCreate(BaseModel):
    """创建分类任务"""
    task_name: str = Field(..., description="任务名称", min_length=1, max_length=100)
    model_version_id: int = Field(..., description="模型版本ID", gt=0)
    charge_categories: List[str] = Field(..., description="收费类别列表", min_length=1)

    model_config = {"protected_namespaces": ()}

    @field_validator('charge_categories')
    @classmethod
    def validate_charge_categories(cls, v: List[str]) -> List[str]:
        """验证收费类别不为空"""
        if not v or len(v) == 0:
            raise ValueError('收费类别列表不能为空')
        return v


class ClassificationTaskResponse(BaseModel):
    """分类任务响应"""
    id: int
    hospital_id: int
    task_name: str
    model_version_id: int
    charge_categories: List[str]
    status: str  # pending, processing, completed, failed, paused
    total_items: int
    processed_items: int
    failed_items: int
    celery_task_id: Optional[str]
    error_message: Optional[str]
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    created_by: int
    created_at: datetime
    updated_at: datetime
    
    # 计算属性
    progress_percentage: Optional[float] = Field(None, description="进度百分比（0-100）")

    model_config = {"from_attributes": True, "protected_namespaces": ()}


class ClassificationTaskListResponse(BaseModel):
    """分类任务列表响应"""
    total: int
    items: List[ClassificationTaskResponse]


class TaskProgressResponse(BaseModel):
    """任务进度响应"""
    task_id: int
    status: str
    total_items: int
    processed_items: int
    failed_items: int
    progress_percentage: float = Field(..., description="进度百分比（0-100）")
    current_item: Optional[str] = Field(None, description="当前处理项目名称")
    estimated_remaining_time: Optional[int] = Field(None, description="预计剩余时间（秒）")


class TaskProgressRecordResponse(BaseModel):
    """任务进度记录响应"""
    id: int
    task_id: int
    charge_item_id: int
    charge_item_name: Optional[str] = Field(None, description="收费项目名称")
    status: str  # pending, processing, completed, failed
    error_message: Optional[str]
    processed_at: Optional[datetime]
    created_at: datetime

    model_config = {"from_attributes": True}


class TaskLogResponse(BaseModel):
    """任务日志响应"""
    task_id: int
    task_name: str
    status: str
    total_items: int
    processed_items: int
    failed_items: int
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    duration: Optional[int] = Field(None, description="执行时长（秒）")
    failed_records: List[TaskProgressRecordResponse] = Field(default_factory=list, description="失败记录列表")


class ContinueTaskRequest(BaseModel):
    """继续处理任务请求"""
    task_id: int = Field(..., description="任务ID", gt=0)


class ContinueTaskResponse(BaseModel):
    """继续处理任务响应"""
    success: bool
    message: str
    celery_task_id: Optional[str] = Field(None, description="新的Celery任务ID")
