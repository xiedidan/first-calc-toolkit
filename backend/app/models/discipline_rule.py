"""
学科规则模型
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Numeric, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.database import Base


class DisciplineRule(Base):
    """学科规则模型 - 给某科室的某维度增加系数"""
    __tablename__ = "discipline_rules"
    __table_args__ = (
        UniqueConstraint(
            'hospital_id', 'version_id', 'department_code', 'dimension_code',
            name='uq_discipline_rule_version_dept_dim'
        ),
        {'comment': '学科规则表'},
    )

    id = Column(Integer, primary_key=True, index=True)
    hospital_id = Column(
        Integer,
        ForeignKey("hospitals.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="所属医疗机构ID"
    )
    version_id = Column(
        Integer,
        ForeignKey("model_versions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="模型版本ID"
    )
    department_code = Column(String(50), nullable=False, index=True, comment="科室代码")
    department_name = Column(String(100), nullable=False, comment="科室名称")
    dimension_code = Column(String(100), nullable=False, index=True, comment="维度代码")
    dimension_name = Column(String(200), nullable=False, comment="维度名称")
    rule_description = Column(String(500), nullable=True, comment="规则描述")
    rule_coefficient = Column(Numeric(10, 4), nullable=False, default=1.0, comment="规则系数")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # 关系
    hospital = relationship("Hospital", back_populates="discipline_rules")
    version = relationship("ModelVersion", back_populates="discipline_rules")
