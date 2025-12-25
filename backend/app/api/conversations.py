"""
对话API路由 - 智能问数系统
用户与AI之间的一次完整交互会话
"""
import logging
from urllib.parse import quote
from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import func, or_
from typing import Optional, List
from datetime import datetime

from app.api.deps import get_db, get_current_active_user
from app.models import User, Conversation, ConversationMessage, ConversationGroup
from app.middleware.hospital_context import require_hospital_id
from app.schemas.conversation import (
    ConversationCreate,
    ConversationUpdate,
    ConversationResponse,
    ConversationListResponse,
    CONVERSATION_TYPE_DISPLAY,
)
from app.schemas.conversation_message import (
    ConversationMessageResponse,
    ConversationDetailResponse,
    SendMessageRequest,
    SendMessageResponse,
    MessageExportRequest,
    CONTENT_TYPE_DISPLAY,
)
from app.models.conversation_message import MessageRole, ContentType
from app.services.conversation_export_service import ConversationExportService
from app.services.metric_caliber_service import (
    MetricCaliberService,
)
from app.services.sql_generation_service import (
    SQLGenerationService,
    SQLGenerationServiceError,
    AINotConfiguredError as SQLAINotConfiguredError,
)

logger = logging.getLogger(__name__)

router = APIRouter()


def _build_conversation_response(conv: Conversation, db: Session) -> ConversationResponse:
    """构建对话响应对象，包含消息数量统计"""
    # 统计消息数量
    message_count = db.query(func.count(ConversationMessage.id)).filter(
        ConversationMessage.conversation_id == conv.id
    ).scalar() or 0
    
    # 获取分组名称
    group_name = None
    if conv.group_id and conv.group:
        group_name = conv.group.name
    
    return ConversationResponse(
        id=conv.id,
        hospital_id=conv.hospital_id,
        group_id=conv.group_id,
        group_name=group_name,
        title=conv.title,
        description=conv.description,
        conversation_type=conv.conversation_type,
        conversation_type_display=CONVERSATION_TYPE_DISPLAY.get(conv.conversation_type, conv.conversation_type),
        message_count=message_count,
        created_at=conv.created_at,
        updated_at=conv.updated_at,
    )


def _build_message_response(msg: ConversationMessage) -> ConversationMessageResponse:
    """构建消息响应对象"""
    return ConversationMessageResponse(
        id=msg.id,
        conversation_id=msg.conversation_id,
        role=msg.role,
        content=msg.content,
        content_type=msg.content_type,
        content_type_display=CONTENT_TYPE_DISPLAY.get(msg.content_type, msg.content_type),
        message_metadata=msg.message_metadata,
        created_at=msg.created_at,
    )


@router.get("", response_model=dict)
def list_conversations(
    keyword: Optional[str] = Query(None, description="搜索关键词（匹配标题或描述）"),
    group_id: Optional[int] = Query(None, description="分组ID筛选，-1表示未分组"),
    conversation_type: Optional[str] = Query(None, description="对话类型筛选"),
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=100, description="每页数量"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    获取对话列表
    
    支持按关键词搜索、分组筛选、对话类型筛选。
    需求 1.2: 当用户通过关键词搜索对话时，智能数据问答模块应筛选并显示标题或描述包含该关键词的对话
    """
    hospital_id = require_hospital_id()
    
    query = db.query(Conversation).filter(
        Conversation.hospital_id == hospital_id
    )
    
    # 关键词搜索（标题或描述）
    if keyword:
        keyword_filter = f"%{keyword}%"
        query = query.filter(
            or_(
                Conversation.title.ilike(keyword_filter),
                Conversation.description.ilike(keyword_filter)
            )
        )
    
    # 分组筛选
    if group_id is not None:
        if group_id == -1:
            # -1 表示未分组
            query = query.filter(Conversation.group_id.is_(None))
        else:
            query = query.filter(Conversation.group_id == group_id)
    
    # 对话类型筛选
    if conversation_type:
        query = query.filter(Conversation.conversation_type == conversation_type)
    
    # 统计总数
    total = query.count()
    
    # 分页查询，按更新时间倒序
    conversations = query.order_by(
        Conversation.updated_at.desc()
    ).offset((page - 1) * size).limit(size).all()
    
    items = [_build_conversation_response(c, db) for c in conversations]
    
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
def create_conversation(
    data: ConversationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    创建新对话
    
    需求 1.1: 当用户点击新建对话按钮时，智能数据问答模块应创建一个带有默认标题的新对话，并在对话列表中显示
    """
    hospital_id = require_hospital_id()
    
    # 如果指定了分组，验证分组存在
    if data.group_id:
        group = db.query(ConversationGroup).filter(
            ConversationGroup.id == data.group_id,
            ConversationGroup.hospital_id == hospital_id
        ).first()
        if not group:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="指定的分组不存在"
            )
    
    # 创建对话
    conversation = Conversation(
        hospital_id=hospital_id,
        group_id=data.group_id,
        title=data.title,
        description=data.description,
        conversation_type=data.conversation_type,
    )
    
    db.add(conversation)
    db.commit()
    db.refresh(conversation)
    
    logger.info(f"创建对话: id={conversation.id}, title={conversation.title}, "
                f"type={conversation.conversation_type}, hospital_id={hospital_id}")
    
    return {
        "code": 200,
        "message": "创建成功",
        "data": _build_conversation_response(conversation, db).model_dump(),
    }


