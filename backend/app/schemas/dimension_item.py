"""
维度目录相关的Schema
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class ChargeItemBase(BaseModel):
    """收费项目基础Schema"""
    item_code: str = Field(..., description="收费项目编码")
    item_name: str = Field(..., description="收费项目名称")
    item_category: Optional[str] = Field(None, description="收费项目分类")
    unit_price: Optional[str] = Field(None, description="单价")


class ChargeItemCreate(ChargeItemBase):
    """创建收费项目Schema"""
    pass


class ChargeItemUpdate(BaseModel):
    """更新收费项目Schema"""
    item_name: Optional[str] = Field(None, description="收费项目名称")
    item_category: Optional[str] = Field(None, description="收费项目分类")
    unit_price: Optional[str] = Field(None, description="单价")


class ChargeItem(ChargeItemBase):
    """收费项目Schema"""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ChargeItemList(BaseModel):
    """收费项目列表Schema"""
    total: int
    items: list[ChargeItem]


class DimensionItemMappingBase(BaseModel):
    """维度-收费项目映射基础Schema"""
    dimension_code: str = Field(..., description="维度节点编码")
    item_code: str = Field(..., description="收费项目编码")


class DimensionItemMappingCreate(BaseModel):
    """创建维度-收费项目映射Schema"""
    dimension_code: str = Field(..., description="维度节点编码")
    item_codes: list[str] = Field(..., description="收费项目编码列表")


class DimensionItemMapping(DimensionItemMappingBase):
    """维度-收费项目映射Schema"""
    id: int
    item_name: Optional[str] = None
    item_category: Optional[str] = None
    dimension_name: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class DimensionItemList(BaseModel):
    """维度目录列表Schema"""
    total: int
    items: list[DimensionItemMapping]


# 智能导入相关Schema

class SmartImportParseResponse(BaseModel):
    """智能导入解析响应Schema"""
    session_id: str = Field(..., description="会话ID")
    sheet_names: list[str] = Field(..., description="所有Sheet名称列表")
    current_sheet: str = Field(..., description="当前选中的Sheet")
    headers: list[str] = Field(..., description="Excel表头列表")
    preview_data: list[list[str]] = Field(..., description="预览数据")
    total_rows: int = Field(..., description="总行数")
    skip_rows: int = Field(..., description="跳过的行数")
    suggested_mapping: dict[str, str] = Field(..., description="建议的字段映射")


class SmartImportFieldMapping(BaseModel):
    """智能导入字段映射Schema"""
    session_id: str = Field(..., description="会话ID")
    field_mapping: dict[str, str] = Field(..., description="字段映射")
    model_version_id: int = Field(..., description="模型版本ID")
    match_by: str = Field("code", description="匹配方式：code(按编码) 或 name(按名称)")


class SystemDimension(BaseModel):
    """系统维度Schema"""
    id: int
    name: str
    code: str
    full_path: str


class UniqueValue(BaseModel):
    """唯一值Schema"""
    value: str
    source: str
    count: int
    suggested_dimensions: list[SystemDimension]


class SmartImportExtractResponse(BaseModel):
    """智能导入提取唯一值响应Schema"""
    unique_values: list[UniqueValue]
    system_dimensions: list[SystemDimension]


class ValueMapping(BaseModel):
    """值映射Schema"""
    value: str
    source: str
    dimension_codes: list[str]


class SmartImportPreviewRequest(BaseModel):
    """智能导入预览请求Schema"""
    session_id: str = Field(..., description="会话ID")
    value_mapping: list[ValueMapping] = Field(..., description="维度值映射")


class PreviewItem(BaseModel):
    """预览项Schema"""
    item_code: str
    item_name: str
    dimension_code: str
    dimension_name: str
    dimension_path: str
    source: str
    source_value: str
    status: str
    message: str


class PreviewStatistics(BaseModel):
    """预览统计Schema"""
    total: int
    ok: int
    warning: int
    error: int


class SmartImportPreviewResponse(BaseModel):
    """智能导入预览响应Schema"""
    preview_items: list[PreviewItem]
    statistics: PreviewStatistics


class SmartImportExecuteRequest(BaseModel):
    """智能导入执行请求Schema"""
    session_id: str = Field(..., description="会话ID")
    confirmed_items: Optional[list[PreviewItem]] = Field(None, description="用户确认的导入项")


class ImportError(BaseModel):
    """导入错误Schema"""
    item_code: str
    dimension_code: str
    reason: str


class ImportReport(BaseModel):
    """导入报告Schema"""
    success_count: int
    skipped_count: int
    error_count: int
    errors: list[ImportError]


class SmartImportExecuteResponse(BaseModel):
    """智能导入执行响应Schema"""
    success: bool
    report: ImportReport
