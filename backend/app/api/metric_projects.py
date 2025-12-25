"""
指标项目API路由 - 智能问数系统
指标树的根节点管理，用于组织指标
"""
import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List

from app.api.deps import get_db, get_current_active_user
from app.models import User, MetricProject, MetricTopic, Metric
from app.middleware.hospital_context import require_hospital_id
from app.schemas.metric_project import (
    MetricProjectCreate,
    MetricProjectUpdate,
    MetricProjectResponse,
    MetricProjectListResponse,
    MetricProjectReorderRequest,
)

logger = logging.getLogger(__name__)

router = APIRouter()


def _build_response(project: MetricProject, db: Session) -> MetricProjectResponse:
    """构建指标项目响应对象，包含统计信息"""
    # 统计主题数量
    topic_count = db.query(func.count(MetricTopic.id)).filter(
        MetricTopic.project_id == project.id
    ).scalar() or 0
    
    # 统计指标数量（通过主题关联）
    metric_count = db.query(func.count(Metric.id)).join(
        MetricTopic, Metric.topic_id == MetricTopic.id
    ).filter(
        MetricTopic.project_id == project.id
    ).scalar() or 0
    
    return MetricProjectResponse(
        id=project.id,
        hospital_id=project.hospital_id,
        name=project.name,
        description=project.description,
        sort_order=project.sort_order,
        created_at=project.created_at,
        updated_at=project.updated_at,
        topic_count=topic_count,
        metric_count=metric_count,
    )


@router.get("", response_model=dict)
def list_metric_projects(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    获取指标项目列表
    
    返回当前医疗机构的所有指标项目，按排序顺序排列。
    """
    hospital_id = require_hospital_id()
    
    projects = db.query(MetricProject).filter(
        MetricProject.hospital_id == hospital_id
    ).order_by(MetricProject.sort_order, MetricProject.id).all()
    
    items = [_build_response(p, db) for p in projects]
    
    return {
        "code": 200,
        "message": "success",
        "data": {
            "items": [item.model_dump() for item in items],
            "total": len(items),
        },
    }


@router.put("/reorder", response_model=dict)
def reorder_metric_projects(
    data: MetricProjectReorderRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    重新排序指标项目
    
    需求 7.4: 当用户对同级节点重新排序时，指标资产管理模块应更新排序顺序并持久化更改
    """
    hospital_id = require_hospital_id()
    
    # 验证所有项目ID都属于当前医疗机构
    projects = db.query(MetricProject).filter(
        MetricProject.hospital_id == hospital_id,
        MetricProject.id.in_(data.project_ids)
    ).all()
    
    if len(projects) != len(data.project_ids):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="部分项目ID无效或不属于当前医疗机构"
        )
    
    # 创建ID到项目的映射
    project_map = {p.id: p for p in projects}
    
    # 按新顺序更新sort_order
    for index, project_id in enumerate(data.project_ids):
        project = project_map.get(project_id)
        if project:
            project.sort_order = index
    
    db.commit()
    
    logger.info(f"重新排序指标项目: hospital_id={hospital_id}, new_order={data.project_ids}")
    
    return {
        "code": 200,
        "message": "排序更新成功",
    }


@router.post("", response_model=dict)
def create_metric_project(
    data: MetricProjectCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    创建指标项目
    
    创建新的指标项目作为指标树的根节点。
    """
    hospital_id = require_hospital_id()
    
    # 检查名称是否重复
    existing = db.query(MetricProject).filter(
        MetricProject.hospital_id == hospital_id,
        MetricProject.name == data.name
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"项目名称 '{data.name}' 已存在"
        )
    
    # 如果未指定排序顺序，设置为最大值+1
    if data.sort_order == 0:
        max_order = db.query(func.max(MetricProject.sort_order)).filter(
            MetricProject.hospital_id == hospital_id
        ).scalar() or 0
        sort_order = max_order + 1
    else:
        sort_order = data.sort_order
    
    # 创建项目
    project = MetricProject(
        hospital_id=hospital_id,
        name=data.name,
        description=data.description,
        sort_order=sort_order,
    )
    
    db.add(project)
    db.commit()
    db.refresh(project)
    
    logger.info(f"创建指标项目: id={project.id}, name={project.name}, hospital_id={hospital_id}")
    
    return {
        "code": 200,
        "message": "创建成功",
        "data": _build_response(project, db).model_dump(),
    }


@router.get("/{project_id}", response_model=dict)
def get_metric_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    获取指标项目详情
    """
    hospital_id = require_hospital_id()
    
    project = db.query(MetricProject).filter(
        MetricProject.id == project_id,
        MetricProject.hospital_id == hospital_id
    ).first()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="指标项目不存在"
        )
    
    return {
        "code": 200,
        "message": "success",
        "data": _build_response(project, db).model_dump(),
    }


@router.put("/{project_id}", response_model=dict)
def update_metric_project(
    project_id: int,
    data: MetricProjectUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    更新指标项目
    """
    hospital_id = require_hospital_id()
    
    project = db.query(MetricProject).filter(
        MetricProject.id == project_id,
        MetricProject.hospital_id == hospital_id
    ).first()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="指标项目不存在"
        )
    
    # 检查名称是否与其他项目重复
    if data.name and data.name != project.name:
        existing = db.query(MetricProject).filter(
            MetricProject.hospital_id == hospital_id,
            MetricProject.name == data.name,
            MetricProject.id != project_id
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"项目名称 '{data.name}' 已存在"
            )
    
    # 更新字段
    if data.name is not None:
        project.name = data.name
    if data.description is not None:
        project.description = data.description
    if data.sort_order is not None:
        project.sort_order = data.sort_order
    
    db.commit()
    db.refresh(project)
    
    logger.info(f"更新指标项目: id={project.id}, name={project.name}")
    
    return {
        "code": 200,
        "message": "更新成功",
        "data": _build_response(project, db).model_dump(),
    }


@router.delete("/{project_id}", response_model=dict)
def delete_metric_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    删除指标项目
    
    删除项目时会级联删除其下所有主题和指标。
    需求 7.5: 当用户删除项目或主题时，指标资产管理模块应在确认后移除该节点及其所有子节点
    """
    hospital_id = require_hospital_id()
    
    project = db.query(MetricProject).filter(
        MetricProject.id == project_id,
        MetricProject.hospital_id == hospital_id
    ).first()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="指标项目不存在"
        )
    
    # 统计将被删除的子节点数量（用于日志）
    topic_count = db.query(func.count(MetricTopic.id)).filter(
        MetricTopic.project_id == project_id
    ).scalar() or 0
    
    metric_count = db.query(func.count(Metric.id)).join(
        MetricTopic, Metric.topic_id == MetricTopic.id
    ).filter(
        MetricTopic.project_id == project_id
    ).scalar() or 0
    
    project_name = project.name
    db.delete(project)
    db.commit()
    
    logger.info(f"删除指标项目: id={project_id}, name={project_name}, "
                f"级联删除主题数={topic_count}, 指标数={metric_count}")
    
    return {
        "code": 200,
        "message": "删除成功",
        "data": {
            "deleted_topics": topic_count,
            "deleted_metrics": metric_count,
        },
    }
