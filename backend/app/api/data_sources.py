"""
数据源管理API路由
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.models.data_source import DataSource
from app.schemas.data_source import (
    DataSourceCreate,
    DataSourceUpdate,
    DataSourceResponse,
    DataSourceListItem,
    DataSourceTestResult,
    DataSourcePoolStatus,
    ConnectionStatus,
)
from app.services.data_source_service import (
    DataSourceService,
    connection_manager,
)

router = APIRouter()


@router.get("", response_model=dict)
def get_data_sources(
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(10, ge=1, le=1000, description="每页数量"),
    keyword: Optional[str] = Query(None, description="搜索关键词"),
    db_type: Optional[str] = Query(None, description="数据库类型筛选"),
    is_enabled: Optional[bool] = Query(None, description="启用状态筛选"),
    db: Session = Depends(get_db),
):
    """获取数据源列表"""
    skip = (page - 1) * size
    data_sources, total = DataSourceService.get_data_sources(
        db=db,
        skip=skip,
        limit=size,
        keyword=keyword,
        db_type=db_type,
        is_enabled=is_enabled,
    )
    
    # 转换为响应模型并添加连接状态
    items = []
    for ds in data_sources:
        item = DataSourceListItem.model_validate(ds)
        item.connection_status = DataSourceService.get_connection_status(ds)
        items.append(item)
    
    return {
        "code": 200,
        "message": "success",
        "data": {
            "total": total,
            "items": items,
        }
    }


@router.post("", response_model=dict)
def create_data_source(
    data_source_in: DataSourceCreate,
    db: Session = Depends(get_db),
):
    """创建新数据源"""
    data_source = DataSourceService.create_data_source(db=db, data_source_in=data_source_in)
    
    response = DataSourceResponse.model_validate(data_source)
    response.password = "***"  # 脱敏
    
    return {
        "code": 200,
        "message": "创建成功",
        "data": response,
    }


@router.get("/{data_source_id}", response_model=dict)
def get_data_source(
    data_source_id: int,
    db: Session = Depends(get_db),
):
    """获取数据源详情"""
    data_source = DataSourceService.get_data_source(db=db, data_source_id=data_source_id)
    if not data_source:
        raise HTTPException(status_code=404, detail="数据源不存在")
    
    response = DataSourceResponse.model_validate(data_source)
    response.password = "***"  # 脱敏
    response.connection_status = DataSourceService.get_connection_status(data_source)
    
    return {
        "code": 200,
        "message": "success",
        "data": response,
    }


@router.put("/{data_source_id}", response_model=dict)
def update_data_source(
    data_source_id: int,
    data_source_in: DataSourceUpdate,
    db: Session = Depends(get_db),
):
    """更新数据源信息"""
    data_source = DataSourceService.update_data_source(
        db=db,
        data_source_id=data_source_id,
        data_source_in=data_source_in,
    )
    if not data_source:
        raise HTTPException(status_code=404, detail="数据源不存在")
    
    response = DataSourceResponse.model_validate(data_source)
    response.password = "***"  # 脱敏
    
    return {
        "code": 200,
        "message": "更新成功",
        "data": response,
    }


@router.delete("/{data_source_id}", response_model=dict)
def delete_data_source(
    data_source_id: int,
    db: Session = Depends(get_db),
):
    """删除数据源"""
    success = DataSourceService.delete_data_source(db=db, data_source_id=data_source_id)
    if not success:
        raise HTTPException(status_code=404, detail="数据源不存在")
    
    return {
        "code": 200,
        "message": "删除成功",
        "data": None,
    }


@router.post("/test-connection", response_model=dict)
def test_connection_with_config(
    config: DataSourceCreate,
):
    """使用配置信息测试数据源连接（不保存到数据库）"""
    # 创建临时数据源对象用于测试
    temp_data_source = DataSource(
        name=config.name,
        db_type=config.db_type,
        host=config.host,
        port=config.port,
        database_name=config.database_name,
        username=config.username,
        password=config.password,  # 明文密码
        schema_name=config.schema_name,
        pool_size_min=config.pool_size_min,
        pool_size_max=config.pool_size_max,
        pool_timeout=config.pool_timeout,
    )
    
    # 使用明文密码测试连接
    result = connection_manager.test_connection(temp_data_source, use_plain_password=True)
    
    return {
        "code": 200,
        "message": "success",
        "data": result,
    }


@router.post("/{data_source_id}/test", response_model=dict)
def test_data_source(
    data_source_id: int,
    db: Session = Depends(get_db),
):
    """测试数据源连接"""
    data_source = DataSourceService.get_data_source(db=db, data_source_id=data_source_id)
    if not data_source:
        raise HTTPException(status_code=404, detail="数据源不存在")
    
    result = connection_manager.test_connection(data_source)
    
    return {
        "code": 200,
        "message": "success",
        "data": result,
    }


@router.put("/{data_source_id}/toggle", response_model=dict)
def toggle_data_source(
    data_source_id: int,
    db: Session = Depends(get_db),
):
    """切换数据源启用状态"""
    data_source = DataSourceService.toggle_data_source(db=db, data_source_id=data_source_id)
    if not data_source:
        raise HTTPException(status_code=404, detail="数据源不存在")
    
    return {
        "code": 200,
        "message": "状态切换成功",
        "data": {
            "is_enabled": data_source.is_enabled,
        }
    }


@router.put("/{data_source_id}/set-default", response_model=dict)
def set_default_data_source(
    data_source_id: int,
    db: Session = Depends(get_db),
):
    """设置为默认数据源"""
    success = DataSourceService.set_default_data_source(db=db, data_source_id=data_source_id)
    if not success:
        raise HTTPException(status_code=404, detail="数据源不存在")
    
    return {
        "code": 200,
        "message": "设置成功",
        "data": {
            "success": True,
            "message": "已设置为默认数据源",
        }
    }


@router.get("/{data_source_id}/pool-status", response_model=dict)
def get_pool_status(
    data_source_id: int,
    db: Session = Depends(get_db),
):
    """获取连接池状态"""
    data_source = DataSourceService.get_data_source(db=db, data_source_id=data_source_id)
    if not data_source:
        raise HTTPException(status_code=404, detail="数据源不存在")
    
    if not data_source.is_enabled:
        raise HTTPException(status_code=400, detail="数据源未启用")
    
    status = connection_manager.get_pool_status(data_source_id)
    if not status:
        raise HTTPException(status_code=400, detail="连接池不存在")
    
    return {
        "code": 200,
        "message": "success",
        "data": status,
    }