@router.get("/{conversation_id}", response_model=dict)
def get_conversation(
    conversation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    获取对话详情（包含消息历史）
    
    需求 1.3: 当用户点击对话列表中的某个对话时，智能数据问答模块应加载并在主聊天区域显示该对话的历史记录
    """
    hospital_id = require_hospital_id()
    
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.hospital_id == hospital_id
    ).first()
    
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="对话不存在"
        )
    
    # 获取消息列表，按创建时间正序
    messages = db.query(ConversationMessage).filter(
        ConversationMessage.conversation_id == conversation_id
    ).order_by(ConversationMessage.created_at.asc()).all()
    
    # 获取分组名称
    group_name = None
    if conversation.group_id and conversation.group:
        group_name = conversation.group.name
    
    # 构建详情响应
    detail = ConversationDetailResponse(
        id=conversation.id,
        hospital_id=conversation.hospital_id,
        group_id=conversation.group_id,
        group_name=group_name,
        title=conversation.title,
        description=conversation.description,
        conversation_type=conversation.conversation_type,
        conversation_type_display=CONVERSATION_TYPE_DISPLAY.get(
            conversation.conversation_type, conversation.conversation_type
        ),
        messages=[_build_message_response(m) for m in messages],
        message_count=len(messages),
        created_at=conversation.created_at,
        updated_at=conversation.updated_at,
    )
    
    return {
        "code": 200,
        "message": "success",
        "data": detail.model_dump(),
    }


@router.put("/{conversation_id}", response_model=dict)
def update_conversation(
    conversation_id: int,
    data: ConversationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    更新对话
    
    支持更新标题、描述、对话类型和分组。
    需求 1.4: 当用户编辑对话标题时，智能数据问答模块应更新标题并将更改持久化到数据库
    需求 6.5: 当用户在对话中途切换对话类型时，智能数据问答模块应将新类型应用于后续消息
    """
    hospital_id = require_hospital_id()
    
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.hospital_id == hospital_id
    ).first()
    
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="对话不存在"
        )
    
    # 如果要更新分组，验证分组存在
    if data.group_id is not None and data.group_id != 0:
        group = db.query(ConversationGroup).filter(
            ConversationGroup.id == data.group_id,
            ConversationGroup.hospital_id == hospital_id
        ).first()
        if not group:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="指定的分组不存在"
            )
    
    # 更新字段
    if data.title is not None:
        conversation.title = data.title
    if data.description is not None:
        conversation.description = data.description
    if data.conversation_type is not None:
        conversation.conversation_type = data.conversation_type
    # group_id 可以设为 None（移至未分组）
    if 'group_id' in data.model_dump(exclude_unset=True):
        conversation.group_id = data.group_id if data.group_id != 0 else None
    
    # 更新时间
    conversation.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(conversation)
    
    logger.info(f"更新对话: id={conversation.id}, title={conversation.title}")
    
    return {
        "code": 200,
        "message": "更新成功",
        "data": _build_conversation_response(conversation, db).model_dump(),
    }


