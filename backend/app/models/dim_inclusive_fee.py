"""内含式收费模型"""
from sqlalchemy import Column, Integer, String, Numeric, DateTime, func
from app.database import Base


class DimInclusiveFee(Base):
    """内含式收费表"""
    __tablename__ = "dim_inclusive_fees"

    id = Column(Integer, primary_key=True, index=True)
    item_code = Column(String(255), nullable=False, unique=True, index=True, comment="收费项目代码")
    item_name = Column(String(255), nullable=True, comment="收费项目名称")
    cost = Column(Numeric(10, 2), nullable=False, comment="单位成本")
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<DimInclusiveFee(id={self.id}, item_code={self.item_code}, cost={self.cost})>"
