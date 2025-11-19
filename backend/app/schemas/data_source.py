"""
数据源相关的Pydantic模型
"""
from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, field_validator
from enum import Enum


class DBType(str, Enum):
    """数据库类型枚举"""
    POSTGRESQL = "postgresql"
    MYSQL = "mysql"
    SQLSERVER = "sqlserver"
    ORACLE = "oracle"


class ConnectionStatus(str, Enum):
    """连接状态枚举"""
    ONLINE = "online"
    OFFLINE = "offline"
    ERROR = "error"


class DataSourceBase(BaseModel):
    """数据源基础模型"""
    name: str = Field(..., max_length=100, description="数据源名称")
    db_type: DBType = Field(..., description="数据库类型")
    host: str = Field(..., max_length=255, description="主机地址")
    port: int = Field(..., gt=0, lt=65536, description="端口号")
    database_name: str = Field(..., max_length=100, description="数据库名称")
    username: str = Field(..., max_length=100, description="用户名")
    schema_name: Optional[str] = Field(None, max_length=100, description="Schema名称")
    connection_params: Optional[Dict[str, Any]] = Field(None, description="额外连接参数")
    is_default: bool = Field(False, description="是否默认数据源")
    is_enabled: bool = Field(True, description="是否启用")
    description: Optional[str] = Field(None, description="描述")
    pool_size_min: int = Field(2, ge=1, le=100, description="连接池最小连接数")
    pool_size_max: int = Field(10, ge=1, le=100, description="连接池最大连接数")
    pool_timeout: int = Field(30, ge=1, le=300, description="连接超时时间(秒)")

    @field_validator('pool_size_max')
    @classmethod
    def validate_pool_size(cls, v, info):
        """验证最大连接数必须大于等于最小连接数"""
        if 'pool_size_min' in info.data and v < info.data['pool_size_min']:
            raise ValueError('pool_size_max must be greater than or equal to pool_size_min')
        return v


class DataSourceCreate(DataSourceBase):
    """创建数据源"""
    password: str = Field(..., min_length=1, description="密码")


class DataSourceUpdate(BaseModel):
    """更新数据源"""
    name: Optional[str] = Field(None, max_length=100, description="数据源名称")
    host: Optional[str] = Field(None, max_length=255, description="主机地址")
    port: Optional[int] = Field(None, gt=0, lt=65536, description="端口号")
    database_name: Optional[str] = Field(None, max_length=100, description="数据库名称")
    username: Optional[str] = Field(None, max_length=100, description="用户名")
    password: Optional[str] = Field(None, min_length=1, description="密码（如果不修改则不传）")
    schema_name: Optional[str] = Field(None, max_length=100, description="Schema名称")
    connection_params: Optional[Dict[str, Any]] = Field(None, description="额外连接参数")
    description: Optional[str] = Field(None, description="描述")
    pool_size_min: Optional[int] = Field(None, ge=1, le=100, description="连接池最小连接数")
    pool_size_max: Optional[int] = Field(None, ge=1, le=100, description="连接池最大连接数")
    pool_timeout: Optional[int] = Field(None, ge=1, le=300, description="连接超时时间(秒)")


class DataSourceInDB(DataSourceBase):
    """数据库中的数据源（包含加密密码）"""
    id: int
    password: str  # 加密后的密码
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class DataSourceResponse(BaseModel):
    """数据源响应模型（密码脱敏）"""
    id: int
    name: str
    db_type: DBType
    host: str
    port: int
    database_name: str
    username: str
    password: str = Field(default="***", description="密码（脱敏显示）")
    schema_name: Optional[str] = None
    connection_params: Optional[Dict[str, Any]] = None
    is_default: bool
    is_enabled: bool
    description: Optional[str] = None
    pool_size_min: int
    pool_size_max: int
    pool_timeout: int
    connection_status: Optional[ConnectionStatus] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class DataSourceListItem(BaseModel):
    """数据源列表项"""
    id: int
    name: str
    db_type: DBType
    host: str
    port: int
    database_name: str
    username: str
    is_default: bool
    is_enabled: bool
    connection_status: Optional[ConnectionStatus] = None
    description: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class DataSourceTestResult(BaseModel):
    """数据源测试结果"""
    success: bool
    message: str
    duration_ms: Optional[int] = None
    error: Optional[str] = None


class DataSourcePoolStatus(BaseModel):
    """连接池状态"""
    pool_size: int
    active_connections: int
    idle_connections: int
    waiting_requests: int
    total_connections_created: int
    total_connections_closed: int