@router.delete("/{conversation_id}", response_model=dict)
def delete_conversation(
    conversation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    删除对话
    
    删除对话时会级联删除所有消息。
    需求 1.5: 当用户删除对话时，智能数据问答模块应从系统中移除该对话及其所有消息
    """
    hospital_id = require_hospital_id()
    
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.hospital_id == hospital_id
    ).first()
    
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="对话不存在"
        )
    
    # 统计消息数量
    message_count = db.query(func.count(ConversationMessage.id)).filter(
        ConversationMessage.conversation_id == conversation_id
    ).scalar() or 0
    
    conversation_title = conversation.title
    
    # 删除对话（消息会级联删除）
    db.delete(conversation)
    db.commit()
    
    logger.info(f"删除对话: id={conversation_id}, title={conversation_title}, "
                f"删除的消息数={message_count}")
    
    return {
        "code": 200,
        "message": "删除成功",
        "data": {
            "deleted_messages": message_count,
        },
    }


@router.post("/{conversation_id}/messages", response_model=dict)
def send_message(
    conversation_id: int,
    data: SendMessageRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    发送消息并获取AI回复
    
    需求 6.1: 当用户输入消息并点击发送或按回车键时，智能数据问答模块应将消息发送给AI并在对话中显示
    需求 6.2: 当AI生成响应时，智能数据问答模块应以适当的格式（表格、代码块、图表）显示响应内容
    
    注意：当前实现仅保存用户消息，AI回复功能将在后续AI服务集成时实现。
    """
    hospital_id = require_hospital_id()
    
    # 验证对话存在
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.hospital_id == hospital_id
    ).first()
    
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="对话不存在"
        )
    
    # 创建用户消息
    user_message = ConversationMessage(
        conversation_id=conversation_id,
        role=MessageRole.USER,
        content=data.content,
        content_type=ContentType.TEXT,
    )
    db.add(user_message)
    
    # 更新对话的更新时间
    conversation.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(user_message)
    
    # 调用AI服务获取回复
    assistant_content, assistant_content_type, assistant_metadata = _generate_ai_response(
        db=db,
        hospital_id=hospital_id,
        conversation_type=conversation.conversation_type,
        user_content=data.content,
    )
    
    # 创建AI回复消息
    assistant_message = ConversationMessage(
        conversation_id=conversation_id,
        role=MessageRole.ASSISTANT,
        content=assistant_content,
        content_type=assistant_content_type,
        message_metadata=assistant_metadata,
    )
    db.add(assistant_message)
    db.commit()
    db.refresh(assistant_message)
    
    logger.info(f"发送消息: conversation_id={conversation_id}, "
                f"user_message_id={user_message.id}, assistant_message_id={assistant_message.id}")
    
    # 构建响应
    response = SendMessageResponse(
        user_message=_build_message_response(user_message),
        assistant_message=_build_message_response(assistant_message),
    )
    
    return {
        "code": 200,
        "message": "发送成功",
        "data": response.model_dump(),
    }


def _generate_ai_response(
    db: Session,
    hospital_id: int,
    conversation_type: str,
    user_content: str,
) -> tuple:
    """
    调用AI服务生成回复
    
    Args:
        db: 数据库会话
        hospital_id: 医疗机构ID
        conversation_type: 对话类型
        user_content: 用户消息内容
        
    Returns:
        (content, content_type, metadata)
    """
    try:
        if conversation_type == "caliber":
            # 指标口径查询
            return _handle_caliber_query(db, hospital_id, user_content)
        elif conversation_type == "data":
            # 数据智能查询 - 暂未实现
            return _handle_data_query(db, hospital_id, user_content)
        elif conversation_type == "sql":
            # SQL代码编写
            return _handle_sql_query(db, hospital_id, user_content)
        else:
            return (
                f"收到您的消息：{user_content}\n\n暂不支持此类型的对话。",
                ContentType.TEXT,
                None,
            )
    except Exception as e:
        logger.error(f"AI响应生成失败: {str(e)}", exc_info=True)
        return (
            f"处理您的请求时发生错误：{str(e)}",
            ContentType.ERROR,
            {"error": str(e)},
        )


