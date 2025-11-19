"""
数据源模型
"""
from sqlalchemy import Column, Integer, String, Boolean, Text, TIMESTAMP, JSON
from sqlalchemy.sql import func
from app.database import Base


class DataSource(Base):
    """数据源配置表"""
    __tablename__ = "data_sources"

    id = Column(Integer, primary_key=True, index=True, comment="主键")
    name = Column(String(100), unique=True, nullable=False, comment="数据源名称")
    db_type = Column(String(20), nullable=False, comment="数据库类型")
    host = Column(String(255), nullable=False, comment="主机地址")
    port = Column(Integer, nullable=False, comment="端口号")
    database_name = Column(String(100), nullable=False, comment="数据库名称")
    username = Column(String(100), nullable=False, comment="用户名")
    password = Column(Text, nullable=False, comment="密码（加密存储）")
    schema_name = Column(String(100), nullable=True, comment="Schema名称")
    connection_params = Column(JSON, nullable=True, comment="额外连接参数")
    is_default = Column(Boolean, default=False, nullable=False, comment="是否默认数据源")
    is_enabled = Column(Boolean, default=True, nullable=False, comment="是否启用")
    description = Column(Text, nullable=True, comment="描述")
    pool_size_min = Column(Integer, default=2, nullable=False, comment="连接池最小连接数")
    pool_size_max = Column(Integer, default=10, nullable=False, comment="连接池最大连接数")
    pool_timeout = Column(Integer, default=30, nullable=False, comment="连接超时时间(秒)")
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False, comment="创建时间")
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now(), nullable=False, comment="更新时间")
