"""
指标API路由 - 智能问数系统
具有业务含义的数据度量单位管理
"""
import logging
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, or_
from typing import List, Optional

from app.api.deps import get_db, get_current_active_user
from app.models import User, MetricProject, MetricTopic, Metric, MetricRelation
from app.middleware.hospital_context import require_hospital_id
from app.schemas.metric import (
    MetricCreate,
    MetricUpdate,
    MetricResponse,
    MetricListResponse,
    MetricTreeNodeResponse,
    MetricTreeResponse,
    MetricSearchRequest,
    MetricReorderRequest,
)
from app.schemas.metric_relation import (
    MetricRelationCreate,
    MetricRelationResponse,
    MetricRelationListResponse,
    AffectedMetricResponse,
    AffectedMetricsResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter()

# 指标类型显示名称映射
METRIC_TYPE_DISPLAY = {
    "atomic": "原子指标",
    "composite": "复合指标",
}

# 关联类型显示名称映射
RELATION_TYPE_DISPLAY = {
    "component": "组成关系",
    "derived": "派生关系",
    "related": "相关关系",
}


def _build_metric_response(metric: Metric, db: Session) -> MetricResponse:
    """构建指标响应对象"""
    # 获取主题和项目信息
    topic_name = metric.topic.name if metric.topic else None
    project_id = metric.topic.project_id if metric.topic else None
    project_name = metric.topic.project.name if metric.topic and metric.topic.project else None
    
    # 获取数据源名称
    data_source_name = metric.data_source.name if metric.data_source else None
    
    # 统计关联指标数量
    related_count = db.query(func.count(MetricRelation.id)).filter(
        or_(
            MetricRelation.source_metric_id == metric.id,
            MetricRelation.target_metric_id == metric.id
        )
    ).scalar() or 0
    
    return MetricResponse(
        id=metric.id,
        topic_id=metric.topic_id,
        topic_name=topic_name,
        project_id=project_id,
        project_name=project_name,
        name_cn=metric.name_cn,
        name_en=metric.name_en,
        metric_type=metric.metric_type,
        metric_type_display=METRIC_TYPE_DISPLAY.get(metric.metric_type, metric.metric_type),
        metric_level=metric.metric_level,
        business_caliber=metric.business_caliber,
        technical_caliber=metric.technical_caliber,
        source_tables=metric.source_tables,
        dimension_tables=metric.dimension_tables,
        dimensions=metric.dimensions,
        data_source_id=metric.data_source_id,
        data_source_name=data_source_name,
        sort_order=metric.sort_order,
        created_at=metric.created_at,
        updated_at=metric.updated_at,
        related_metric_count=related_count,
    )


def _build_relation_response(relation: MetricRelation) -> MetricRelationResponse:
    """构建指标关联响应对象"""
    return MetricRelationResponse(
        id=relation.id,
        source_metric_id=relation.source_metric_id,
        source_metric_name=relation.source_metric.name_cn if relation.source_metric else None,
        target_metric_id=relation.target_metric_id,
        target_metric_name=relation.target_metric.name_cn if relation.target_metric else None,
        relation_type=relation.relation_type,
        relation_type_display=RELATION_TYPE_DISPLAY.get(relation.relation_type, relation.relation_type),
        created_at=relation.created_at,
    )


@router.get("/tree", response_model=dict)
def get_metric_tree(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    获取指标树结构
    
    需求 7.1: 当用户查看指标树时，指标资产管理模块应显示多根树结构，
    项目为根节点，主题为一级子节点，指标为二级子节点
    """
    hospital_id = require_hospital_id()
    
    # 获取所有项目
    projects = db.query(MetricProject).filter(
        MetricProject.hospital_id == hospital_id
    ).order_by(MetricProject.sort_order, MetricProject.id).all()
    
    # 获取所有主题
    topics = db.query(MetricTopic).join(
        MetricProject, MetricTopic.project_id == MetricProject.id
    ).filter(
        MetricProject.hospital_id == hospital_id
    ).order_by(MetricTopic.sort_order, MetricTopic.id).all()
    
    # 获取所有指标
    metrics = db.query(Metric).join(
        MetricTopic, Metric.topic_id == MetricTopic.id
    ).join(
        MetricProject, MetricTopic.project_id == MetricProject.id
    ).filter(
        MetricProject.hospital_id == hospital_id
    ).order_by(Metric.sort_order, Metric.id).all()
    
    # 构建主题ID到指标列表的映射
    topic_metrics_map = {}
    for metric in metrics:
        if metric.topic_id not in topic_metrics_map:
            topic_metrics_map[metric.topic_id] = []
        topic_metrics_map[metric.topic_id].append(MetricTreeNodeResponse(
            id=metric.id,
            name=metric.name_cn,
            node_type="metric",
            sort_order=metric.sort_order,
            topic_id=metric.topic_id,
            metric_type=metric.metric_type,
            metric_type_display=METRIC_TYPE_DISPLAY.get(metric.metric_type, metric.metric_type),
        ))
    
    # 构建项目ID到主题列表的映射
    project_topics_map = {}
    for topic in topics:
        if topic.project_id not in project_topics_map:
            project_topics_map[topic.project_id] = []
        topic_children = topic_metrics_map.get(topic.id, None)
        project_topics_map[topic.project_id].append(MetricTreeNodeResponse(
            id=topic.id,
            name=topic.name,
            node_type="topic",
            sort_order=topic.sort_order,
            description=topic.description,
            project_id=topic.project_id,
            children=topic_children if topic_children else None,
        ))
    
    # 构建项目树
    tree_items = []
    for project in projects:
        project_children = project_topics_map.get(project.id, None)
        tree_items.append(MetricTreeNodeResponse(
            id=project.id,
            name=project.name,
            node_type="project",
            sort_order=project.sort_order,
            description=project.description,
            children=project_children if project_children else None,
        ))
    
    return {
        "code": 200,
        "message": "success",
        "data": {
            "items": [item.model_dump() for item in tree_items],
            "total_projects": len(projects),
            "total_topics": len(topics),
            "total_metrics": len(metrics),
        },
    }


@router.put("/reorder", response_model=dict)
def reorder_metrics(
    data: MetricReorderRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    重新排序指标
    
    需求 7.4: 当用户对同级节点重新排序时，指标资产管理模块应更新排序顺序并持久化更改
    """
    hospital_id = require_hospital_id()
    
    # 验证主题存在且属于当前医疗机构
    topic = db.query(MetricTopic).join(
        MetricProject, MetricTopic.project_id == MetricProject.id
    ).filter(
        MetricTopic.id == data.topic_id,
        MetricProject.hospital_id == hospital_id
    ).first()
    
    if not topic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="指标主题不存在或不属于当前医疗机构"
        )
    
    # 验证所有指标ID都属于该主题
    metrics = db.query(Metric).filter(
        Metric.topic_id == data.topic_id,
        Metric.id.in_(data.metric_ids)
    ).all()
    
    if len(metrics) != len(data.metric_ids):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="部分指标ID无效或不属于该主题"
        )
    
    # 创建ID到指标的映射
    metric_map = {m.id: m for m in metrics}
    
    # 按新顺序更新sort_order
    for index, mid in enumerate(data.metric_ids):
        metric = metric_map.get(mid)
        if metric:
            metric.sort_order = index
    
    db.commit()
    
    logger.info(f"重新排序指标: topic_id={data.topic_id}, new_order={data.metric_ids}")
    
    return {
        "code": 200,
        "message": "排序更新成功",
    }