def _handle_caliber_query(
    db: Session,
    hospital_id: int,
    user_content: str,
) -> tuple:
    """
    处理指标口径查询
    
    直接在指标资产中搜索，不依赖 AI
    需求 3.1, 3.2, 3.4
    """
    try:
        # 直接在指标资产中搜索
        search_results = MetricCaliberService.search_metrics(
            db=db,
            hospital_id=hospital_id,
            keyword=user_content,
            limit=20,
        )
        
        if search_results:
            # 构建友好的响应
            response_parts = [f"## 指标口径查询结果\n"]
            response_parts.append(f"查询关键词：**{user_content}**\n")
            response_parts.append(f"找到 **{len(search_results)}** 个相关指标：\n")
            
            # 使用详细列表格式展示
            response_parts.append(MetricCaliberService.format_results_as_detailed_list(search_results))
            
            response = "\n".join(response_parts)
            
            metadata = {
                "query": user_content,
                "result_count": len(search_results),
                "metrics": [r.to_dict() for r in search_results],
            }
            return response, ContentType.TEXT, metadata
        else:
            # 无搜索结果，建议替代词
            suggestions = MetricCaliberService.suggest_alternative_keywords(
                db=db,
                hospital_id=hospital_id,
                original_keyword=user_content,
            )
            
            response_parts = [f"## 指标口径查询结果\n"]
            response_parts.append(f"查询关键词：**{user_content}**\n")
            response_parts.append("未找到匹配的指标。\n")
            
            if suggestions:
                response_parts.append("### 您可以尝试以下搜索词：\n")
                for s in suggestions:
                    response_parts.append(f"- {s}")
            else:
                response_parts.append("### 建议：\n")
                response_parts.append("- 尝试使用更通用的关键词")
                response_parts.append("- 检查是否有拼写错误")
                response_parts.append("- 使用指标的中文名称进行搜索")
            
            response = "\n".join(response_parts)
            return response, ContentType.TEXT, {"query": user_content, "result_count": 0}
            
    except Exception as e:
        logger.error(f"指标口径查询服务错误: {str(e)}", exc_info=True)
        return (
            f"## 指标口径查询失败\n\n查询关键词：**{user_content}**\n\n错误信息：{str(e)}",
            ContentType.ERROR,
            {"error": str(e)},
        )


def _handle_data_query(
    db: Session,
    hospital_id: int,
    user_content: str,
) -> tuple:
    """
    处理数据智能查询
    
    需求 4.1, 4.2, 4.3
    
    注：数据查询功能需要执行SQL并返回结果，暂未完全实现
    """
    # 暂时返回提示信息
    return (
        f"【数据智能查询】\n\n您查询的内容：{user_content}\n\n"
        "数据智能查询功能正在开发中，敬请期待。\n\n"
        "该功能将支持：\n"
        "- 自然语言转SQL查询\n"
        "- 自动执行查询并返回结果\n"
        "- 智能推荐可视化图表",
        ContentType.TEXT,
        {"query": user_content, "feature_pending": True},
    )


def _handle_sql_query(
    db: Session,
    hospital_id: int,
    user_content: str,
) -> tuple:
    """
    处理SQL代码编写请求
    
    需求 5.1, 5.2
    """
    try:
        # 调用SQL生成服务
        result = SQLGenerationService.generate_sql_from_description(
            db=db,
            hospital_id=hospital_id,
            user_description=user_content,
        )
        
        # 构建响应
        response_parts = ["【SQL代码编写】\n"]
        
        if result.explanation:
            response_parts.append(result.explanation)
            response_parts.append("")
        
        if result.sql_code:
            response_parts.append("```sql")
            response_parts.append(result.sql_code)
            response_parts.append("```")
        
        if result.warnings:
            response_parts.append("\n**注意事项：**")
            for w in result.warnings:
                response_parts.append(f"- {w}")
        
        if result.suggestions:
            response_parts.append("\n**优化建议：**")
            for s in result.suggestions:
                response_parts.append(f"- {s}")
        
        response = "\n".join(response_parts)
        
        # 构建元数据
        metadata = {
            "request": user_content,
            "sql_code": result.sql_code,
            "metric_name": result.metric_name,
            "metric_id": result.metric_id,
            "warnings": result.warnings,
            "suggestions": result.suggestions,
        }
        
        # 如果有SQL代码，使用code类型
        content_type = ContentType.CODE if result.sql_code else ContentType.TEXT
        
        return response, content_type, metadata
        
    except SQLAINotConfiguredError as e:
        logger.warning(f"SQL代码编写AI未配置: {str(e)}")
        return (
            f"【SQL代码编写】\n\n您的需求：{user_content}\n\n"
            f"无法生成SQL代码：{str(e)}\n\n"
            "请先在系统设置中配置AI接口，并将其关联到「智能问数-SQL代码编写」模块。",
            ContentType.TEXT,
            {"request": user_content, "ai_unavailable": True},
        )
        
    except SQLGenerationServiceError as e:
        logger.error(f"SQL代码生成服务错误: {str(e)}")
        return (
            f"【SQL代码编写】\n\n您的需求：{user_content}\n\n生成失败：{str(e)}",
            ContentType.ERROR,
            {"error": str(e)},
        )


