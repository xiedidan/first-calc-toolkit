"""
数据库连接配置
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.config import settings

# 创建数据库引擎
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_size=10,  # 增加连接池大小
    max_overflow=20,  # 增加最大溢出连接数
    pool_recycle=1800,  # 30分钟回收连接
    pool_timeout=60,  # 连接超时60秒
    connect_args={
        "connect_timeout": 10,  # 连接超时10秒
    }
)

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建基类
Base = declarative_base()


def get_db():
    """获取数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
