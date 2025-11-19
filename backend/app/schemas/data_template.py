"""
数据模板Schema
"""
from typing import Optional, List
from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from decimal import Decimal


class DataTemplateBase(BaseModel):
    """数据模板基础Schema"""
    table_name: str = Field(..., min_length=1, max_length=100, description="表名")
    table_name_cn: str = Field(..., min_length=1, max_length=200, description="中文名")
    description: Optional[str] = Field(None, description="表说明")
    is_core: bool = Field(False, description="是否核心表")
    
    @field_validator('table_name')
    @classmethod
    def validate_table_name(cls, v: str) -> str:
        """验证表名格式"""
        if not v:
            raise ValueError("表名不能为空")
        # 可以添加更多验证规则，如只允许字母、数字、下划线
        return v.strip()
    
    @field_validator('table_name_cn')
    @classmethod
    def validate_table_name_cn(cls, v: str) -> str:
        """验证中文名"""
        if not v:
            raise ValueError("中文名不能为空")
        return v.strip()


class DataTemplateCreate(DataTemplateBase):
    """创建数据模板Schema"""
    sort_order: Optional[Decimal] = Field(None, description="排序序号，不提供则自动设置为最大值+1")


class DataTemplateUpdate(BaseModel):
    """更新数据模板Schema"""
    table_name_cn: Optional[str] = Field(None, min_length=1, max_length=200, description="中文名")
    description: Optional[str] = Field(None, description="表说明")
    is_core: Optional[bool] = Field(None, description="是否核心表")
    sort_order: Optional[Decimal] = Field(None, description="排序序号")


class DataTemplate(DataTemplateBase):
    """数据模板响应Schema"""
    id: int
    hospital_id: int
    sort_order: Decimal
    definition_file_path: Optional[str] = None
    definition_file_name: Optional[str] = None
    sql_file_path: Optional[str] = None
    sql_file_name: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    # 添加计算字段，表示是否已上传文件
    has_definition: bool = Field(default=False, description="是否已上传表定义文档")
    has_sql: bool = Field(default=False, description="是否已上传SQL建表代码")
    
    class Config:
        from_attributes = True
    
    @classmethod
    def from_orm(cls, obj):
        """从ORM对象创建Schema实例"""
        data = {
            'id': obj.id,
            'hospital_id': obj.hospital_id,
            'table_name': obj.table_name,
            'table_name_cn': obj.table_name_cn,
            'description': obj.description,
            'is_core': obj.is_core,
            'sort_order': obj.sort_order,
            'definition_file_path': obj.definition_file_path,
            'definition_file_name': obj.definition_file_name,
            'sql_file_path': obj.sql_file_path,
            'sql_file_name': obj.sql_file_name,
            'created_at': obj.created_at,
            'updated_at': obj.updated_at,
            'has_definition': bool(obj.definition_file_path),
            'has_sql': bool(obj.sql_file_path),
        }
        return cls(**data)


class DataTemplateList(BaseModel):
    """数据模板列表响应Schema"""
    total: int = Field(..., description="总数量")
    items: List[DataTemplate] = Field(..., description="数据模板列表")


class FileUploadResponse(BaseModel):
    """文件上传响应Schema"""
    success: bool = Field(..., description="是否成功")
    message: str = Field(..., description="消息")
    file_name: Optional[str] = Field(None, description="文件名")
    file_path: Optional[str] = Field(None, description="文件路径")


class BatchUploadItem(BaseModel):
    """批量上传项Schema"""
    table_name: str = Field(..., description="表名")
    table_name_cn: Optional[str] = Field(None, description="中文名")
    definition_file_name: Optional[str] = Field(None, description="表定义文档文件名")
    sql_file_name: Optional[str] = Field(None, description="SQL文件名")
    status: str = Field(..., description="匹配状态：matched/partial/unmatched")
    message: Optional[str] = Field(None, description="提示信息")


class BatchUploadPreview(BaseModel):
    """批量上传预览Schema"""
    items: List[BatchUploadItem] = Field(..., description="匹配项列表")
    total: int = Field(..., description="总数量")
    matched: int = Field(..., description="完全匹配数量（有文档和SQL）")
    partial: int = Field(..., description="部分匹配数量（只有文档或SQL）")
    unmatched: int = Field(..., description="未匹配数量")


class BatchUploadResult(BaseModel):
    """批量上传结果Schema"""
    success_count: int = Field(..., description="成功数量")
    failed_count: int = Field(..., description="失败数量")
    skipped_count: int = Field(..., description="跳过数量")
    details: List[dict] = Field(..., description="详细信息")


class CopyTemplateRequest(BaseModel):
    """复制数据模板请求Schema"""
    source_hospital_id: int = Field(..., description="源医疗机构ID")
    template_ids: List[int] = Field(..., description="要复制的数据模板ID列表")
    conflict_strategy: str = Field("skip", description="冲突处理策略：skip/overwrite")
    
    @field_validator('conflict_strategy')
    @classmethod
    def validate_conflict_strategy(cls, v: str) -> str:
        """验证冲突策略"""
        if v not in ['skip', 'overwrite']:
            raise ValueError("冲突策略必须是 skip 或 overwrite")
        return v


class CopyResult(BaseModel):
    """复制结果Schema"""
    success_count: int = Field(..., description="成功数量")
    skipped_count: int = Field(..., description="跳过数量")
    failed_count: int = Field(..., description="失败数量")
    details: List[dict] = Field(..., description="详细信息")


class HospitalSimple(BaseModel):
    """医疗机构简单信息Schema"""
    id: int
    code: str
    name: str
    
    class Config:
        from_attributes = True


class ExportTemplateRequest(BaseModel):
    """导出数据模板请求Schema"""
    template_ids: List[int] = Field(..., description="要导出的数据模板ID列表")
