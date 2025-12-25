"""
指标主题API路由 - 智能问数系统
项目下的一级分类，用于归类指标
"""
import logging
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional

from app.api.deps import get_db, get_current_active_user
from app.models import User, MetricProject, MetricTopic, Metric
from app.middleware.hospital_context import require_hospital_id
from app.schemas.metric_topic import (
    MetricTopicCreate,
    MetricTopicUpdate,
    MetricTopicResponse,
    MetricTopicListResponse,
    MetricTopicReorderRequest,
)

logger = logging.getLogger(__name__)

router = APIRouter()


def _build_response(topic: MetricTopic, db: Session) -> MetricTopicResponse:
    """构建指标主题响应对象，包含统计信息"""
    # 统计指标数量
    metric_count = db.query(func.count(Metric.id)).filter(
        Metric.topic_id == topic.id
    ).scalar() or 0
    
    # 获取项目名称
    project_name = topic.project.name if topic.project else None
    
    return MetricTopicResponse(
        id=topic.id,
        project_id=topic.project_id,
        project_name=project_name,
        name=topic.name,
        description=topic.description,
        sort_order=topic.sort_order,
        created_at=topic.created_at,
        updated_at=topic.updated_at,
        metric_count=metric_count,
    )


@router.get("", response_model=dict)
def list_metric_topics(
    project_id: Optional[int] = Query(None, description="按项目ID筛选"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    获取指标主题列表
    
    返回当前医疗机构的所有指标主题，按排序顺序排列。
    可选按项目ID筛选。
    """
    hospital_id = require_hospital_id()
    
    # 构建查询，通过项目关联过滤医疗机构
    query = db.query(MetricTopic).join(
        MetricProject, MetricTopic.project_id == MetricProject.id
    ).filter(
        MetricProject.hospital_id == hospital_id
    )
    
    # 按项目ID筛选
    if project_id is not None:
        query = query.filter(MetricTopic.project_id == project_id)
    
    topics = query.order_by(MetricTopic.sort_order, MetricTopic.id).all()
    
    items = [_build_response(t, db) for t in topics]
    
    return {
        "code": 200,
        "message": "success",
        "data": {
            "items": [item.model_dump() for item in items],
            "total": len(items),
        },
    }


@router.put("/reorder", response_model=dict)
def reorder_metric_topics(
    data: MetricTopicReorderRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    重新排序指标主题
    
    需求 7.4: 当用户对同级节点重新排序时，指标资产管理模块应更新排序顺序并持久化更改
    """
    hospital_id = require_hospital_id()
    
    # 验证所有主题ID都属于当前医疗机构（通过项目关联）
    topics = db.query(MetricTopic).join(
        MetricProject, MetricTopic.project_id == MetricProject.id
    ).filter(
        MetricProject.hospital_id == hospital_id,
        MetricTopic.id.in_(data.topic_ids)
    ).all()
    
    if len(topics) != len(data.topic_ids):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="部分主题ID无效或不属于当前医疗机构"
        )
    
    # 创建ID到主题的映射
    topic_map = {t.id: t for t in topics}
    
    # 按新顺序更新sort_order
    for index, topic_id in enumerate(data.topic_ids):
        topic = topic_map.get(topic_id)
        if topic:
            topic.sort_order = index
    
    db.commit()
    
    logger.info(f"重新排序指标主题: hospital_id={hospital_id}, new_order={data.topic_ids}")
    
    return {
        "code": 200,
        "message": "排序更新成功",
    }


@router.post("", response_model=dict)
def create_metric_topic(
    data: MetricTopicCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    创建指标主题
    
    需求 7.3: 当用户在项目下创建新主题时，指标资产管理模块应将主题添加为所选项目的子节点
    """
    hospital_id = require_hospital_id()
    
    # 验证项目存在且属于当前医疗机构
    project = db.query(MetricProject).filter(
        MetricProject.id == data.project_id,
        MetricProject.hospital_id == hospital_id
    ).first()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="指标项目不存在或不属于当前医疗机构"
        )
    
    # 检查名称是否在同一项目下重复
    existing = db.query(MetricTopic).filter(
        MetricTopic.project_id == data.project_id,
        MetricTopic.name == data.name
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"主题名称 '{data.name}' 在该项目下已存在"
        )
    
    # 如果未指定排序顺序，设置为该项目下最大值+1
    if data.sort_order == 0:
        max_order = db.query(func.max(MetricTopic.sort_order)).filter(
            MetricTopic.project_id == data.project_id
        ).scalar() or 0
        sort_order = max_order + 1
    else:
        sort_order = data.sort_order
    
    # 创建主题
    topic = MetricTopic(
        project_id=data.project_id,
        name=data.name,
        description=data.description,
        sort_order=sort_order,
    )
    
    db.add(topic)
    db.commit()
    db.refresh(topic)
    
    logger.info(f"创建指标主题: id={topic.id}, name={topic.name}, project_id={data.project_id}")
    
    return {
        "code": 200,
        "message": "创建成功",
        "data": _build_response(topic, db).model_dump(),
    }


@router.get("/{topic_id}", response_model=dict)
def get_metric_topic(
    topic_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    获取指标主题详情
    """
    hospital_id = require_hospital_id()
    
    topic = db.query(MetricTopic).join(
        MetricProject, MetricTopic.project_id == MetricProject.id
    ).filter(
        MetricTopic.id == topic_id,
        MetricProject.hospital_id == hospital_id
    ).first()
    
    if not topic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="指标主题不存在"
        )
    
    return {
        "code": 200,
        "message": "success",
        "data": _build_response(topic, db).model_dump(),
    }


@router.put("/{topic_id}", response_model=dict)
def update_metric_topic(
    topic_id: int,
    data: MetricTopicUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    更新指标主题
    """
    hospital_id = require_hospital_id()
    
    topic = db.query(MetricTopic).join(
        MetricProject, MetricTopic.project_id == MetricProject.id
    ).filter(
        MetricTopic.id == topic_id,
        MetricProject.hospital_id == hospital_id
    ).first()
    
    if not topic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="指标主题不存在"
        )
    
    # 如果要更改项目，验证新项目存在且属于当前医疗机构
    if data.project_id is not None and data.project_id != topic.project_id:
        new_project = db.query(MetricProject).filter(
            MetricProject.id == data.project_id,
            MetricProject.hospital_id == hospital_id
        ).first()
        if not new_project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="目标项目不存在或不属于当前医疗机构"
            )
    
    # 检查名称是否与同一项目下其他主题重复
    target_project_id = data.project_id if data.project_id is not None else topic.project_id
    if data.name and data.name != topic.name:
        existing = db.query(MetricTopic).filter(
            MetricTopic.project_id == target_project_id,
            MetricTopic.name == data.name,
            MetricTopic.id != topic_id
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"主题名称 '{data.name}' 在该项目下已存在"
            )
    
    # 更新字段
    if data.project_id is not None:
        topic.project_id = data.project_id
    if data.name is not None:
        topic.name = data.name
    if data.description is not None:
        topic.description = data.description
    if data.sort_order is not None:
        topic.sort_order = data.sort_order
    
    db.commit()
    db.refresh(topic)
    
    logger.info(f"更新指标主题: id={topic.id}, name={topic.name}")
    
    return {
        "code": 200,
        "message": "更新成功",
        "data": _build_response(topic, db).model_dump(),
    }


@router.delete("/{topic_id}", response_model=dict)
def delete_metric_topic(
    topic_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    删除指标主题
    
    删除主题时会级联删除其下所有指标。
    需求 7.5: 当用户删除项目或主题时，指标资产管理模块应在确认后移除该节点及其所有子节点
    """
    hospital_id = require_hospital_id()
    
    topic = db.query(MetricTopic).join(
        MetricProject, MetricTopic.project_id == MetricProject.id
    ).filter(
        MetricTopic.id == topic_id,
        MetricProject.hospital_id == hospital_id
    ).first()
    
    if not topic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="指标主题不存在"
        )
    
    # 统计将被删除的指标数量（用于日志和返回）
    metric_count = db.query(func.count(Metric.id)).filter(
        Metric.topic_id == topic_id
    ).scalar() or 0
    
    topic_name = topic.name
    db.delete(topic)
    db.commit()
    
    logger.info(f"删除指标主题: id={topic_id}, name={topic_name}, 级联删除指标数={metric_count}")
    
    return {
        "code": 200,
        "message": "删除成功",
        "data": {
            "deleted_metrics": metric_count,
        },
    }
