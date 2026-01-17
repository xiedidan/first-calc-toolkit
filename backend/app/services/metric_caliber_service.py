"""
指标口径查询服务 - 智能问数系统
负责指标搜索和口径查询逻辑

需求 3.1: 当用户选择"指标口径查询"对话类型并发送查询时，智能数据问答模块应搜索相关指标并以表格形式返回结果
需求 3.2: 当系统返回指标口径结果时，智能数据问答模块应在结构化表格中显示指标名称、口径定义、源表和相关维度
需求 3.4: 当未找到匹配的指标时，智能数据问答模块应显示无结果消息并建议替代搜索词
"""
import json
import logging
from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import or_, func

from app.models import Metric, MetricTopic, MetricProject, AIInterface, AIPromptModule
from app.models.ai_prompt_module import PromptModuleCode
from app.services.ai_prompt_module_service import AIPromptModuleService
from app.utils.ai_interface import (
    call_ai_text_generation,
    AIConnectionError,
    AIResponseError,
    AIRateLimitError,
)
from app.utils.encryption import decrypt_api_key

logger = logging.getLogger(__name__)


class MetricCaliberServiceError(Exception):
    """指标口径服务错误基类"""
    pass


class MetricNotFoundError(MetricCaliberServiceError):
    """未找到指标错误"""
    pass


class AINotConfiguredError(MetricCaliberServiceError):
    """AI未配置错误"""
    pass


class MetricCaliberResult:
    """指标口径查询结果"""
    
    def __init__(
        self,
        metric_id: int,
        metric_name: str,
        business_caliber: Optional[str],
        technical_caliber: Optional[str],
        source_tables: Optional[List[str]],
        dimensions: Optional[List[str]],
        dimension_tables: Optional[List[str]],
        project_name: Optional[str],
        topic_name: Optional[str],
        metric_type: str,
        metric_level: Optional[str],
    ):
        self.metric_id = metric_id
        self.metric_name = metric_name
        self.business_caliber = business_caliber
        self.technical_caliber = technical_caliber
        self.source_tables = source_tables or []
        self.dimensions = dimensions or []
        self.dimension_tables = dimension_tables or []
        self.project_name = project_name
        self.topic_name = topic_name
        self.metric_type = metric_type
        self.metric_level = metric_level
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "metric_id": self.metric_id,
            "metric_name": self.metric_name,
            "business_caliber": self.business_caliber,
            "technical_caliber": self.technical_caliber,
            "source_tables": self.source_tables,
            "dimensions": self.dimensions,
            "dimension_tables": self.dimension_tables,
            "project_name": self.project_name,
            "topic_name": self.topic_name,
            "metric_type": self.metric_type,
            "metric_level": self.metric_level,
        }


