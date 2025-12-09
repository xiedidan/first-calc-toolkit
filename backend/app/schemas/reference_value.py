"""
参考价值相关的Schema
"""
from datetime import datetime
from typing import Optional, List
from decimal import Decimal
from pydantic import BaseModel, Field


class ReferenceValueBase(BaseModel):
    """参考价值基础Schema"""
    period: str = Field(..., description="年月，格式：YYYY-MM")
    department_code: str = Field(..., description="科室代码")
    department_name: str = Field(..., description="科室名称")
    reference_value: Decimal = Field(..., description="参考总价值")
    doctor_reference_value: Optional[Decimal] = Field(None, description="医生参考价值")
    nurse_reference_value: Optional[Decimal] = Field(None, description="护理参考价值")
    tech_reference_value: Optional[Decimal] = Field(None, description="医技参考价值")


class ReferenceValueCreate(ReferenceValueBase):
    """创建参考价值Schema"""
    pass


class ReferenceValueUpdate(BaseModel):
    """更新参考价值Schema"""
    period: Optional[str] = Field(None, description="年月")
    department_code: Optional[str] = Field(None, description="科室代码")
    department_name: Optional[str] = Field(None, description="科室名称")
    reference_value: Optional[Decimal] = Field(None, description="参考总价值")
    doctor_reference_value: Optional[Decimal] = Field(None, description="医生参考价值")
    nurse_reference_value: Optional[Decimal] = Field(None, description="护理参考价值")
    tech_reference_value: Optional[Decimal] = Field(None, description="医技参考价值")


class ReferenceValue(ReferenceValueBase):
    """参考价值Schema"""
    id: int
    hospital_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ReferenceValueList(BaseModel):
    """参考价值列表Schema"""
    total: int
    items: List[ReferenceValue]


# 智能导入相关Schema

class RefValueImportParseResponse(BaseModel):
    """参考价值导入解析响应Schema"""
    session_id: str = Field(..., description="会话ID")
    sheet_names: List[str] = Field(..., description="所有Sheet名称列表")
    current_sheet: str = Field(..., description="当前选中的Sheet")
    headers: List[str] = Field(..., description="Excel表头列表")
    preview_data: List[List[str]] = Field(..., description="预览数据")
    total_rows: int = Field(..., description="总行数")
    skip_rows: int = Field(..., description="跳过的行数")
    suggested_mapping: dict = Field(..., description="建议的字段映射")


class RefValueImportFieldMapping(BaseModel):
    """参考价值导入字段映射Schema"""
    session_id: str = Field(..., description="会话ID")
    field_mapping: dict = Field(..., description="字段映射")
    match_by: str = Field("code", description="匹配方式：code(按科室代码精确匹配) 或 name(按科室名称模糊匹配)")


class DepartmentMatch(BaseModel):
    """科室匹配Schema"""
    id: int
    code: str
    name: str
    score: float = Field(1.0, description="匹配得分")


class UniqueValueForMatch(BaseModel):
    """待匹配的唯一值Schema"""
    value: str = Field(..., description="Excel中的科室名称")
    count: int = Field(..., description="出现次数")
    suggested_departments: List[DepartmentMatch] = Field(..., description="建议匹配的科室")


class RefValueImportExtractResponse(BaseModel):
    """参考价值导入提取唯一值响应Schema"""
    unique_values: List[UniqueValueForMatch]
    system_departments: List[DepartmentMatch]


class DepartmentValueMapping(BaseModel):
    """科室值映射Schema"""
    value: str = Field(..., description="Excel中的科室名称")
    department_code: Optional[str] = Field(None, description="匹配的科室代码")


class RefValueImportPreviewRequest(BaseModel):
    """参考价值导入预览请求Schema"""
    session_id: str = Field(..., description="会话ID")
    value_mapping: List[DepartmentValueMapping] = Field(..., description="科室值映射")


class RefValuePreviewItem(BaseModel):
    """参考价值预览项Schema"""
    period: str
    department_code: str
    department_name: str
    excel_department_name: str = Field(..., description="Excel中的科室名称")
    reference_value: Decimal
    doctor_reference_value: Optional[Decimal] = None
    nurse_reference_value: Optional[Decimal] = None
    tech_reference_value: Optional[Decimal] = None
    status: str = Field(..., description="状态：new(新增), update(覆盖), error(错误)")
    message: str = Field("", description="提示信息")


class RefValuePreviewStatistics(BaseModel):
    """参考价值预览统计Schema"""
    total: int
    new_count: int = Field(..., description="新增数量")
    update_count: int = Field(..., description="覆盖数量")
    error_count: int = Field(..., description="错误数量")


class RefValueImportPreviewResponse(BaseModel):
    """参考价值导入预览响应Schema"""
    preview_items: List[RefValuePreviewItem]
    statistics: RefValuePreviewStatistics


class RefValueImportExecuteRequest(BaseModel):
    """参考价值导入执行请求Schema"""
    session_id: str = Field(..., description="会话ID")
    confirmed_items: Optional[List[RefValuePreviewItem]] = Field(None, description="用户确认的导入项")


class RefValueImportError(BaseModel):
    """参考价值导入错误Schema"""
    period: str
    department_code: str
    reason: str


class RefValueImportReport(BaseModel):
    """参考价值导入报告Schema"""
    success_count: int
    update_count: int
    error_count: int
    errors: List[RefValueImportError]


class RefValueImportExecuteResponse(BaseModel):
    """参考价值导入执行响应Schema"""
    success: bool
    report: RefValueImportReport