@router.get("", response_model=dict)
def list_metrics(
    keyword: Optional[str] = Query(None, description="搜索关键词"),
    project_id: Optional[int] = Query(None, description="项目ID筛选"),
    topic_id: Optional[int] = Query(None, description="主题ID筛选"),
    metric_type: Optional[str] = Query(None, description="指标类型筛选"),
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=100, description="每页数量"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    获取指标列表（支持搜索和筛选）
    
    需求 8.1: 当用户点击树中的指标时，指标资产管理模块应在右侧显示指标详情面板
    """
    hospital_id = require_hospital_id()
    
    # 构建基础查询
    query = db.query(Metric).join(
        MetricTopic, Metric.topic_id == MetricTopic.id
    ).join(
        MetricProject, MetricTopic.project_id == MetricProject.id
    ).filter(
        MetricProject.hospital_id == hospital_id
    )
    
    # 关键词搜索
    if keyword:
        keyword_filter = f"%{keyword}%"
        query = query.filter(
            or_(
                Metric.name_cn.ilike(keyword_filter),
                Metric.name_en.ilike(keyword_filter),
                Metric.business_caliber.ilike(keyword_filter),
            )
        )
    
    # 项目筛选
    if project_id is not None:
        query = query.filter(MetricTopic.project_id == project_id)
    
    # 主题筛选
    if topic_id is not None:
        query = query.filter(Metric.topic_id == topic_id)
    
    # 指标类型筛选
    if metric_type is not None:
        query = query.filter(Metric.metric_type == metric_type)
    
    # 统计总数
    total = query.count()
    
    # 分页查询
    metrics = query.order_by(
        Metric.sort_order, Metric.id
    ).offset((page - 1) * size).limit(size).all()
    
    items = [_build_metric_response(m, db) for m in metrics]
    
    return {
        "code": 200,
        "message": "success",
        "data": {
            "items": [item.model_dump() for item in items],
            "total": total,
            "page": page,
            "size": size,
        },
    }


@router.post("", response_model=dict)
def create_metric(
    data: MetricCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    创建指标
    
    需求 8.5: 当用户创建新指标时，指标资产管理模块应将其添加到所选主题下并设置默认值
    """
    hospital_id = require_hospital_id()
    
    # 验证主题存在且属于当前医疗机构
    topic = db.query(MetricTopic).join(
        MetricProject, MetricTopic.project_id == MetricProject.id
    ).filter(
        MetricTopic.id == data.topic_id,
        MetricProject.hospital_id == hospital_id
    ).first()
    
    if not topic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="指标主题不存在或不属于当前医疗机构"
        )
    
    # 检查名称是否在同一主题下重复
    existing = db.query(Metric).filter(
        Metric.topic_id == data.topic_id,
        Metric.name_cn == data.name_cn
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"指标名称 '{data.name_cn}' 在该主题下已存在"
        )
    
    # 如果未指定排序顺序，设置为该主题下最大值+1
    if data.sort_order == 0:
        max_order = db.query(func.max(Metric.sort_order)).filter(
            Metric.topic_id == data.topic_id
        ).scalar() or 0
        sort_order = max_order + 1
    else:
        sort_order = data.sort_order
    
    # 创建指标
    metric = Metric(
        topic_id=data.topic_id,
        name_cn=data.name_cn,
        name_en=data.name_en,
        metric_type=data.metric_type,
        metric_level=data.metric_level,
        business_caliber=data.business_caliber,
        technical_caliber=data.technical_caliber,
        source_tables=data.source_tables,
        dimension_tables=data.dimension_tables,
        dimensions=data.dimensions,
        data_source_id=data.data_source_id,
        sort_order=sort_order,
    )
    
    db.add(metric)
    db.commit()
    db.refresh(metric)
    
    logger.info(f"创建指标: id={metric.id}, name={metric.name_cn}, topic_id={data.topic_id}")
    
    return {
        "code": 200,
        "message": "创建成功",
        "data": _build_metric_response(metric, db).model_dump(),
    }


