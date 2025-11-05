"""
医疗机构服务
"""
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from fastapi import HTTPException, status

from app.models.hospital import Hospital
from app.models.user import User
from app.models.model_version import ModelVersion
from app.models.department import Department
from app.schemas.hospital import (
    HospitalCreate,
    HospitalUpdate,
    HospitalList,
)


class HospitalService:
    """医疗机构服务"""
    
    @staticmethod
    def get_hospital_by_id(db: Session, hospital_id: int) -> Optional[Hospital]:
        """
        根据ID获取医疗机构
        
        Args:
            db: 数据库会话
            hospital_id: 医疗机构ID
            
        Returns:
            医疗机构对象，如果不存在则返回None
        """
        return db.query(Hospital).filter(Hospital.id == hospital_id).first()
    
    @staticmethod
    def get_hospital_by_code(db: Session, code: str) -> Optional[Hospital]:
        """
        根据编码获取医疗机构
        
        Args:
            db: 数据库会话
            code: 医疗机构编码
            
        Returns:
            医疗机构对象，如果不存在则返回None
        """
        return db.query(Hospital).filter(Hospital.code == code.lower()).first()
    
    @staticmethod
    def get_hospitals(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
        is_active: Optional[bool] = None,
    ) -> HospitalList:
        """
        获取医疗机构列表
        
        Args:
            db: 数据库会话
            skip: 跳过记录数
            limit: 返回记录数
            search: 搜索关键词（搜索编码和名称）
            is_active: 是否启用过滤
            
        Returns:
            医疗机构列表
        """
        query = db.query(Hospital)
        
        # 搜索过滤
        if search:
            search_pattern = f"%{search}%"
            query = query.filter(
                or_(
                    Hospital.code.ilike(search_pattern),
                    Hospital.name.ilike(search_pattern)
                )
            )
        
        # 启用状态过滤
        if is_active is not None:
            query = query.filter(Hospital.is_active == is_active)
        
        # 获取总数
        total = query.count()
        
        # 分页查询
        items = query.order_by(Hospital.created_at.desc()).offset(skip).limit(limit).all()
        
        return HospitalList(total=total, items=items)
    
    @staticmethod
    def create_hospital(db: Session, hospital_create: HospitalCreate) -> Hospital:
        """
        创建医疗机构
        
        Args:
            db: 数据库会话
            hospital_create: 医疗机构创建数据
            
        Returns:
            创建的医疗机构对象
            
        Raises:
            HTTPException: 如果编码已存在
        """
        # 检查编码是否已存在
        existing = HospitalService.get_hospital_by_code(db, hospital_create.code)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"医疗机构编码 '{hospital_create.code}' 已存在"
            )
        
        # 创建医疗机构
        hospital = Hospital(
            code=hospital_create.code.lower(),
            name=hospital_create.name,
            is_active=hospital_create.is_active,
        )
        
        db.add(hospital)
        db.commit()
        db.refresh(hospital)
        
        return hospital
    
    @staticmethod
    def update_hospital(
        db: Session,
        hospital_id: int,
        hospital_update: HospitalUpdate
    ) -> Hospital:
        """
        更新医疗机构
        
        Args:
            db: 数据库会话
            hospital_id: 医疗机构ID
            hospital_update: 医疗机构更新数据
            
        Returns:
            更新后的医疗机构对象
            
        Raises:
            HTTPException: 如果医疗机构不存在
        """
        hospital = HospitalService.get_hospital_by_id(db, hospital_id)
        if not hospital:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"医疗机构 ID {hospital_id} 不存在"
            )
        
        # 更新字段（不允许修改code）
        update_data = hospital_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(hospital, field, value)
        
        db.commit()
        db.refresh(hospital)
        
        return hospital
    
    @staticmethod
    def delete_hospital(db: Session, hospital_id: int) -> None:
        """
        删除医疗机构
        
        Args:
            db: 数据库会话
            hospital_id: 医疗机构ID
            
        Raises:
            HTTPException: 如果医疗机构不存在或有关联数据
        """
        hospital = HospitalService.get_hospital_by_id(db, hospital_id)
        if not hospital:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"医疗机构 ID {hospital_id} 不存在"
            )
        
        # 检查是否有关联的用户
        user_count = db.query(func.count(User.id)).filter(User.hospital_id == hospital_id).scalar()
        if user_count > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"无法删除医疗机构，存在 {user_count} 个关联用户"
            )
        
        # 检查是否有关联的模型版本
        model_count = db.query(func.count(ModelVersion.id)).filter(
            ModelVersion.hospital_id == hospital_id
        ).scalar()
        if model_count > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"无法删除医疗机构，存在 {model_count} 个关联模型版本"
            )
        
        # 检查是否有关联的科室
        dept_count = db.query(func.count(Department.id)).filter(
            Department.hospital_id == hospital_id
        ).scalar()
        if dept_count > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"无法删除医疗机构，存在 {dept_count} 个关联科室"
            )
        
        # 删除医疗机构
        db.delete(hospital)
        db.commit()
    
    @staticmethod
    def get_accessible_hospitals(db: Session, user_id: int) -> List[Hospital]:
        """
        获取用户可访问的医疗机构列表
        
        Args:
            db: 数据库会话
            user_id: 用户ID
            
        Returns:
            医疗机构列表
        """
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return []
        
        # 如果用户是超级用户（hospital_id为空），返回所有启用的医疗机构
        if user.hospital_id is None:
            return db.query(Hospital).filter(Hospital.is_active == True).order_by(Hospital.name).all()
        
        # 如果用户绑定了医疗机构，只返回该医疗机构
        hospital = HospitalService.get_hospital_by_id(db, user.hospital_id)
        return [hospital] if hospital and hospital.is_active else []
    
    @staticmethod
    def can_user_access_hospital(db: Session, user_id: int, hospital_id: int) -> bool:
        """
        检查用户是否可以访问指定医疗机构
        
        Args:
            db: 数据库会话
            user_id: 用户ID
            hospital_id: 医疗机构ID
            
        Returns:
            是否可以访问
        """
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return False
        
        # 超级用户可以访问所有医疗机构
        if user.hospital_id is None:
            return True
        
        # 普通用户只能访问自己绑定的医疗机构
        return user.hospital_id == hospital_id
