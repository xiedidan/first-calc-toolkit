"""
分类预案相关的Pydantic模型
"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import datetime
from decimal import Decimal


class PlanItemResponse(BaseModel):
    """预案项目响应（包含AI建议和用户设置）"""
    id: int
    plan_id: int
    charge_item_id: int
    charge_item_name: str
    charge_item_code: Optional[str] = Field(None, description="项目编码")
    charge_item_category: Optional[str] = Field(None, description="项目类别")
    
    # AI建议
    ai_suggested_dimension_id: Optional[int] = Field(None, description="AI建议维度ID")
    ai_suggested_dimension_name: Optional[str] = Field(None, description="AI建议维度名称")
    ai_suggested_dimension_path: Optional[str] = Field(None, description="AI建议维度路径")
    ai_confidence: Optional[Decimal] = Field(None, description="AI确信度（0-1）")
    
    # 用户设置
    user_set_dimension_id: Optional[int] = Field(None, description="用户设置维度ID")
    user_set_dimension_name: Optional[str] = Field(None, description="用户设置维度名称")
    user_set_dimension_path: Optional[str] = Field(None, description="用户设置维度路径")
    is_adjusted: bool = Field(False, description="是否已调整")
    
    # 最终维度（用户设置 ?? AI建议）
    final_dimension_id: Optional[int] = Field(None, description="最终维度ID")
    final_dimension_name: Optional[str] = Field(None, description="最终维度名称")
    final_dimension_path: Optional[str] = Field(None, description="最终维度路径")
    
    # 处理状态
    processing_status: str = Field(..., description="处理状态")  # pending, processing, completed, failed
    error_message: Optional[str] = Field(None, description="错误信息")
    
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class PlanItemUpdate(BaseModel):
    """调整预案项目维度"""
    dimension_id: Optional[int] = Field(None, description="新的维度ID，为null表示不设维度（跳过该项目）")


class ClassificationPlanResponse(BaseModel):
    """分类预案响应"""
    id: int
    hospital_id: int
    task_id: int
    plan_name: Optional[str] = Field(None, description="预案名称")
    status: str  # draft, submitted
    submitted_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    
    # 任务元数据
    task_name: Optional[str] = Field(None, description="关联任务名称")
    model_version_id: Optional[int] = Field(None, description="模型版本ID")
    charge_categories: Optional[List[str]] = Field(None, description="收费类别列表")
    
    # 统计信息
    total_items: int = Field(0, description="总项目数")
    adjusted_items: int = Field(0, description="已调整项目数")
    low_confidence_items: int = Field(0, description="低确信度项目数（<0.5）")

    model_config = {"from_attributes": True, "protected_namespaces": ()}


class ClassificationPlanListResponse(BaseModel):
    """分类预案列表响应"""
    total: int
    items: List[ClassificationPlanResponse]


class PlanItemListResponse(BaseModel):
    """预案项目列表响应"""
    total: int
    items: List[PlanItemResponse]


class PlanItemQueryParams(BaseModel):
    """预案项目查询参数"""
    sort_by: Optional[str] = Field(None, description="排序字段：confidence_asc, confidence_desc")
    min_confidence: Optional[float] = Field(None, description="最小确信度", ge=0.0, le=1.0)
    max_confidence: Optional[float] = Field(None, description="最大确信度", ge=0.0, le=1.0)
    is_adjusted: Optional[bool] = Field(None, description="是否已调整")
    processing_status: Optional[str] = Field(None, description="处理状态")
    page: int = Field(1, description="页码", ge=1)
    size: int = Field(50, description="每页数量", ge=1, le=1000)


class UpdatePlanRequest(BaseModel):
    """更新预案请求"""
    plan_name: Optional[str] = Field(None, description="预案名称", min_length=1, max_length=100)

    @field_validator('plan_name')
    @classmethod
    def validate_plan_name(cls, v: Optional[str]) -> Optional[str]:
        """验证预案名称"""
        if v is not None and (len(v) == 0 or len(v) > 100):
            raise ValueError('预案名称长度必须在1-100字符之间')
        return v


class SubmitPreviewItem(BaseModel):
    """提交预览项目"""
    item_id: int
    item_name: str
    dimension_id: int
    dimension_name: str
    dimension_path: str


class SubmitPreviewOverwriteItem(SubmitPreviewItem):
    """提交预览覆盖项目（包含原维度信息）"""
    old_dimension_id: int
    old_dimension_name: str
    old_dimension_path: str


class SubmitPreviewResponse(BaseModel):
    """提交预览响应（新增/覆盖分析）"""
    plan_id: int
    plan_name: Optional[str]
    
    # 统计
    total_items: int = Field(..., description="总项目数")
    new_count: int = Field(..., description="新增项目数")
    overwrite_count: int = Field(..., description="覆盖项目数")
    
    # 详细列表
    new_items: List[SubmitPreviewItem] = Field(default_factory=list, description="新增项目列表")
    overwrite_items: List[SubmitPreviewOverwriteItem] = Field(default_factory=list, description="覆盖项目列表")
    
    # 警告信息
    warnings: List[str] = Field(default_factory=list, description="警告信息列表")


class SubmitPlanRequest(BaseModel):
    """提交预案请求"""
    confirm: bool = Field(True, description="确认提交")


class SubmitPlanResponse(BaseModel):
    """提交预案响应"""
    success: bool
    message: str
    new_count: int = Field(0, description="新增项目数")
    overwrite_count: int = Field(0, description="覆盖项目数")
    submitted_at: Optional[datetime] = Field(None, description="提交时间")
