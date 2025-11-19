"""
医疗机构管理API
"""
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api import deps
from app.services.hospital_service import HospitalService
from app.schemas.hospital import (
    Hospital as HospitalSchema,
    HospitalCreate,
    HospitalUpdate,
    HospitalList,
    HospitalActivate,
)

router = APIRouter()


@router.get("", response_model=HospitalList)
def get_hospitals(
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_current_user),
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(10, ge=1, le=100, description="每页数量"),
    search: Optional[str] = Query(None, description="搜索关键词（编码或名称）"),
    is_active: Optional[bool] = Query(None, description="是否启用"),
):
    """
    获取医疗机构列表
    
    仅系统管理员可访问
    """
    # TODO: 添加管理员权限检查
    # if not deps.is_admin(current_user):
    #     raise HTTPException(
    #         status_code=status.HTTP_403_FORBIDDEN,
    #         detail="仅系统管理员可访问"
    #     )
    
    skip = (page - 1) * size
    return HospitalService.get_hospitals(
        db=db,
        skip=skip,
        limit=size,
        search=search,
        is_active=is_active,
    )


@router.post("", response_model=HospitalSchema, status_code=status.HTTP_201_CREATED)
def create_hospital(
    hospital_in: HospitalCreate,
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_current_user),
):
    """
    创建医疗机构
    
    仅系统管理员可访问
    """
    # TODO: 添加管理员权限检查
    # if not deps.is_admin(current_user):
    #     raise HTTPException(
    #         status_code=status.HTTP_403_FORBIDDEN,
    #         detail="仅系统管理员可访问"
    #     )
    
    return HospitalService.create_hospital(db=db, hospital_create=hospital_in)


@router.get("/accessible", response_model=List[HospitalSchema])
def get_accessible_hospitals(
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_current_user),
):
    """
    获取当前用户可访问的医疗机构列表
    
    - 超级用户：返回所有启用的医疗机构
    - 普通用户：返回用户绑定的医疗机构
    """
    return HospitalService.get_accessible_hospitals(db=db, user_id=current_user.id)


@router.get("/{hospital_id}", response_model=HospitalSchema)
def get_hospital(
    hospital_id: int,
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_current_user),
):
    """
    获取医疗机构详情
    
    仅系统管理员可访问
    """
    # TODO: 添加管理员权限检查
    # if not deps.is_admin(current_user):
    #     raise HTTPException(
    #         status_code=status.HTTP_403_FORBIDDEN,
    #         detail="仅系统管理员可访问"
    #     )
    
    hospital = HospitalService.get_hospital_by_id(db=db, hospital_id=hospital_id)
    if not hospital:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"医疗机构 ID {hospital_id} 不存在"
        )
    
    return hospital


@router.put("/{hospital_id}", response_model=HospitalSchema)
def update_hospital(
    hospital_id: int,
    hospital_in: HospitalUpdate,
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_current_user),
):
    """
    更新医疗机构
    
    仅系统管理员可访问
    注意：不允许修改医疗机构编码
    """
    # TODO: 添加管理员权限检查
    # if not deps.is_admin(current_user):
    #     raise HTTPException(
    #         status_code=status.HTTP_403_FORBIDDEN,
    #         detail="仅系统管理员可访问"
    #     )
    
    return HospitalService.update_hospital(
        db=db,
        hospital_id=hospital_id,
        hospital_update=hospital_in
    )


@router.delete("/{hospital_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_hospital(
    hospital_id: int,
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_current_user),
):
    """
    删除医疗机构
    
    仅系统管理员可访问
    如果医疗机构有关联数据（用户、模型、科室等），将拒绝删除
    """
    # TODO: 添加管理员权限检查
    # if not deps.is_admin(current_user):
    #     raise HTTPException(
    #         status_code=status.HTTP_403_FORBIDDEN,
    #         detail="仅系统管理员可访问"
    #     )
    
    HospitalService.delete_hospital(db=db, hospital_id=hospital_id)


@router.post("/{hospital_id}/activate", response_model=HospitalActivate)
def activate_hospital(
    hospital_id: int,
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_current_user),
):
    """
    激活医疗机构
    
    将指定的医疗机构设置为当前用户的激活机构
    用户只能激活自己有权访问的医疗机构
    
    注意：前端需要在后续请求中通过 X-Hospital-ID 请求头传递医疗机构ID
    """
    # 检查医疗机构是否存在
    hospital = HospitalService.get_hospital_by_id(db=db, hospital_id=hospital_id)
    if not hospital:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"医疗机构 ID {hospital_id} 不存在"
        )
    
    # 检查医疗机构是否启用
    if not hospital.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该医疗机构已被禁用"
        )
    
    # 检查用户是否有权访问该医疗机构
    if not HospitalService.can_user_access_hospital(db=db, user_id=current_user.id, hospital_id=hospital_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="您没有权限访问该医疗机构"
        )
    
    # 返回成功响应
    # 前端需要将hospital_id存储到localStorage或sessionStorage
    # 并在后续请求中通过 X-Hospital-ID 请求头传递
    return HospitalActivate(
        hospital_id=hospital.id,
        hospital_name=hospital.name,
        message="医疗机构激活成功，请在后续请求中通过 X-Hospital-ID 请求头传递医疗机构ID"
    )
