"""
医疗机构上下文中间件

用于管理当前激活的医疗机构ID，支持从请求头或会话中获取
"""
from typing import Optional
from contextvars import ContextVar
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from fastapi import HTTPException, status

# 使用ContextVar存储当前请求的医疗机构ID
_current_hospital_id: ContextVar[Optional[int]] = ContextVar("current_hospital_id", default=None)


class HospitalContextMiddleware(BaseHTTPMiddleware):
    """
    医疗机构上下文中间件
    
    从请求头 X-Hospital-ID 中获取当前激活的医疗机构ID，
    并将其存储到上下文变量中供后续使用
    """
    
    async def dispatch(self, request: Request, call_next):
        """
        处理请求，提取医疗机构ID
        
        Args:
            request: 请求对象
            call_next: 下一个中间件或路由处理器
            
        Returns:
            响应对象
        """
        # 从请求头中获取医疗机构ID
        hospital_id_str = request.headers.get("X-Hospital-ID")
        
        hospital_id = None
        if hospital_id_str:
            try:
                hospital_id = int(hospital_id_str)
            except (ValueError, TypeError):
                # 如果转换失败，忽略该值
                pass
        
        # 设置到上下文变量
        token = _current_hospital_id.set(hospital_id)
        
        try:
            response = await call_next(request)
            return response
        finally:
            # 清理上下文变量
            _current_hospital_id.reset(token)


def get_current_hospital_id() -> Optional[int]:
    """
    获取当前请求的医疗机构ID
    
    Returns:
        医疗机构ID，如果未设置则返回None
    """
    return _current_hospital_id.get()


def require_hospital_id() -> int:
    """
    获取当前请求的医疗机构ID，如果未设置则抛出异常
    
    Returns:
        医疗机构ID
        
    Raises:
        HTTPException: 如果未激活医疗机构
    """
    hospital_id = _current_hospital_id.get()
    if hospital_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="请先激活医疗机构"
        )
    return hospital_id


def set_current_hospital_id(hospital_id: Optional[int]) -> None:
    """
    设置当前请求的医疗机构ID
    
    Args:
        hospital_id: 医疗机构ID
    """
    _current_hospital_id.set(hospital_id)
