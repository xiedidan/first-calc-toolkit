"""
时区处理工具

统一使用UTC时间存储，前端显示时转换为本地时间（UTC+8）
"""
from datetime import datetime, timezone, timedelta

# 中国时区 (UTC+8)
CHINA_TZ = timezone(timedelta(hours=8))


def utc_now() -> datetime:
    """获取当前UTC时间（无时区信息，用于数据库存储）"""
    return datetime.utcnow()


def china_now() -> datetime:
    """获取当前中国时间（UTC+8，带时区信息）"""
    return datetime.now(CHINA_TZ)


def utc_to_china(dt: datetime) -> datetime:
    """将UTC时间转换为中国时间
    
    Args:
        dt: UTC时间（可以有或没有时区信息）
    
    Returns:
        中国时间（UTC+8）
    """
    if dt is None:
        return None
    
    # 如果没有时区信息，假设是UTC
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    
    return dt.astimezone(CHINA_TZ)


def china_to_utc(dt: datetime) -> datetime:
    """将中国时间转换为UTC时间
    
    Args:
        dt: 中国时间（可以有或没有时区信息）
    
    Returns:
        UTC时间（无时区信息，用于数据库存储）
    """
    if dt is None:
        return None
    
    # 如果没有时区信息，假设是中国时间
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=CHINA_TZ)
    
    return dt.astimezone(timezone.utc).replace(tzinfo=None)


def format_china_time(dt: datetime, fmt: str = "%Y-%m-%d %H:%M:%S") -> str:
    """将UTC时间格式化为中国时间字符串
    
    Args:
        dt: UTC时间
        fmt: 格式字符串
    
    Returns:
        格式化的中国时间字符串
    """
    if dt is None:
        return ""
    
    china_dt = utc_to_china(dt)
    return china_dt.strftime(fmt)