class MetricCaliberService:
    """指标口径查询服务"""
    
    # 指标类型显示名称映射
    METRIC_TYPE_DISPLAY = {
        "atomic": "原子指标",
        "composite": "复合指标",
    }
    
    @staticmethod
    def search_metrics(
        db: Session,
        hospital_id: int,
        keyword: str,
        limit: int = 20,
    ) -> List[MetricCaliberResult]:
        """
        搜索指标
        
        需求 3.1: 搜索相关指标
        
        Args:
            db: 数据库会话
            hospital_id: 医疗机构ID
            keyword: 搜索关键词
            limit: 返回结果数量限制
            
        Returns:
            指标口径结果列表
        """
        if not keyword or not keyword.strip():
            return []
        
        keyword = keyword.strip()
        keyword_filter = f"%{keyword}%"
        
        # 构建查询
        query = db.query(Metric).join(
            MetricTopic, Metric.topic_id == MetricTopic.id
        ).join(
            MetricProject, MetricTopic.project_id == MetricProject.id
        ).filter(
            MetricProject.hospital_id == hospital_id
        ).filter(
            or_(
                Metric.name_cn.ilike(keyword_filter),
                Metric.name_en.ilike(keyword_filter),
                Metric.business_caliber.ilike(keyword_filter),
                Metric.technical_caliber.ilike(keyword_filter),
            )
        ).order_by(
            Metric.sort_order,
            Metric.id
        ).limit(limit)
        
        metrics = query.all()
        
        results = []
        for metric in metrics:
            # 解析源表信息
            source_tables = []
            if metric.source_tables:
                if isinstance(metric.source_tables, list):
                    source_tables = metric.source_tables
                elif isinstance(metric.source_tables, str):
                    source_tables = [metric.source_tables]
            
            # 解析维度信息
            dimensions = []
            if metric.dimensions:
                if isinstance(metric.dimensions, list):
                    dimensions = metric.dimensions
                elif isinstance(metric.dimensions, dict):
                    dimensions = list(metric.dimensions.values())
            
            # 解析维表信息
            dimension_tables = []
            if metric.dimension_tables:
                if isinstance(metric.dimension_tables, list):
                    dimension_tables = metric.dimension_tables
                elif isinstance(metric.dimension_tables, dict):
                    dimension_tables = list(metric.dimension_tables.values())
            
            result = MetricCaliberResult(
                metric_id=metric.id,
                metric_name=metric.name_cn,
                business_caliber=metric.business_caliber,
                technical_caliber=metric.technical_caliber,
                source_tables=source_tables,
                dimensions=dimensions,
                dimension_tables=dimension_tables,
                project_name=metric.topic.project.name if metric.topic and metric.topic.project else None,
                topic_name=metric.topic.name if metric.topic else None,
                metric_type=MetricCaliberService.METRIC_TYPE_DISPLAY.get(
                    metric.metric_type, metric.metric_type
                ),
                metric_level=metric.metric_level,
            )
            results.append(result)
        
        logger.info(f"指标搜索: keyword='{keyword}', hospital_id={hospital_id}, found={len(results)}")
        return results
    
    @staticmethod
    def get_metric_by_id(
        db: Session,
        hospital_id: int,
        metric_id: int,
    ) -> Optional[MetricCaliberResult]:
        """
        根据ID获取指标口径信息
        
        Args:
            db: 数据库会话
            hospital_id: 医疗机构ID
            metric_id: 指标ID
            
        Returns:
            指标口径结果，如果不存在返回None
        """
        metric = db.query(Metric).join(
            MetricTopic, Metric.topic_id == MetricTopic.id
        ).join(
            MetricProject, MetricTopic.project_id == MetricProject.id
        ).filter(
            Metric.id == metric_id,
            MetricProject.hospital_id == hospital_id
        ).first()
        
        if not metric:
            return None
        
        # 解析源表信息
        source_tables = []
        if metric.source_tables:
            if isinstance(metric.source_tables, list):
                source_tables = metric.source_tables
            elif isinstance(metric.source_tables, str):
                source_tables = [metric.source_tables]
        
        # 解析维度信息
        dimensions = []
        if metric.dimensions:
            if isinstance(metric.dimensions, list):
                dimensions = metric.dimensions
            elif isinstance(metric.dimensions, dict):
                dimensions = list(metric.dimensions.values())
        
        # 解析维表信息
        dimension_tables = []
        if metric.dimension_tables:
            if isinstance(metric.dimension_tables, list):
                dimension_tables = metric.dimension_tables
            elif isinstance(metric.dimension_tables, dict):
                dimension_tables = list(metric.dimension_tables.values())
        
        return MetricCaliberResult(
            metric_id=metric.id,
            metric_name=metric.name_cn,
            business_caliber=metric.business_caliber,
            technical_caliber=metric.technical_caliber,
            source_tables=source_tables,
            dimensions=dimensions,
            dimension_tables=dimension_tables,
            project_name=metric.topic.project.name if metric.topic and metric.topic.project else None,
            topic_name=metric.topic.name if metric.topic else None,
            metric_type=MetricCaliberService.METRIC_TYPE_DISPLAY.get(
                metric.metric_type, metric.metric_type
            ),
            metric_level=metric.metric_level,
        )
    
    @staticmethod
    def format_results_as_table(results: List[MetricCaliberResult]) -> str:
        """
        将结果格式化为Markdown表格
        
        需求 3.2: 以表格形式返回结果
        
        Args:
            results: 指标口径结果列表
            
        Returns:
            Markdown格式的表格字符串
        """
        if not results:
            return "未找到匹配的指标。"
        
        # 构建表头
        table = "| 指标名称 | 业务口径 | 源表 | 相关维度 | 所属项目 | 所属主题 |\n"
        table += "|----------|----------|------|----------|----------|----------|\n"
        
        # 构建表格行
        for result in results:
            # 处理可能为空的字段
            business_caliber = result.business_caliber or "-"
            # 截断过长的口径描述
            if len(business_caliber) > 50:
                business_caliber = business_caliber[:47] + "..."
            
            source_tables = ", ".join(result.source_tables) if result.source_tables else "-"
            dimensions = ", ".join(result.dimensions) if result.dimensions else "-"
            project_name = result.project_name or "-"
            topic_name = result.topic_name or "-"
            
            # 转义表格中的特殊字符
            business_caliber = business_caliber.replace("|", "\\|").replace("\n", " ")
            
            table += f"| {result.metric_name} | {business_caliber} | {source_tables} | {dimensions} | {project_name} | {topic_name} |\n"
        
        return table
    
    @staticmethod
    def format_results_as_detailed_list(results: List[MetricCaliberResult]) -> str:
        """
        将结果格式化为详细列表
        
        Args:
            results: 指标口径结果列表
            
        Returns:
            Markdown格式的详细列表字符串
        """
        if not results:
            return "未找到匹配的指标。"
        
        output = []
        for i, result in enumerate(results, 1):
            output.append(f"### {i}. {result.metric_name}")
            output.append("")
            output.append(f"- **所属项目**: {result.project_name or '-'}")
            output.append(f"- **所属主题**: {result.topic_name or '-'}")
            output.append(f"- **指标类型**: {result.metric_type}")
            output.append(f"- **指标层级**: {result.metric_level or '-'}")
            output.append(f"- **业务口径**: {result.business_caliber or '-'}")
            output.append(f"- **技术口径**: {result.technical_caliber or '-'}")
            output.append(f"- **源表**: {', '.join(result.source_tables) if result.source_tables else '-'}")
            output.append(f"- **相关维度**: {', '.join(result.dimensions) if result.dimensions else '-'}")
            output.append(f"- **关联维表**: {', '.join(result.dimension_tables) if result.dimension_tables else '-'}")
            output.append("")
        
        return "\n".join(output)
    
    @staticmethod
    def suggest_alternative_keywords(
        db: Session,
        hospital_id: int,
        original_keyword: str,
    ) -> List[str]:
        """
        建议替代搜索词
        
        需求 3.4: 当未找到匹配的指标时，建议替代搜索词
        
        Args:
            db: 数据库会话
            hospital_id: 医疗机构ID
            original_keyword: 原始搜索关键词
            
        Returns:
            建议的替代搜索词列表
        """
        suggestions = []
        
        # 获取所有指标名称
        metric_names = db.query(Metric.name_cn).join(
            MetricTopic, Metric.topic_id == MetricTopic.id
        ).join(
            MetricProject, MetricTopic.project_id == MetricProject.id
        ).filter(
            MetricProject.hospital_id == hospital_id
        ).all()
        
        metric_names = [name[0] for name in metric_names if name[0]]
        
        # 简单的相似度匹配：查找包含原始关键词部分字符的指标名称
        original_chars = set(original_keyword)
        for name in metric_names:
            name_chars = set(name)
            # 计算字符重叠度
            overlap = len(original_chars & name_chars)
            if overlap >= len(original_keyword) * 0.3:  # 至少30%字符重叠
                suggestions.append(name)
        
        # 限制建议数量
        return suggestions[:5]
    
    @staticmethod
    def extract_keywords_with_ai(
        db: Session,
        hospital_id: int,
        user_query: str,
    ) -> List[str]:
        """
        使用AI从用户查询中提取搜索关键词
        
        Args:
            db: 数据库会话
            hospital_id: 医疗机构ID
            user_query: 用户查询内容
            
        Returns:
            提取的关键词列表，如果AI不可用则返回空列表
        """
        # 检查关键词提取模块是否已配置
        is_ready, _ = AIPromptModuleService.check_module_ready(
            db, hospital_id, PromptModuleCode.QUERY_KEYWORD
        )
        if not is_ready:
            logger.debug(f"关键词提取模块未配置，跳过AI提取: hospital_id={hospital_id}")
            return []
        
        # 获取模块配置
        module = AIPromptModuleService.get_module_config(
            db, hospital_id, PromptModuleCode.QUERY_KEYWORD
        )
        if not module:
            return []
        
        # 获取AI接口配置
        ai_interface = db.query(AIInterface).filter(
            AIInterface.id == module.ai_interface_id
        ).first()
        if not ai_interface:
            return []
        
        try:
            # 解密API密钥
            api_key = decrypt_api_key(ai_interface.api_key_encrypted)
            
            # 渲染提示词
            user_prompt = module.user_prompt.replace("{user_query}", user_query)
            system_prompt = module.system_prompt or ""
            
            # 调用AI
            ai_response = call_ai_text_generation(
                api_endpoint=ai_interface.api_endpoint,
                api_key=api_key,
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                model_name=ai_interface.model_name,
                temperature=module.temperature,
                timeout=60.0,  # 关键词提取应该较快
            )
            
            # 解析JSON响应
            # 尝试从响应中提取JSON
            response_text = ai_response.strip()
            
            # 处理可能的markdown代码块
            if "```json" in response_text:
                start = response_text.find("```json") + 7
                end = response_text.find("```", start)
                response_text = response_text[start:end].strip()
            elif "```" in response_text:
                start = response_text.find("```") + 3
                end = response_text.find("```", start)
                response_text = response_text[start:end].strip()
            
            result = json.loads(response_text)
            keywords = result.get("keywords", [])
            
            if keywords:
                logger.info(f"AI关键词提取成功: query='{user_query}' -> keywords={keywords}")
                return keywords[:3]  # 最多返回3个关键词
            
            return []
            
        except json.JSONDecodeError as e:
            logger.warning(f"AI关键词提取响应解析失败: {str(e)}, response={ai_response[:200] if ai_response else 'empty'}")
            return []
        except (AIConnectionError, AIResponseError, AIRateLimitError) as e:
            logger.warning(f"AI关键词提取调用失败: {str(e)}")
            return []
        except Exception as e:
            logger.warning(f"AI关键词提取异常: {str(e)}")
            return []
    
    @staticmethod
    def smart_search_metrics(
        db: Session,
        hospital_id: int,
        user_query: str,
        limit: int = 20,
    ) -> Tuple[List[MetricCaliberResult], List[str], str]:
        """
        智能搜索指标（先用AI提取关键词，再用关键词搜索）
        
        流程：
        1. 先尝试用AI提取关键词
        2. 如果提取成功，用关键词搜索
        3. 如果AI不可用或提取失败，回退到原始查询直接搜索
        
        Args:
            db: 数据库会话
            hospital_id: 医疗机构ID
            user_query: 用户查询内容
            limit: 返回结果数量限制
            
        Returns:
            (搜索结果列表, 使用的关键词列表, 原始查询)
        """
        used_keywords = []
        
        # 1. 先尝试用AI提取关键词
        extracted_keywords = MetricCaliberService.extract_keywords_with_ai(
            db, hospital_id, user_query
        )
        
        if extracted_keywords:
            # 用提取的关键词逐个搜索，合并结果
            all_results = []
            seen_ids = set()
            
            for keyword in extracted_keywords:
                keyword_results = MetricCaliberService.search_metrics(
                    db, hospital_id, keyword, limit
                )
                for r in keyword_results:
                    if r.metric_id not in seen_ids:
                        all_results.append(r)
                        seen_ids.add(r.metric_id)
                
                if keyword_results:
                    used_keywords.append(keyword)
            
            if all_results:
                logger.info(f"智能搜索成功: query='{user_query}' -> keywords={used_keywords}, found={len(all_results)}")
                return all_results[:limit], used_keywords, user_query
            
            # AI提取了关键词但搜索无结果，记录使用的关键词
            if not used_keywords:
                used_keywords = extracted_keywords
        
        # 2. AI不可用或关键词搜索无结果，回退到原始查询直接搜索
        results = MetricCaliberService.search_metrics(
            db, hospital_id, user_query, limit
        )
        
        if results:
            logger.info(f"直接搜索成功: query='{user_query}', found={len(results)}")
            # 如果之前AI提取了关键词但没搜到，这里用原始查询搜到了
            if used_keywords:
                # 保留AI提取的关键词信息，但标记是用原始查询搜到的
                return results, [user_query], user_query
            return results, [user_query], user_query
        
        # 3. 都没有结果
        return [], used_keywords or [user_query], user_query
    
    @staticmethod
    def query_with_ai(
        db: Session,
        hospital_id: int,
        user_query: str,
    ) -> Tuple[str, List[MetricCaliberResult]]:
        """
        使用AI进行指标口径查询
        
        需求 3.1, 3.2, 3.4: 完整的指标口径查询流程
        
        Args:
            db: 数据库会话
            hospital_id: 医疗机构ID
            user_query: 用户查询内容
            
        Returns:
            (AI响应文本, 相关指标列表)
            
        Raises:
            AINotConfiguredError: AI未配置
            MetricCaliberServiceError: 其他服务错误
        """
        # 检查模块是否已配置AI接口
        is_ready, error_msg = AIPromptModuleService.check_module_ready(
            db, hospital_id, PromptModuleCode.QUERY_CALIBER
        )
        if not is_ready:
            raise AINotConfiguredError(error_msg)
        
        # 获取模块配置
        module = AIPromptModuleService.get_module_config(
            db, hospital_id, PromptModuleCode.QUERY_CALIBER
        )
        if not module:
            raise AINotConfiguredError("指标口径查询模块配置不存在")
        
        # 获取AI接口配置
        ai_interface = db.query(AIInterface).filter(
            AIInterface.id == module.ai_interface_id
        ).first()
        if not ai_interface:
            raise AINotConfiguredError("AI接口配置不存在")
        
        # 先进行关键词搜索，获取相关指标
        search_results = MetricCaliberService.search_metrics(
            db, hospital_id, user_query, limit=10
        )
        
        # 构建指标上下文
        metrics_context = MetricCaliberService._build_metrics_context(search_results)
        
        # 渲染提示词
        user_prompt = module.user_prompt
        user_prompt = user_prompt.replace("{user_query}", user_query)
        user_prompt = user_prompt.replace("{metrics_context}", metrics_context)
        
        system_prompt = module.system_prompt or ""
        
        try:
            # 解密API密钥
            api_key = decrypt_api_key(ai_interface.api_key_encrypted)
            
            # 调用AI
            ai_response = call_ai_text_generation(
                api_endpoint=ai_interface.api_endpoint,
                api_key=api_key,
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                model_name=ai_interface.model_name,
                timeout=120.0,
            )
            
            logger.info(f"AI指标口径查询成功: query='{user_query}', hospital_id={hospital_id}")
            return ai_response, search_results
            
        except (AIConnectionError, AIResponseError, AIRateLimitError) as e:
            logger.error(f"AI调用失败: {str(e)}")
            # 如果AI调用失败，返回基于搜索结果的响应
            if search_results:
                fallback_response = MetricCaliberService._generate_fallback_response(
                    user_query, search_results
                )
                return fallback_response, search_results
            else:
                suggestions = MetricCaliberService.suggest_alternative_keywords(
                    db, hospital_id, user_query
                )
                return MetricCaliberService._generate_no_result_response(
                    user_query, suggestions
                ), []
        except Exception as e:
            logger.error(f"指标口径查询异常: {str(e)}", exc_info=True)
            raise MetricCaliberServiceError(f"查询失败: {str(e)}")
    
    @staticmethod
    def _build_metrics_context(results: List[MetricCaliberResult]) -> str:
        """
        构建指标上下文JSON
        
        Args:
            results: 指标口径结果列表
            
        Returns:
            JSON格式的指标上下文
        """
        if not results:
            return "[]"
        
        context = []
        for result in results:
            context.append({
                "id": result.metric_id,
                "name": result.metric_name,
                "business_caliber": result.business_caliber,
                "technical_caliber": result.technical_caliber,
                "source_tables": result.source_tables,
                "dimensions": result.dimensions,
                "dimension_tables": result.dimension_tables,
                "project": result.project_name,
                "topic": result.topic_name,
                "type": result.metric_type,
                "level": result.metric_level,
            })
        
        return json.dumps(context, ensure_ascii=False, indent=2)
    
    @staticmethod
    def _generate_fallback_response(
        user_query: str,
        results: List[MetricCaliberResult],
    ) -> str:
        """
        生成降级响应（AI不可用时）
        
        Args:
            user_query: 用户查询
            results: 搜索结果
            
        Returns:
            降级响应文本
        """
        output = [f"根据您的查询「{user_query}」，找到以下相关指标：\n"]
        output.append(MetricCaliberService.format_results_as_table(results))
        output.append("\n*注：AI服务暂时不可用，以上为基于关键词搜索的结果。*")
        return "\n".join(output)
    
    @staticmethod
    def _generate_no_result_response(
        user_query: str,
        suggestions: List[str],
    ) -> str:
        """
        生成无结果响应
        
        需求 3.4: 显示无结果消息并建议替代搜索词
        
        Args:
            user_query: 用户查询
            suggestions: 建议的替代搜索词
            
        Returns:
            无结果响应文本
        """
        output = [f"未找到与「{user_query}」匹配的指标。\n"]
        
        if suggestions:
            output.append("您可以尝试以下搜索词：")
            for suggestion in suggestions:
                output.append(f"- {suggestion}")
        else:
            output.append("建议：")
            output.append("- 尝试使用更通用的关键词")
            output.append("- 检查是否有拼写错误")
            output.append("- 使用指标的中文名称进行搜索")
        
        return "\n".join(output)
