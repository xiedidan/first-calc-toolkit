"""
对话分组API路由 - 智能问数系统
用于组织和管理多个相关对话的容器
"""
import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List

from app.api.deps import get_db, get_current_active_user
from app.models import User, ConversationGroup, Conversation
from app.middleware.hospital_context import require_hospital_id
from app.schemas.conversation_group import (
    ConversationGroupCreate,
    ConversationGroupUpdate,
    ConversationGroupResponse,
    ConversationGroupListResponse,
    ConversationGroupReorderRequest,
)

logger = logging.getLogger(__name__)

router = APIRouter()


def _build_response(group: ConversationGroup, db: Session) -> ConversationGroupResponse:
    """构建对话分组响应对象，包含对话数量统计"""
    # 统计分组内对话数量
    conversation_count = db.query(func.count(Conversation.id)).filter(
        Conversation.group_id == group.id
    ).scalar() or 0
    
    return ConversationGroupResponse(
        id=group.id,
        hospital_id=group.hospital_id,
        name=group.name,
        sort_order=group.sort_order,
        is_collapsed=group.is_collapsed,
        conversation_count=conversation_count,
        created_at=group.created_at,
    )


@router.get("", response_model=dict)
def list_conversation_groups(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    获取对话分组列表
    
    返回当前医疗机构的所有对话分组，按排序顺序排列。
    需求 2.1: 当用户创建新的对话分组时，智能数据问答模块应在侧边栏添加该分组并允许命名
    """
    hospital_id = require_hospital_id()
    
    groups = db.query(ConversationGroup).filter(
        ConversationGroup.hospital_id == hospital_id
    ).order_by(ConversationGroup.sort_order, ConversationGroup.id).all()
    
    items = [_build_response(g, db) for g in groups]
    
    return {
        "code": 200,
        "message": "success",
        "data": {
            "items": [item.model_dump() for item in items],
            "total": len(items),
        },
    }



@router.post("", response_model=dict)
def create_conversation_group(
    data: ConversationGroupCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    创建对话分组
    
    需求 2.1: 当用户创建新的对话分组时，智能数据问答模块应在侧边栏添加该分组并允许命名
    """
    hospital_id = require_hospital_id()
    
    # 检查名称是否重复
    existing = db.query(ConversationGroup).filter(
        ConversationGroup.hospital_id == hospital_id,
        ConversationGroup.name == data.name
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"分组名称 '{data.name}' 已存在"
        )
    
    # 如果未指定排序顺序，设置为最大值+1
    if data.sort_order == 0:
        max_order = db.query(func.max(ConversationGroup.sort_order)).filter(
            ConversationGroup.hospital_id == hospital_id
        ).scalar() or 0
        sort_order = max_order + 1
    else:
        sort_order = data.sort_order
    
    # 创建分组
    group = ConversationGroup(
        hospital_id=hospital_id,
        name=data.name,
        sort_order=sort_order,
        is_collapsed=data.is_collapsed,
    )
    
    db.add(group)
    db.commit()
    db.refresh(group)
    
    logger.info(f"创建对话分组: id={group.id}, name={group.name}, hospital_id={hospital_id}")
    
    return {
        "code": 200,
        "message": "创建成功",
        "data": _build_response(group, db).model_dump(),
    }


@router.put("/reorder", response_model=dict)
def reorder_conversation_groups(
    data: ConversationGroupReorderRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    重新排序对话分组
    
    按照传入的分组ID列表顺序更新排序。
    """
    hospital_id = require_hospital_id()
    
    # 验证所有分组ID都属于当前医疗机构
    groups = db.query(ConversationGroup).filter(
        ConversationGroup.hospital_id == hospital_id,
        ConversationGroup.id.in_(data.group_ids)
    ).all()
    
    if len(groups) != len(data.group_ids):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="部分分组ID无效或不属于当前医疗机构"
        )
    
    # 创建ID到分组的映射
    group_map = {g.id: g for g in groups}
    
    # 按新顺序更新sort_order
    for index, group_id in enumerate(data.group_ids):
        group = group_map.get(group_id)
        if group:
            group.sort_order = index
    
    db.commit()
    
    logger.info(f"重新排序对话分组: hospital_id={hospital_id}, new_order={data.group_ids}")
    
    return {
        "code": 200,
        "message": "排序更新成功",
    }


@router.get("/{group_id}", response_model=dict)
def get_conversation_group(
    group_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    获取对话分组详情
    """
    hospital_id = require_hospital_id()
    
    group = db.query(ConversationGroup).filter(
        ConversationGroup.id == group_id,
        ConversationGroup.hospital_id == hospital_id
    ).first()
    
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="对话分组不存在"
        )
    
    return {
        "code": 200,
        "message": "success",
        "data": _build_response(group, db).model_dump(),
    }


@router.put("/{group_id}", response_model=dict)
def update_conversation_group(
    group_id: int,
    data: ConversationGroupUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    更新对话分组
    
    支持更新分组名称、排序顺序和收起状态。
    需求 2.3: 当用户收起某个分组时，智能数据问答模块应隐藏该分组的对话
    需求 2.4: 当用户展开已收起的分组时，智能数据问答模块应显示该分组内的所有对话
    """
    hospital_id = require_hospital_id()
    
    group = db.query(ConversationGroup).filter(
        ConversationGroup.id == group_id,
        ConversationGroup.hospital_id == hospital_id
    ).first()
    
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="对话分组不存在"
        )
    
    # 检查名称是否与其他分组重复
    if data.name and data.name != group.name:
        existing = db.query(ConversationGroup).filter(
            ConversationGroup.hospital_id == hospital_id,
            ConversationGroup.name == data.name,
            ConversationGroup.id != group_id
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"分组名称 '{data.name}' 已存在"
            )
    
    # 更新字段
    if data.name is not None:
        group.name = data.name
    if data.sort_order is not None:
        group.sort_order = data.sort_order
    if data.is_collapsed is not None:
        group.is_collapsed = data.is_collapsed
    
    db.commit()
    db.refresh(group)
    
    logger.info(f"更新对话分组: id={group.id}, name={group.name}")
    
    return {
        "code": 200,
        "message": "更新成功",
        "data": _build_response(group, db).model_dump(),
    }



@router.delete("/{group_id}", response_model=dict)
def delete_conversation_group(
    group_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    删除对话分组
    
    删除分组时，分组内的对话会被移至未分组状态（group_id设为NULL）。
    需求 2.5: 当用户删除分组时，智能数据问答模块应将该分组内的所有对话移至未分组状态
    """
    hospital_id = require_hospital_id()
    
    group = db.query(ConversationGroup).filter(
        ConversationGroup.id == group_id,
        ConversationGroup.hospital_id == hospital_id
    ).first()
    
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="对话分组不存在"
        )
    
    # 统计分组内对话数量
    conversation_count = db.query(func.count(Conversation.id)).filter(
        Conversation.group_id == group_id
    ).scalar() or 0
    
    # 将分组内的对话移至未分组状态
    db.query(Conversation).filter(
        Conversation.group_id == group_id
    ).update({"group_id": None})
    
    group_name = group.name
    db.delete(group)
    db.commit()
    
    logger.info(f"删除对话分组: id={group_id}, name={group_name}, "
                f"移至未分组的对话数={conversation_count}")
    
    return {
        "code": 200,
        "message": "删除成功",
        "data": {
            "ungrouped_conversations": conversation_count,
        },
    }


@router.put("/{group_id}/conversations", response_model=dict)
def move_conversations_to_group(
    group_id: int,
    conversation_ids: List[int],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    批量移动对话到分组
    
    将指定的对话移动到目标分组。
    需求 2.2: 当用户将对话拖拽到某个分组时，智能数据问答模块应将该对话移动到该分组并更新显示
    """
    hospital_id = require_hospital_id()
    
    # 验证分组存在
    group = db.query(ConversationGroup).filter(
        ConversationGroup.id == group_id,
        ConversationGroup.hospital_id == hospital_id
    ).first()
    
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="对话分组不存在"
        )
    
    # 验证所有对话ID都属于当前医疗机构
    conversations = db.query(Conversation).filter(
        Conversation.hospital_id == hospital_id,
        Conversation.id.in_(conversation_ids)
    ).all()
    
    if len(conversations) != len(conversation_ids):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="部分对话ID无效或不属于当前医疗机构"
        )
    
    # 更新对话的分组
    db.query(Conversation).filter(
        Conversation.id.in_(conversation_ids)
    ).update({"group_id": group_id}, synchronize_session=False)
    
    db.commit()
    
    logger.info(f"移动对话到分组: group_id={group_id}, conversation_ids={conversation_ids}")
    
    return {
        "code": 200,
        "message": "移动成功",
        "data": {
            "moved_count": len(conversation_ids),
        },
    }
