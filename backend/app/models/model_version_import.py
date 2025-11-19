"""
模型版本导入记录模型
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from app.database import Base


class ModelVersionImport(Base):
    """模型版本导入记录模型"""
    __tablename__ = "model_version_imports"

    id = Column(Integer, primary_key=True, index=True)
    target_version_id = Column(Integer, ForeignKey("model_versions.id", ondelete="CASCADE"), nullable=False, index=True, comment="目标版本ID（导入后创建的新版本）")
    source_version_id = Column(Integer, ForeignKey("model_versions.id", ondelete="CASCADE"), nullable=False, index=True, comment="源版本ID")
    source_hospital_id = Column(Integer, ForeignKey("hospitals.id", ondelete="CASCADE"), nullable=False, comment="源医疗机构ID")
    import_type = Column(String(50), nullable=False, comment="导入类型（structure_only/with_workflows）")
    imported_by = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, comment="导入用户ID")
    import_time = Column(DateTime, default=datetime.utcnow, nullable=False, comment="导入时间")
    statistics = Column(JSONB, comment="导入统计信息（JSON格式）")

    # 关系
    target_version = relationship("ModelVersion", foreign_keys=[target_version_id], backref="import_record")
    source_version = relationship("ModelVersion", foreign_keys=[source_version_id])
    source_hospital = relationship("Hospital", foreign_keys=[source_hospital_id])
    importer = relationship("User", foreign_keys=[imported_by])