@router.get("/{metric_id}", response_model=dict)
def get_metric(
    metric_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    获取指标详情
    
    需求 8.1: 当用户点击树中的指标时，指标资产管理模块应在右侧显示指标详情面板
    """
    hospital_id = require_hospital_id()
    
    metric = db.query(Metric).join(
        MetricTopic, Metric.topic_id == MetricTopic.id
    ).join(
        MetricProject, MetricTopic.project_id == MetricProject.id
    ).filter(
        Metric.id == metric_id,
        MetricProject.hospital_id == hospital_id
    ).first()
    
    if not metric:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="指标不存在"
        )
    
    return {
        "code": 200,
        "message": "success",
        "data": _build_metric_response(metric, db).model_dump(),
    }


@router.put("/{metric_id}", response_model=dict)
def update_metric(
    metric_id: int,
    data: MetricUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    更新指标
    
    需求 8.2, 8.3: 当用户编辑指标业务属性/技术属性时，指标资产管理模块应允许编辑相关字段
    需求 8.4: 当用户保存指标更改时，指标资产管理模块应验证必填字段并持久化更改
    """
    hospital_id = require_hospital_id()
    
    metric = db.query(Metric).join(
        MetricTopic, Metric.topic_id == MetricTopic.id
    ).join(
        MetricProject, MetricTopic.project_id == MetricProject.id
    ).filter(
        Metric.id == metric_id,
        MetricProject.hospital_id == hospital_id
    ).first()
    
    if not metric:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="指标不存在"
        )
    
    # 如果要更改主题，验证新主题存在且属于当前医疗机构
    if data.topic_id is not None and data.topic_id != metric.topic_id:
        new_topic = db.query(MetricTopic).join(
            MetricProject, MetricTopic.project_id == MetricProject.id
        ).filter(
            MetricTopic.id == data.topic_id,
            MetricProject.hospital_id == hospital_id
        ).first()
        if not new_topic:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="目标主题不存在或不属于当前医疗机构"
            )
    
    # 检查名称是否与同一主题下其他指标重复
    target_topic_id = data.topic_id if data.topic_id is not None else metric.topic_id
    if data.name_cn and data.name_cn != metric.name_cn:
        existing = db.query(Metric).filter(
            Metric.topic_id == target_topic_id,
            Metric.name_cn == data.name_cn,
            Metric.id != metric_id
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"指标名称 '{data.name_cn}' 在该主题下已存在"
            )
    
    # 更新字段
    if data.topic_id is not None:
        metric.topic_id = data.topic_id
    if data.name_cn is not None:
        metric.name_cn = data.name_cn
    if data.name_en is not None:
        metric.name_en = data.name_en
    if data.metric_type is not None:
        metric.metric_type = data.metric_type
    if data.metric_level is not None:
        metric.metric_level = data.metric_level
    if data.business_caliber is not None:
        metric.business_caliber = data.business_caliber
    if data.technical_caliber is not None:
        metric.technical_caliber = data.technical_caliber
    if data.source_tables is not None:
        metric.source_tables = data.source_tables
    if data.dimension_tables is not None:
        metric.dimension_tables = data.dimension_tables
    if data.dimensions is not None:
        metric.dimensions = data.dimensions
    if data.data_source_id is not None:
        metric.data_source_id = data.data_source_id
    if data.sort_order is not None:
        metric.sort_order = data.sort_order
    
    db.commit()
    db.refresh(metric)
    
    logger.info(f"更新指标: id={metric.id}, name={metric.name_cn}")
    
    return {
        "code": 200,
        "message": "更新成功",
        "data": _build_metric_response(metric, db).model_dump(),
    }



