"""
数据源管理服务
"""
import time
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, text
from sqlalchemy.pool import NullPool
from fastapi import HTTPException

from app.models.data_source import DataSource
from app.schemas.data_source import (
    DataSourceCreate,
    DataSourceUpdate,
    DataSourceTestResult,
    DataSourcePoolStatus,
    ConnectionStatus,
    DBType,
)
from app.utils.encryption import encrypt_password, decrypt_password


class DataSourceConnectionManager:
    """数据源连接管理器"""
    
    def __init__(self):
        """初始化连接管理器"""
        self.pools: Dict[int, Any] = {}  # 存储所有数据源的连接池
    
    def _build_connection_string(self, data_source: DataSource, use_plain_password: bool = False) -> str:
        """
        构建数据库连接字符串
        
        Args:
            data_source: 数据源对象
            use_plain_password: 是否使用明文密码（用于测试连接时）
            
        Returns:
            连接字符串
        """
        # 解密密码（如果不是明文）
        if use_plain_password:
            password = data_source.password
        else:
            password = decrypt_password(data_source.password)
        
        # 根据数据库类型构建连接字符串
        if data_source.db_type == DBType.POSTGRESQL:
            conn_str = f"postgresql://{data_source.username}:{password}@{data_source.host}:{data_source.port}/{data_source.database_name}"
            if data_source.schema_name:
                conn_str += f"?options=-csearch_path%3D{data_source.schema_name}"
        elif data_source.db_type == DBType.MYSQL:
            conn_str = f"mysql+pymysql://{data_source.username}:{password}@{data_source.host}:{data_source.port}/{data_source.database_name}"
        elif data_source.db_type == DBType.SQLSERVER:
            conn_str = f"mssql+pyodbc://{data_source.username}:{password}@{data_source.host}:{data_source.port}/{data_source.database_name}?driver=ODBC+Driver+17+for+SQL+Server"
        elif data_source.db_type == DBType.ORACLE:
            conn_str = f"oracle+cx_oracle://{data_source.username}:{password}@{data_source.host}:{data_source.port}/{data_source.database_name}"
        else:
            raise ValueError(f"不支持的数据库类型: {data_source.db_type}")
        
        return conn_str
    
    def create_pool(self, data_source: DataSource) -> Any:
        """
        为数据源创建连接池
        
        Args:
            data_source: 数据源对象
            
        Returns:
            SQLAlchemy Engine对象
        """
        conn_str = self._build_connection_string(data_source)
        
        engine = create_engine(
            conn_str,
            pool_size=data_source.pool_size_min,
            max_overflow=data_source.pool_size_max - data_source.pool_size_min,
            pool_timeout=data_source.pool_timeout,
            pool_recycle=3600,  # 1小时回收连接
            pool_pre_ping=True,  # 连接前测试
            echo=False,
        )
        
        self.pools[data_source.id] = engine
        return engine
    
    def get_pool(self, data_source_id: int) -> Optional[Any]:
        """
        获取指定数据源的连接池
        
        Args:
            data_source_id: 数据源ID
            
        Returns:
            SQLAlchemy Engine对象，如果不存在则返回None
        """
        return self.pools.get(data_source_id)
    
    def close_pool(self, data_source_id: int):
        """
        关闭并清理连接池
        
        Args:
            data_source_id: 数据源ID
        """
        if data_source_id in self.pools:
            engine = self.pools[data_source_id]
            engine.dispose()
            del self.pools[data_source_id]
    
    def test_connection(self, data_source: DataSource, use_plain_password: bool = False) -> DataSourceTestResult:
        """
        测试数据源连接
        
        Args:
            data_source: 数据源对象
            use_plain_password: 是否使用明文密码（用于测试连接时）
            
        Returns:
            测试结果
        """
        start_time = time.time()
        
        try:
            # 构建连接字符串
            conn_str = self._build_connection_string(data_source, use_plain_password=use_plain_password)
            
            # 创建临时引擎（不使用连接池）
            engine = create_engine(conn_str, poolclass=NullPool)
            
            # 尝试连接并执行简单查询
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            
            # 关闭引擎
            engine.dispose()
            
            duration_ms = int((time.time() - start_time) * 1000)
            
            return DataSourceTestResult(
                success=True,
                message="连接成功",
                duration_ms=duration_ms
            )
        except Exception as e:
            duration_ms = int((time.time() - start_time) * 1000)
            return DataSourceTestResult(
                success=False,
                message="连接失败",
                duration_ms=duration_ms,
                error=str(e)
            )
    
    def get_pool_status(self, data_source_id: int) -> Optional[DataSourcePoolStatus]:
        """
        获取连接池状态
        
        Args:
            data_source_id: 数据源ID
            
        Returns:
            连接池状态，如果连接池不存在则返回None
        """
        engine = self.get_pool(data_source_id)
        if not engine:
            return None
        
        pool = engine.pool
        
        return DataSourcePoolStatus(
            pool_size=pool.size(),
            active_connections=pool.checkedout(),
            idle_connections=pool.size() - pool.checkedout(),
            waiting_requests=pool.overflow(),
            total_connections_created=pool.size(),
            total_connections_closed=0,  # SQLAlchemy不直接提供此信息
        )


