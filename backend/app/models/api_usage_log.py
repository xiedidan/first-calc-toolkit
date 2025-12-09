"""
API使用日志模型
"""
from datetime import datetime
from sqlalchemy import Column, Integer, Float, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.database import Base


class APIUsageLog(Base):
    """API使用日志模型"""
    __tablename__ = "api_usage_logs"

    id = Column(Integer, primary_key=True, index=True, comment="主键")
    hospital_id = Column(Integer, ForeignKey("hospitals.id", ondelete="CASCADE"), nullable=False, index=True, comment="医疗机构ID")
    task_id = Column(Integer, ForeignKey("classification_tasks.id", ondelete="CASCADE"), nullable=False, index=True, comment="分类任务ID")
    charge_item_id = Column(Integer, ForeignKey("charge_items.id", ondelete="CASCADE"), nullable=False, comment="收费项目ID")
    request_data = Column(JSON, nullable=True, comment="请求数据")
    response_data = Column(JSON, nullable=True, comment="响应数据")
    status_code = Column(Integer, nullable=True, comment="HTTP状态码")
    error_message = Column(Text, nullable=True, comment="错误信息")
    call_duration = Column(Float, nullable=True, comment="调用耗时（秒）")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True, comment="创建时间")

    # 关系
    hospital = relationship("Hospital")
    task = relationship("ClassificationTask")
    charge_item = relationship("ChargeItem")
