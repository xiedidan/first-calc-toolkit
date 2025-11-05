"""
医疗机构数据隔离过滤器

提供自动添加hospital_id过滤条件的工具函数
"""
from typing import Optional, Type, TypeVar
from sqlalchemy.orm import Query
from fastapi import HTTPException, status

from app.middleware.hospital_context import get_current_hospital_id

T = TypeVar('T')


def apply_hospital_filter(query: Query, model: Type[T], required: bool = True) -> Query:
    """
    为查询自动添加医疗机构过滤条件
    
    Args:
        query: SQLAlchemy查询对象
        model: 模型类（必须有hospital_id字段）
        required: 是否要求必须有激活的医疗机构
        
    Returns:
        添加了hospital_id过滤条件的查询对象
        
    Raises:
        HTTPException: 如果required=True且未激活医疗机构
    """
    hospital_id = get_current_hospital_id()
    
    # 如果要求必须有医疗机构但未激活，抛出异常
    if required and hospital_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="请先激活医疗机构"
        )
    
    # 如果有激活的医疗机构，添加过滤条件
    if hospital_id is not None:
        if not hasattr(model, 'hospital_id'):
            raise ValueError(f"模型 {model.__name__} 没有 hospital_id 字段")
        query = query.filter(model.hospital_id == hospital_id)
    
    return query


def get_current_hospital_id_or_raise() -> int:
    """
    获取当前激活的医疗机构ID，如果未激活则抛出异常
    
    Returns:
        医疗机构ID
        
    Raises:
        HTTPException: 如果未激活医疗机构
    """
    hospital_id = get_current_hospital_id()
    if hospital_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="请先激活医疗机构"
        )
    return hospital_id


def validate_hospital_access(db, model_instance, hospital_id: Optional[int] = None) -> None:
    """
    验证数据是否属于当前激活的医疗机构
    
    Args:
        db: 数据库会话
        model_instance: 模型实例
        hospital_id: 医疗机构ID，如果为None则从上下文获取
        
    Raises:
        HTTPException: 如果数据不属于当前医疗机构
    """
    if hospital_id is None:
        hospital_id = get_current_hospital_id_or_raise()
    
    if not hasattr(model_instance, 'hospital_id'):
        raise ValueError(f"模型实例没有 hospital_id 字段")
    
    if model_instance.hospital_id != hospital_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="您没有权限访问该数据"
        )


def set_hospital_id_for_create(data_dict: dict, hospital_id: Optional[int] = None) -> dict:
    """
    为创建操作自动设置hospital_id
    
    Args:
        data_dict: 数据字典
        hospital_id: 医疗机构ID，如果为None则从上下文获取
        
    Returns:
        添加了hospital_id的数据字典
        
    Raises:
        HTTPException: 如果未激活医疗机构
    """
    if hospital_id is None:
        hospital_id = get_current_hospital_id_or_raise()
    
    data_dict['hospital_id'] = hospital_id
    return data_dict


def get_user_hospital_id(current_user) -> int:
    """
    从当前用户获取医疗机构ID
    
    Args:
        current_user: 当前用户对象
        
    Returns:
        医疗机构ID
        
    Raises:
        HTTPException: 如果用户未绑定医疗机构或未激活医疗机构
    """
    # 优先使用上下文中激活的医疗机构
    hospital_id = get_current_hospital_id()
    
    if hospital_id is not None:
        return hospital_id
    
    # 如果上下文中没有，尝试从用户对象获取
    if hasattr(current_user, 'hospital_id') and current_user.hospital_id:
        return current_user.hospital_id
    
    # 如果都没有，抛出异常
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="请先激活医疗机构"
    )