# 全局连接管理器实例
connection_manager = DataSourceConnectionManager()


class DataSourceService:
    """数据源服务"""
    
    @staticmethod
    def create_data_source(db: Session, data_source_in: DataSourceCreate) -> DataSource:
        """
        创建数据源
        
        Args:
            db: 数据库会话
            data_source_in: 数据源创建数据
            
        Returns:
            创建的数据源对象
        """
        # 检查名称是否已存在
        existing = db.query(DataSource).filter(DataSource.name == data_source_in.name).first()
        if existing:
            raise HTTPException(status_code=400, detail="数据源名称已存在")
        
        # 如果设置为默认数据源，取消其他数据源的默认标记
        if data_source_in.is_default:
            db.query(DataSource).filter(DataSource.is_default == True).update({"is_default": False})
        
        # 加密密码
        encrypted_password = encrypt_password(data_source_in.password)
        
        # 创建数据源
        data_source = DataSource(
            **data_source_in.model_dump(exclude={"password"}),
            password=encrypted_password
        )
        
        db.add(data_source)
        db.commit()
        db.refresh(data_source)
        
        # 如果启用，创建连接池
        if data_source.is_enabled:
            try:
                connection_manager.create_pool(data_source)
            except Exception as e:
                print(f"创建连接池失败: {str(e)}")
        
        return data_source
    
    @staticmethod
    def get_data_source(db: Session, data_source_id: int) -> Optional[DataSource]:
        """
        获取数据源
        
        Args:
            db: 数据库会话
            data_source_id: 数据源ID
            
        Returns:
            数据源对象，如果不存在则返回None
        """
        return db.query(DataSource).filter(DataSource.id == data_source_id).first()
    
    @staticmethod
    def get_data_sources(
        db: Session,
        skip: int = 0,
        limit: int = 10,
        keyword: Optional[str] = None,
        db_type: Optional[str] = None,
        is_enabled: Optional[bool] = None,
    ) -> tuple[List[DataSource], int]:
        """
        获取数据源列表
        
        Args:
            db: 数据库会话
            skip: 跳过数量
            limit: 限制数量
            keyword: 搜索关键词
            db_type: 数据库类型筛选
            is_enabled: 启用状态筛选
            
        Returns:
            (数据源列表, 总数量)
        """
        query = db.query(DataSource)
        
        # 关键词搜索
        if keyword:
            query = query.filter(DataSource.name.ilike(f"%{keyword}%"))
        
        # 数据库类型筛选
        if db_type:
            query = query.filter(DataSource.db_type == db_type)
        
        # 启用状态筛选
        if is_enabled is not None:
            query = query.filter(DataSource.is_enabled == is_enabled)
        
        total = query.count()
        data_sources = query.offset(skip).limit(limit).all()
        
        return data_sources, total
    
    @staticmethod
    def update_data_source(
        db: Session,
        data_source_id: int,
        data_source_in: DataSourceUpdate
    ) -> Optional[DataSource]:
        """
        更新数据源
        
        Args:
            db: 数据库会话
            data_source_id: 数据源ID
            data_source_in: 数据源更新数据
            
        Returns:
            更新后的数据源对象，如果不存在则返回None
        """
        data_source = db.query(DataSource).filter(DataSource.id == data_source_id).first()
        if not data_source:
            return None
        
        # 检查名称是否与其他数据源冲突
        if data_source_in.name and data_source_in.name != data_source.name:
            existing = db.query(DataSource).filter(
                DataSource.name == data_source_in.name,
                DataSource.id != data_source_id
            ).first()
            if existing:
                raise HTTPException(status_code=400, detail="数据源名称已存在")
        
        # 更新字段
        update_data = data_source_in.model_dump(exclude_unset=True)
        
        # 如果更新了密码，需要加密
        if "password" in update_data and update_data["password"]:
            update_data["password"] = encrypt_password(update_data["password"])
        
        for field, value in update_data.items():
            setattr(data_source, field, value)
        
        db.commit()
        db.refresh(data_source)
        
        # 如果更新了连接配置，重新创建连接池
        if data_source.is_enabled:
            connection_manager.close_pool(data_source_id)
            try:
                connection_manager.create_pool(data_source)
            except Exception as e:
                print(f"重新创建连接池失败: {str(e)}")
        
        return data_source
    
    @staticmethod
    def delete_data_source(db: Session, data_source_id: int) -> bool:
        """
        删除数据源
        
        Args:
            db: 数据库会话
            data_source_id: 数据源ID
            
        Returns:
            是否删除成功
        """
        data_source = db.query(DataSource).filter(DataSource.id == data_source_id).first()
        if not data_source:
            return False
        
        # 检查是否被计算步骤引用
        from app.models.calculation_step import CalculationStep
        step_count = db.query(CalculationStep).filter(
            CalculationStep.data_source_id == data_source_id
        ).count()
        
        if step_count > 0:
            raise HTTPException(
                status_code=400,
                detail=f"数据源被 {step_count} 个计算步骤引用，无法删除"
            )
        
        # 关闭连接池
        connection_manager.close_pool(data_source_id)
        
        # 删除数据源
        db.delete(data_source)
        db.commit()
        
        return True
    
    @staticmethod
    def toggle_data_source(db: Session, data_source_id: int) -> Optional[DataSource]:
        """
        切换数据源启用状态
        
        Args:
            db: 数据库会话
            data_source_id: 数据源ID
            
        Returns:
            更新后的数据源对象，如果不存在则返回None
        """
        data_source = db.query(DataSource).filter(DataSource.id == data_source_id).first()
        if not data_source:
            return None
        
        # 切换状态
        data_source.is_enabled = not data_source.is_enabled
        db.commit()
        db.refresh(data_source)
        
        # 根据状态创建或关闭连接池
        if data_source.is_enabled:
            try:
                connection_manager.create_pool(data_source)
            except Exception as e:
                print(f"创建连接池失败: {str(e)}")
        else:
            connection_manager.close_pool(data_source_id)
        
        return data_source
    
    @staticmethod
    def set_default_data_source(db: Session, data_source_id: int) -> bool:
        """
        设置为默认数据源
        
        Args:
            db: 数据库会话
            data_source_id: 数据源ID
            
        Returns:
            是否设置成功
        """
        data_source = db.query(DataSource).filter(DataSource.id == data_source_id).first()
        if not data_source:
            return False
        
        # 取消其他数据源的默认标记
        db.query(DataSource).filter(DataSource.is_default == True).update({"is_default": False})
        
        # 设置为默认
        data_source.is_default = True
        db.commit()
        
        return True
    
    @staticmethod
    def get_default_data_source(db: Session) -> Optional[DataSource]:
        """
        获取默认数据源
        
        Args:
            db: 数据库会话
            
        Returns:
            默认数据源对象，如果不存在则返回None
        """
        return db.query(DataSource).filter(DataSource.is_default == True).first()
    
    @staticmethod
    def get_connection_status(data_source: DataSource) -> ConnectionStatus:
        """
        获取数据源连接状态
        
        Args:
            data_source: 数据源对象
            
        Returns:
            连接状态
        """
        if not data_source.is_enabled:
            return ConnectionStatus.OFFLINE
        
        pool = connection_manager.get_pool(data_source.id)
        if not pool:
            return ConnectionStatus.OFFLINE
        
        # 尝试测试连接
        result = connection_manager.test_connection(data_source)
        if result.success:
            return ConnectionStatus.ONLINE
        else:
            return ConnectionStatus.ERROR