@router.get("/{metric_id}/affected", response_model=dict)
def get_affected_metrics(
    metric_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    获取受影响的指标列表（删除前检查）
    
    需求 9.4: 当用户尝试删除被其他指标关联的指标时，
    指标资产管理模块应在删除前显示受影响的指标列表并要求用户确认
    """
    hospital_id = require_hospital_id()
    
    # 验证指标存在
    metric = db.query(Metric).join(
        MetricTopic, Metric.topic_id == MetricTopic.id
    ).join(
        MetricProject, MetricTopic.project_id == MetricProject.id
    ).filter(
        Metric.id == metric_id,
        MetricProject.hospital_id == hospital_id
    ).first()
    
    if not metric:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="指标不存在"
        )
    
    # 查找所有引用此指标的关联（此指标作为目标）
    relations = db.query(MetricRelation).filter(
        MetricRelation.target_metric_id == metric_id
    ).all()
    
    affected_items = []
    for relation in relations:
        source_metric = relation.source_metric
        if source_metric:
            topic_name = source_metric.topic.name if source_metric.topic else None
            project_name = source_metric.topic.project.name if source_metric.topic and source_metric.topic.project else None
            affected_items.append(AffectedMetricResponse(
                id=source_metric.id,
                name_cn=source_metric.name_cn,
                topic_name=topic_name,
                project_name=project_name,
                relation_type=relation.relation_type,
            ))
    
    return {
        "code": 200,
        "message": "success",
        "data": {
            "items": [item.model_dump() for item in affected_items],
            "total": len(affected_items),
            "can_delete": len(affected_items) == 0,
        },
    }



@router.delete("/{metric_id}", response_model=dict)
def delete_metric(
    metric_id: int,
    force: bool = Query(False, description="强制删除（即使有关联）"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    删除指标
    
    需求 9.4: 当用户尝试删除被其他指标关联的指标时，
    指标资产管理模块应在删除前显示受影响的指标列表并要求用户确认
    """
    hospital_id = require_hospital_id()
    
    metric = db.query(Metric).join(
        MetricTopic, Metric.topic_id == MetricTopic.id
    ).join(
        MetricProject, MetricTopic.project_id == MetricProject.id
    ).filter(
        Metric.id == metric_id,
        MetricProject.hospital_id == hospital_id
    ).first()
    
    if not metric:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="指标不存在"
        )
    
    # 检查是否有其他指标引用此指标（作为目标）
    if not force:
        affected_count = db.query(func.count(MetricRelation.id)).filter(
            MetricRelation.target_metric_id == metric_id
        ).scalar() or 0
        
        if affected_count > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"该指标被 {affected_count} 个其他指标引用，请先查看受影响的指标列表或使用强制删除"
            )
    
    metric_name = metric.name_cn
    db.delete(metric)
    db.commit()
    
    logger.info(f"删除指标: id={metric_id}, name={metric_name}, force={force}")
    
    return {
        "code": 200,
        "message": "删除成功",
    }



# ==================== 指标关联管理 ====================

