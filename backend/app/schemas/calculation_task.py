"""
计算任务相关的Pydantic模型
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from decimal import Decimal


# 计算任务相关
class CalculationTaskCreate(BaseModel):
    """创建计算任务"""
    model_version_id: int = Field(..., description="模型版本ID")
    workflow_id: Optional[int] = Field(None, description="计算流程ID")
    department_ids: Optional[List[int]] = Field(None, description="科室ID列表，为空则计算所有科室")
    period: str = Field(..., description="计算周期(YYYY-MM)")
    description: Optional[str] = Field(None, description="任务描述")


class CalculationTaskResponse(BaseModel):
    """计算任务响应"""
    id: int
    task_id: str
    model_version_id: int
    workflow_id: Optional[int]
    period: str
    status: str
    progress: Decimal
    description: Optional[str]
    error_message: Optional[str]
    created_at: datetime
    started_at: Optional[datetime]
    completed_at: Optional[datetime]

    model_config = {"from_attributes": True, "protected_namespaces": ()}


class CalculationTaskListResponse(BaseModel):
    """计算任务列表响应"""
    total: int
    items: List[CalculationTaskResponse]


# 计算结果相关
class CalculationResultResponse(BaseModel):
    """计算结果响应"""
    id: int
    task_id: str
    department_id: int
    node_id: int
    node_name: str
    node_code: Optional[str]
    node_type: Optional[str]
    parent_id: Optional[int]
    workload: Optional[Decimal]
    weight: Optional[Decimal]
    value: Optional[Decimal]
    ratio: Optional[Decimal]

    model_config = {"from_attributes": True}


class DimensionDetail(BaseModel):
    """维度详情 - 支持树形结构"""
    node_id: int
    parent_id: Optional[int]
    dimension_name: str
    dimension_code: Optional[str]
    level: int  # 维度层级：1=一级，2=二级，3=三级
    value: Decimal
    ratio: Decimal
    workload: Optional[Decimal]
    weight: Optional[Decimal]
    business_guide: Optional[str]  # 业务导向
    children: List['DimensionDetail'] = []  # 子维度


class SequenceDetail(BaseModel):
    """序列详情"""
    sequence_type: str
    sequence_name: str
    total_value: Decimal
    dimensions: List[DimensionDetail]  # 树形结构的维度列表


class StructureRow(BaseModel):
    """结构表行数据（按模型结构展示）"""
    level1: Optional[str] = None  # 一级维度
    level2: Optional[str] = None  # 二级维度
    level3: Optional[str] = None  # 三级维度
    level4: Optional[str] = None  # 四级维度（如果有）
    workload: Optional[Decimal] = None  # 工作量（总收入）
    hospital_value: Optional[str] = None  # 全院业务价值（权重/单价），非末级用"-"
    business_guide: Optional[str] = None  # 业务导向，非末级用"-"
    dept_value: Optional[str] = None  # 科室业务价值，非末级用"-"
    amount: Optional[Decimal] = None  # 金额
    ratio: Optional[Decimal] = None  # 占比


class DepartmentDetailResponse(BaseModel):
    """科室详细业务价值数据"""
    department_id: int
    department_name: str
    period: str
    sequences: List[SequenceDetail]  # 保留旧格式兼容性
    # 新增：Excel模板格式
    doctor: Optional[List[StructureRow]] = None  # 医生序列
    nurse: Optional[List[StructureRow]] = None  # 护理序列
    tech: Optional[List[StructureRow]] = None  # 医技序列


# 汇总数据相关
class CalculationSummaryResponse(BaseModel):
    """计算结果汇总响应"""
    department_id: int
    department_name: str
    doctor_value: Decimal
    doctor_ratio: Decimal
    nurse_value: Decimal
    nurse_ratio: Decimal
    tech_value: Decimal
    tech_ratio: Decimal
    total_value: Decimal

    model_config = {"from_attributes": True}


class SummaryListResponse(BaseModel):
    """汇总列表响应"""
    task_id: str  # 任务ID
    summary: CalculationSummaryResponse  # 全院汇总
    departments: List[CalculationSummaryResponse]  # 各科室数据


# 报表导出相关
class ExportSummaryRequest(BaseModel):
    """导出汇总表请求"""
    period: str = Field(..., description="评估月份(YYYY-MM)")
    model_version_id: Optional[int] = Field(None, description="模型版本ID")
    department_ids: Optional[List[int]] = Field(None, description="科室ID列表")


class ExportDetailRequest(BaseModel):
    """导出明细表请求"""
    task_id: str = Field(..., description="计算任务ID")
    department_ids: Optional[List[int]] = Field(None, description="科室ID列表")


class ExportTaskResponse(BaseModel):
    """导出任务响应"""
    task_id: str
    download_url: Optional[str] = None
