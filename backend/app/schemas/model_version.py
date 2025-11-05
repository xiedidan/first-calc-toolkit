"""
模型版本Schema
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class ModelVersionBase(BaseModel):
    """模型版本基础Schema"""
    version: str = Field(..., description="版本号")
    name: str = Field(..., description="版本名称")
    description: Optional[str] = Field(None, description="版本描述")


class ModelVersionCreate(ModelVersionBase):
    """创建模型版本Schema"""
    base_version_id: Optional[int] = Field(None, description="基础版本ID（用于复制）")


class ModelVersionUpdate(BaseModel):
    """更新模型版本Schema"""
    name: Optional[str] = Field(None, description="版本名称")
    description: Optional[str] = Field(None, description="版本描述")


class ModelVersionResponse(ModelVersionBase):
    """模型版本响应Schema"""
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ModelVersionListResponse(BaseModel):
    """模型版本列表响应Schema"""
    total: int
    items: list[ModelVersionResponse]


class ImportableVersionResponse(BaseModel):
    """可导入版本响应Schema"""
    id: int
    version: str = Field(..., description="版本号")
    name: str = Field(..., description="版本名称")
    description: Optional[str] = Field(None, description="版本描述")
    hospital_id: int = Field(..., description="所属医疗机构ID")
    hospital_name: str = Field(..., description="所属医疗机构名称")
    created_at: datetime = Field(..., description="创建时间")

    class Config:
        from_attributes = True


class ImportableVersionListResponse(BaseModel):
    """可导入版本列表响应Schema"""
    total: int
    items: list[ImportableVersionResponse]


class VersionPreviewResponse(BaseModel):
    """版本预览响应Schema"""
    id: int
    version: str
    name: str
    description: Optional[str]
    hospital_name: str
    node_count: int = Field(..., description="节点数量")
    workflow_count: int = Field(..., description="计算流程数量")
    step_count: int = Field(..., description="计算步骤数量")
    created_at: datetime

    class Config:
        from_attributes = True


class ModelVersionImportRequest(BaseModel):
    """模型版本导入请求Schema"""
    source_version_id: int = Field(..., description="源版本ID")
    import_type: str = Field(..., description="导入类型（structure_only/with_workflows）")
    version: str = Field(..., description="新版本号")
    name: str = Field(..., description="新版本名称")
    description: Optional[str] = Field(None, description="新版本描述")


class ModelVersionImportResponse(BaseModel):
    """模型版本导入响应Schema"""
    id: int = Field(..., description="新版本ID")
    version: str = Field(..., description="新版本号")
    name: str = Field(..., description="新版本名称")
    statistics: dict = Field(..., description="导入统计信息")
    warnings: list[str] = Field(default_factory=list, description="警告信息")

    class Config:
        from_attributes = True


class ImportInfoResponse(BaseModel):
    """导入信息响应Schema"""
    is_imported: bool = Field(..., description="是否为导入版本")
    source_version: Optional[str] = Field(None, description="源版本号")
    source_hospital_name: Optional[str] = Field(None, description="源医疗机构名称")
    import_type: Optional[str] = Field(None, description="导入类型")
    import_time: Optional[datetime] = Field(None, description="导入时间")
    importer_name: Optional[str] = Field(None, description="导入用户名")

    class Config:
        from_attributes = True