@router.get("/{metric_id}/relations", response_model=dict)
def get_metric_relations(
    metric_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    获取指标的关联列表
    
    需求 9.1: 当用户添加关联指标时，指标资产管理模块应允许从现有指标中选择并保存关联关系
    需求 9.2: 当用户查看复合指标时，指标资产管理模块应显示所有关联的原子指标
    """
    hospital_id = require_hospital_id()
    
    # 验证指标存在
    metric = db.query(Metric).join(
        MetricTopic, Metric.topic_id == MetricTopic.id
    ).join(
        MetricProject, MetricTopic.project_id == MetricProject.id
    ).filter(
        Metric.id == metric_id,
        MetricProject.hospital_id == hospital_id
    ).first()
    
    if not metric:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="指标不存在"
        )
    
    # 获取此指标作为源的所有关联（此指标引用的其他指标）
    source_relations = db.query(MetricRelation).filter(
        MetricRelation.source_metric_id == metric_id
    ).all()
    
    # 获取此指标作为目标的所有关联（引用此指标的其他指标）
    target_relations = db.query(MetricRelation).filter(
        MetricRelation.target_metric_id == metric_id
    ).all()
    
    # 合并并构建响应
    all_relations = source_relations + target_relations
    items = [_build_relation_response(r) for r in all_relations]
    
    return {
        "code": 200,
        "message": "success",
        "data": {
            "items": [item.model_dump() for item in items],
            "total": len(items),
            "as_source_count": len(source_relations),
            "as_target_count": len(target_relations),
        },
    }



@router.post("/{metric_id}/relations", response_model=dict)
def create_metric_relation(
    metric_id: int,
    data: MetricRelationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    添加指标关联
    
    需求 9.1: 当用户添加关联指标时，指标资产管理模块应允许从现有指标中选择并保存关联关系
    """
    hospital_id = require_hospital_id()
    
    # 验证源指标存在
    source_metric = db.query(Metric).join(
        MetricTopic, Metric.topic_id == MetricTopic.id
    ).join(
        MetricProject, MetricTopic.project_id == MetricProject.id
    ).filter(
        Metric.id == metric_id,
        MetricProject.hospital_id == hospital_id
    ).first()
    
    if not source_metric:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="源指标不存在"
        )
    
    # 验证目标指标存在
    target_metric = db.query(Metric).join(
        MetricTopic, Metric.topic_id == MetricTopic.id
    ).join(
        MetricProject, MetricTopic.project_id == MetricProject.id
    ).filter(
        Metric.id == data.target_metric_id,
        MetricProject.hospital_id == hospital_id
    ).first()
    
    if not target_metric:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="目标指标不存在"
        )
    
    # 不能关联自己
    if metric_id == data.target_metric_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不能将指标关联到自身"
        )
    
    # 检查关联是否已存在
    existing = db.query(MetricRelation).filter(
        MetricRelation.source_metric_id == metric_id,
        MetricRelation.target_metric_id == data.target_metric_id
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该关联关系已存在"
        )
    
    # 创建关联
    relation = MetricRelation(
        source_metric_id=metric_id,
        target_metric_id=data.target_metric_id,
        relation_type=data.relation_type,
    )
    
    db.add(relation)
    db.commit()
    db.refresh(relation)
    
    logger.info(f"创建指标关联: source={metric_id}, target={data.target_metric_id}, type={data.relation_type}")
    
    return {
        "code": 200,
        "message": "创建成功",
        "data": _build_relation_response(relation).model_dump(),
    }


@router.delete("/{metric_id}/relations/{related_id}", response_model=dict)
def delete_metric_relation(
    metric_id: int,
    related_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    删除指标关联
    
    需求 9.3: 当用户移除指标关联时，指标资产管理模块应删除关联关系但不影响指标本身
    """
    hospital_id = require_hospital_id()
    
    # 验证源指标存在
    source_metric = db.query(Metric).join(
        MetricTopic, Metric.topic_id == MetricTopic.id
    ).join(
        MetricProject, MetricTopic.project_id == MetricProject.id
    ).filter(
        Metric.id == metric_id,
        MetricProject.hospital_id == hospital_id
    ).first()
    
    if not source_metric:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="源指标不存在"
        )
    
    # 查找关联关系（可能是源或目标）
    relation = db.query(MetricRelation).filter(
        or_(
            (MetricRelation.source_metric_id == metric_id) & (MetricRelation.target_metric_id == related_id),
            (MetricRelation.source_metric_id == related_id) & (MetricRelation.target_metric_id == metric_id),
        )
    ).first()
    
    if not relation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="关联关系不存在"
        )
    
    db.delete(relation)
    db.commit()
    
    logger.info(f"删除指标关联: metric_id={metric_id}, related_id={related_id}")
    
    return {
        "code": 200,
        "message": "删除成功",
    }