def _generate_placeholder_response(conversation_type: str, user_content: str) -> str:
    """
    生成占位符回复（已废弃，保留用于兼容）
    """
    if conversation_type == "caliber":
        return f"【指标口径查询】\n\n您查询的内容：{user_content}\n\n抱歉，AI服务尚未集成。请稍后再试。"
    elif conversation_type == "data":
        return f"【数据智能查询】\n\n您查询的内容：{user_content}\n\n抱歉，AI服务尚未集成。请稍后再试。"
    elif conversation_type == "sql":
        return f"【SQL代码编写】\n\n您的需求：{user_content}\n\n抱歉，AI服务尚未集成。请稍后再试。"
    else:
        return f"收到您的消息：{user_content}\n\n抱歉，AI服务尚未集成。请稍后再试。"


@router.get("/{conversation_id}/messages", response_model=dict)
def list_messages(
    conversation_id: int,
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(50, ge=1, le=200, description="每页数量"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    获取对话消息列表（分页）
    
    用于加载更多历史消息。
    """
    hospital_id = require_hospital_id()
    
    # 验证对话存在
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.hospital_id == hospital_id
    ).first()
    
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="对话不存在"
        )
    
    # 统计总数
    total = db.query(func.count(ConversationMessage.id)).filter(
        ConversationMessage.conversation_id == conversation_id
    ).scalar() or 0
    
    # 分页查询，按创建时间正序
    messages = db.query(ConversationMessage).filter(
        ConversationMessage.conversation_id == conversation_id
    ).order_by(
        ConversationMessage.created_at.asc()
    ).offset((page - 1) * size).limit(size).all()
    
    items = [_build_message_response(m) for m in messages]
    
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



@router.post("/{conversation_id}/messages/{message_id}/export")
def export_message(
    conversation_id: int,
    message_id: int,
    data: MessageExportRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    导出消息内容
    
    支持导出格式：
    - markdown: Markdown格式，适用于指标口径查询结果
    - pdf: PDF格式，适用于指标口径查询结果
    - excel: Excel格式，适用于数据智能查询结果（表格数据）
    - csv: CSV格式，适用于数据智能查询结果（表格数据）
    
    需求 3.3: 当用户请求下载结果时，智能数据问答模块应生成并下载Markdown或PDF格式的结果文件
    需求 4.4: 当用户请求下载结果时，智能数据问答模块应生成并下载Excel或CSV格式的数据文件
    需求 12.1: 当用户导出指标口径结果时，智能数据问答模块应生成带有格式化表格的Markdown文件
    需求 12.2: 当用户将指标口径结果导出为PDF时，智能数据问答模块应生成格式正确的PDF文档
    需求 12.3: 当用户将查询数据导出为Excel时，智能数据问答模块应生成包含数据和列标题的Excel文件
    需求 12.4: 当用户将查询数据导出为CSV时，智能数据问答模块应生成UTF-8编码的CSV文件
    """
    hospital_id = require_hospital_id()
    
    # 验证对话存在
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.hospital_id == hospital_id
    ).first()
    
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="对话不存在"
        )
    
    # 获取消息
    message = db.query(ConversationMessage).filter(
        ConversationMessage.id == message_id,
        ConversationMessage.conversation_id == conversation_id
    ).first()
    
    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="消息不存在"
        )
    
    # 验证导出格式与内容类型的兼容性
    export_format = data.format
    content_type = message.content_type
    
    # Excel和CSV只支持表格数据
    if export_format in ["excel", "csv"] and content_type != "table":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"{export_format.upper()}格式仅支持表格数据导出"
        )
    
    # 错误类型不支持导出
    if content_type == "error":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="错误消息不支持导出"
        )
    
    try:
        # 生成导出文件
        file_data, file_ext, mime_type = ConversationExportService.export_message(
            content=message.content,
            content_type=content_type,
            export_format=export_format,
            metadata=message.message_metadata,
            title=conversation.title
        )
        
        # 生成文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"导出_{conversation.title}_{timestamp}{file_ext}"
        
        # 返回文件流
        return StreamingResponse(
            file_data,
            media_type=mime_type,
            headers={
                "Content-Disposition": f"attachment; filename*=UTF-8''{quote(filename)}"
            }
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"导出消息失败: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"导出失败: {str(e)}"
        )
