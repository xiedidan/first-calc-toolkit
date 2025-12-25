"""
SQL代码生成服务 - 智能问数系统
负责基于指标定义生成SQL代码

需求 5.1: 当用户选择"SQL代码编写"对话类型并请求为现有指标生成SQL时，智能数据问答模块应基于指标定义生成SQL代码
需求 5.2: 当用户用自然语言定义新指标时，智能数据问答模块应解析定义并生成相应的SQL代码
"""
import json
import logging
from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.models import Metric, MetricTopic, MetricProject, AIInterface, AIPromptModule, DataSource
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


class SQLGenerationServiceError(Exception):
    """SQL生成服务错误基类"""
    pass


class MetricNotFoundError(SQLGenerationServiceError):
    """未找到指标错误"""
    pass


class AINotConfiguredError(SQLGenerationServiceError):
    """AI未配置错误"""
    pass


class SQLGenerationResult:
    """SQL生成结果"""
    
    def __init__(
        self,
        sql_code: str,
        explanation: str,
        metric_name: Optional[str] = None,
        metric_id: Optional[int] = None,
        warnings: Optional[List[str]] = None,
        suggestions: Optional[List[str]] = None,
    ):
        self.sql_code = sql_code
        self.explanation = explanation
        self.metric_name = metric_name
        self.metric_id = metric_id
        self.warnings = warnings or []
        self.suggestions = suggestions or []
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "sql_code": self.sql_code,
            "explanation": self.explanation,
            "metric_name": self.metric_name,
            "metric_id": self.metric_id,
            "warnings": self.warnings,
            "suggestions": self.suggestions,
        }


class SQLGenerationService:
    """SQL代码生成服务"""
    
    @staticmethod
    def get_metric_definition(
        db: Session,
        hospital_id: int,
        metric_id: int,
    ) -> Optional[Dict[str, Any]]:
        """
        获取指标定义信息
        
        Args:
            db: 数据库会话
            hospital_id: 医疗机构ID
            metric_id: 指标ID
            
        Returns:
            指标定义字典，如果不存在返回None
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
        
        return {
            "id": metric.id,
            "name_cn": metric.name_cn,
            "name_en": metric.name_en,
            "metric_type": metric.metric_type,
            "metric_level": metric.metric_level,
            "business_caliber": metric.business_caliber,
            "technical_caliber": metric.technical_caliber,
            "source_table": metric.source_table,
            "dimensions": dimensions,
            "dimension_tables": dimension_tables,
            "project_name": metric.topic.project.name if metric.topic and metric.topic.project else None,
            "topic_name": metric.topic.name if metric.topic else None,
        }
    
    @staticmethod
    def search_metrics_by_name(
        db: Session,
        hospital_id: int,
        keyword: str,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        """
        根据名称搜索指标
        
        Args:
            db: 数据库会话
            hospital_id: 医疗机构ID
            keyword: 搜索关键词
            limit: 返回结果数量限制
            
        Returns:
            指标定义列表
        """
        if not keyword or not keyword.strip():
            return []
        
        keyword = keyword.strip()
        keyword_filter = f"%{keyword}%"
        
        metrics = db.query(Metric).join(
            MetricTopic, Metric.topic_id == MetricTopic.id
        ).join(
            MetricProject, MetricTopic.project_id == MetricProject.id
        ).filter(
            MetricProject.hospital_id == hospital_id
        ).filter(
            or_(
                Metric.name_cn.ilike(keyword_filter),
                Metric.name_en.ilike(keyword_filter),
            )
        ).order_by(
            Metric.sort_order,
            Metric.id
        ).limit(limit).all()
        
        results = []
        for metric in metrics:
            results.append(SQLGenerationService.get_metric_definition(
                db, hospital_id, metric.id
            ))
        
        return [r for r in results if r is not None]
    
    @staticmethod
    def get_schema_context(
        db: Session,
        hospital_id: int,
        table_names: Optional[List[str]] = None,
    ) -> str:
        """
        获取数据库表结构上下文
        
        Args:
            db: 数据库会话
            hospital_id: 医疗机构ID
            table_names: 指定的表名列表，如果为None则返回通用上下文
            
        Returns:
            表结构描述字符串
        """
        # 获取数据源信息
        data_sources = db.query(DataSource).filter(
            DataSource.is_enabled == True
        ).all()
        
        if not data_sources:
            return "暂无可用的数据源配置。"
        
        context_parts = []
        
        for ds in data_sources:
            context_parts.append(f"数据源: {ds.name}")
            context_parts.append(f"  数据库类型: {ds.db_type}")
            context_parts.append(f"  数据库名: {ds.database_name}")
            if ds.schema_name:
                context_parts.append(f"  Schema: {ds.schema_name}")
            context_parts.append("")
        
        # 添加常用表结构说明（基于项目实际情况）
        context_parts.append("常用业务表结构:")
        context_parts.append("")
        context_parts.append("1. charge_details (收费明细表)")
        context_parts.append("   - id: 主键")
        context_parts.append("   - hospital_id: 医疗机构ID")
        context_parts.append("   - charge_date: 收费日期")
        context_parts.append("   - department_code: 科室编码")
        context_parts.append("   - item_code: 项目编码")
        context_parts.append("   - item_name: 项目名称")
        context_parts.append("   - amount: 金额")
        context_parts.append("   - quantity: 数量")
        context_parts.append("   - business_type: 业务类型(门诊/住院)")
        context_parts.append("")
        context_parts.append("2. departments (科室表)")
        context_parts.append("   - id: 主键")
        context_parts.append("   - hospital_id: 医疗机构ID")
        context_parts.append("   - code: 科室编码")
        context_parts.append("   - name: 科室名称")
        context_parts.append("")
        context_parts.append("3. calculation_results (计算结果表)")
        context_parts.append("   - id: 主键")
        context_parts.append("   - task_id: 任务ID")
        context_parts.append("   - node_id: 节点ID")
        context_parts.append("   - node_code: 节点编码")
        context_parts.append("   - department_code: 科室编码")
        context_parts.append("   - workload: 工作量")
        context_parts.append("   - weight: 权重")
        context_parts.append("   - value: 业务价值")
        context_parts.append("")
        
        return "\n".join(context_parts)
    
    @staticmethod
    def build_metric_definition_context(metric_def: Dict[str, Any]) -> str:
        """
        构建指标定义上下文
        
        Args:
            metric_def: 指标定义字典
            
        Returns:
            格式化的指标定义字符串
        """
        if not metric_def:
            return "无指标定义信息"
        
        parts = []
        parts.append(f"指标名称: {metric_def.get('name_cn', '未知')}")
        
        if metric_def.get('name_en'):
            parts.append(f"英文名称: {metric_def['name_en']}")
        
        parts.append(f"指标类型: {metric_def.get('metric_type', '未知')}")
        
        if metric_def.get('metric_level'):
            parts.append(f"指标层级: {metric_def['metric_level']}")
        
        if metric_def.get('business_caliber'):
            parts.append(f"业务口径: {metric_def['business_caliber']}")
        
        if metric_def.get('technical_caliber'):
            parts.append(f"技术口径: {metric_def['technical_caliber']}")
        
        if metric_def.get('source_table'):
            parts.append(f"源表: {metric_def['source_table']}")
        
        if metric_def.get('dimensions'):
            parts.append(f"维度: {', '.join(metric_def['dimensions'])}")
        
        if metric_def.get('dimension_tables'):
            parts.append(f"维表: {', '.join(metric_def['dimension_tables'])}")
        
        if metric_def.get('project_name'):
            parts.append(f"所属项目: {metric_def['project_name']}")
        
        if metric_def.get('topic_name'):
            parts.append(f"所属主题: {metric_def['topic_name']}")
        
        return "\n".join(parts)
    
    @staticmethod
    def generate_sql_for_metric(
        db: Session,
        hospital_id: int,
        metric_id: int,
        additional_requirements: Optional[str] = None,
    ) -> SQLGenerationResult:
        """
        为现有指标生成SQL代码
        
        需求 5.1: 基于指标定义生成SQL代码
        
        Args:
            db: 数据库会话
            hospital_id: 医疗机构ID
            metric_id: 指标ID
            additional_requirements: 额外需求说明
            
        Returns:
            SQL生成结果
            
        Raises:
            MetricNotFoundError: 指标不存在
            AINotConfiguredError: AI未配置
            SQLGenerationServiceError: 其他服务错误
        """
        # 获取指标定义
        metric_def = SQLGenerationService.get_metric_definition(db, hospital_id, metric_id)
        if not metric_def:
            raise MetricNotFoundError(f"指标ID {metric_id} 不存在")
        
        # 构建用户请求
        user_request = f"请为指标「{metric_def['name_cn']}」生成SQL代码"
        if additional_requirements:
            user_request += f"\n\n额外需求：{additional_requirements}"
        
        # 调用AI生成
        return SQLGenerationService._generate_sql_with_ai(
            db=db,
            hospital_id=hospital_id,
            user_request=user_request,
            metric_definition=SQLGenerationService.build_metric_definition_context(metric_def),
            metric_name=metric_def['name_cn'],
            metric_id=metric_id,
        )
    
    @staticmethod
    def generate_sql_from_description(
        db: Session,
        hospital_id: int,
        user_description: str,
    ) -> SQLGenerationResult:
        """
        根据自然语言描述生成SQL代码
        
        需求 5.2: 解析用户定义并生成相应的SQL代码
        
        Args:
            db: 数据库会话
            hospital_id: 医疗机构ID
            user_description: 用户的自然语言描述
            
        Returns:
            SQL生成结果
            
        Raises:
            AINotConfiguredError: AI未配置
            SQLGenerationServiceError: 其他服务错误
        """
        # 尝试从描述中提取可能的指标名称并搜索
        related_metrics = SQLGenerationService.search_metrics_by_name(
            db, hospital_id, user_description, limit=5
        )
        
        # 构建指标上下文
        metric_context = ""
        if related_metrics:
            metric_context = "相关的已有指标定义：\n\n"
            for i, m in enumerate(related_metrics, 1):
                metric_context += f"{i}. {m['name_cn']}\n"
                if m.get('business_caliber'):
                    metric_context += f"   业务口径: {m['business_caliber']}\n"
                if m.get('source_table'):
                    metric_context += f"   源表: {m['source_table']}\n"
                metric_context += "\n"
        
        # 调用AI生成
        return SQLGenerationService._generate_sql_with_ai(
            db=db,
            hospital_id=hospital_id,
            user_request=user_description,
            metric_definition=metric_context if metric_context else "用户定义的新指标，无现有指标参考",
            metric_name=None,
            metric_id=None,
        )
    
    @staticmethod
    def _generate_sql_with_ai(
        db: Session,
        hospital_id: int,
        user_request: str,
        metric_definition: str,
        metric_name: Optional[str] = None,
        metric_id: Optional[int] = None,
    ) -> SQLGenerationResult:
        """
        使用AI生成SQL代码
        
        Args:
            db: 数据库会话
            hospital_id: 医疗机构ID
            user_request: 用户请求
            metric_definition: 指标定义上下文
            metric_name: 指标名称（可选）
            metric_id: 指标ID（可选）
            
        Returns:
            SQL生成结果
            
        Raises:
            AINotConfiguredError: AI未配置
            SQLGenerationServiceError: 其他服务错误
        """
        # 检查模块是否已配置AI接口
        is_ready, error_msg = AIPromptModuleService.check_module_ready(
            db, hospital_id, PromptModuleCode.QUERY_SQL
        )
        if not is_ready:
            raise AINotConfiguredError(error_msg)
        
        # 获取模块配置
        module = AIPromptModuleService.get_module_config(
            db, hospital_id, PromptModuleCode.QUERY_SQL
        )
        if not module:
            raise AINotConfiguredError("SQL代码编写模块配置不存在")
        
        # 获取AI接口配置
        ai_interface = db.query(AIInterface).filter(
            AIInterface.id == module.ai_interface_id
        ).first()
        if not ai_interface:
            raise AINotConfiguredError("AI接口配置不存在")
        
        # 获取表结构上下文
        schema_context = SQLGenerationService.get_schema_context(db, hospital_id)
        
        # 渲染提示词
        user_prompt = module.user_prompt
        user_prompt = user_prompt.replace("{user_request}", user_request)
        user_prompt = user_prompt.replace("{metric_definition}", metric_definition)
        user_prompt = user_prompt.replace("{schema_context}", schema_context)
        
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
                timeout=90.0,  # SQL生成可能需要更长时间
            )
            
            # 解析AI响应
            sql_code, explanation, warnings, suggestions = SQLGenerationService._parse_ai_response(
                ai_response
            )
            
            logger.info(f"SQL代码生成成功: request='{user_request[:50]}...', hospital_id={hospital_id}")
            
            return SQLGenerationResult(
                sql_code=sql_code,
                explanation=explanation,
                metric_name=metric_name,
                metric_id=metric_id,
                warnings=warnings,
                suggestions=suggestions,
            )
            
        except (AIConnectionError, AIResponseError, AIRateLimitError) as e:
            logger.error(f"AI调用失败: {str(e)}")
            # 返回降级响应
            return SQLGenerationService._generate_fallback_response(
                user_request, metric_definition, str(e)
            )
        except Exception as e:
            logger.error(f"SQL代码生成异常: {str(e)}", exc_info=True)
            raise SQLGenerationServiceError(f"生成失败: {str(e)}")
    
    @staticmethod
    def _parse_ai_response(
        response: str,
    ) -> Tuple[str, str, List[str], List[str]]:
        """
        解析AI响应，提取SQL代码和说明
        
        Args:
            response: AI响应文本
            
        Returns:
            (sql_code, explanation, warnings, suggestions)
        """
        sql_code = ""
        explanation = ""
        warnings = []
        suggestions = []
        
        # 尝试提取SQL代码块
        import re
        
        # 匹配 ```sql ... ``` 或 ``` ... ``` 代码块
        sql_pattern = r'```(?:sql)?\s*\n?(.*?)\n?```'
        sql_matches = re.findall(sql_pattern, response, re.DOTALL | re.IGNORECASE)
        
        if sql_matches:
            # 取最长的SQL代码块（通常是主要的SQL）
            sql_code = max(sql_matches, key=len).strip()
        
        # 提取代码块之外的文本作为说明
        explanation_text = re.sub(sql_pattern, '', response, flags=re.DOTALL | re.IGNORECASE).strip()
        
        # 分析说明文本，提取警告和建议
        lines = explanation_text.split('\n')
        current_section = "explanation"
        explanation_lines = []
        
        for line in lines:
            line_lower = line.lower().strip()
            
            if '警告' in line or 'warning' in line_lower or '注意' in line:
                current_section = "warnings"
                continue
            elif '建议' in line or 'suggestion' in line_lower or '优化' in line:
                current_section = "suggestions"
                continue
            
            line_stripped = line.strip()
            if line_stripped:
                if current_section == "warnings":
                    # 移除列表标记
                    cleaned = re.sub(r'^[-*•]\s*', '', line_stripped)
                    if cleaned:
                        warnings.append(cleaned)
                elif current_section == "suggestions":
                    cleaned = re.sub(r'^[-*•]\s*', '', line_stripped)
                    if cleaned:
                        suggestions.append(cleaned)
                else:
                    explanation_lines.append(line)
        
        explanation = '\n'.join(explanation_lines).strip()
        
        # 如果没有提取到SQL代码，将整个响应作为说明
        if not sql_code:
            explanation = response
        
        return sql_code, explanation, warnings, suggestions
    
    @staticmethod
    def _generate_fallback_response(
        user_request: str,
        metric_definition: str,
        error_message: str,
    ) -> SQLGenerationResult:
        """
        生成降级响应（AI不可用时）
        
        Args:
            user_request: 用户请求
            metric_definition: 指标定义
            error_message: 错误信息
            
        Returns:
            降级的SQL生成结果
        """
        explanation = f"""AI服务暂时不可用（{error_message}），无法自动生成SQL代码。

根据您的需求：
{user_request}

指标信息：
{metric_definition}

建议您：
1. 稍后重试
2. 参考指标的技术口径手动编写SQL
3. 联系系统管理员检查AI服务配置"""
        
        return SQLGenerationResult(
            sql_code="-- AI服务暂时不可用，请稍后重试",
            explanation=explanation,
            warnings=["AI服务不可用"],
            suggestions=["稍后重试", "手动编写SQL", "检查AI配置"],
        )
    
    @staticmethod
    def optimize_sql(
        db: Session,
        hospital_id: int,
        sql_code: str,
        optimization_goals: Optional[str] = None,
    ) -> SQLGenerationResult:
        """
        优化SQL代码
        
        需求 5.4: 分析并建议优化后的SQL代码
        
        Args:
            db: 数据库会话
            hospital_id: 医疗机构ID
            sql_code: 原始SQL代码
            optimization_goals: 优化目标说明
            
        Returns:
            优化后的SQL生成结果
            
        Raises:
            AINotConfiguredError: AI未配置
            SQLGenerationServiceError: 其他服务错误
        """
        user_request = f"请优化以下SQL代码：\n\n```sql\n{sql_code}\n```"
        if optimization_goals:
            user_request += f"\n\n优化目标：{optimization_goals}"
        else:
            user_request += "\n\n请从性能、可读性、可维护性等方面进行优化。"
        
        return SQLGenerationService._generate_sql_with_ai(
            db=db,
            hospital_id=hospital_id,
            user_request=user_request,
            metric_definition="SQL优化请求，无特定指标定义",
        )
    
    @staticmethod
    def explain_sql(
        db: Session,
        hospital_id: int,
        sql_code: str,
    ) -> str:
        """
        解释SQL代码
        
        Args:
            db: 数据库会话
            hospital_id: 医疗机构ID
            sql_code: SQL代码
            
        Returns:
            SQL解释文本
            
        Raises:
            AINotConfiguredError: AI未配置
            SQLGenerationServiceError: 其他服务错误
        """
        # 检查模块是否已配置AI接口
        is_ready, error_msg = AIPromptModuleService.check_module_ready(
            db, hospital_id, PromptModuleCode.QUERY_SQL
        )
        if not is_ready:
            raise AINotConfiguredError(error_msg)
        
        # 获取模块配置
        module = AIPromptModuleService.get_module_config(
            db, hospital_id, PromptModuleCode.QUERY_SQL
        )
        if not module:
            raise AINotConfiguredError("SQL代码编写模块配置不存在")
        
        # 获取AI接口配置
        ai_interface = db.query(AIInterface).filter(
            AIInterface.id == module.ai_interface_id
        ).first()
        if not ai_interface:
            raise AINotConfiguredError("AI接口配置不存在")
        
        system_prompt = """你是一个SQL专家。你的任务是解释SQL代码的逻辑和功能。

解释要求：
1. 逐步分析SQL的各个部分
2. 说明每个子查询/CTE的作用
3. 解释JOIN条件和过滤条件
4. 指出可能的性能问题
5. 使用通俗易懂的语言"""
        
        user_prompt = f"""请解释以下SQL代码：

```sql
{sql_code}
```

请从以下方面进行解释：
1. 整体功能概述
2. 数据来源和表关系
3. 过滤条件说明
4. 聚合和计算逻辑
5. 输出结果说明"""
        
        try:
            api_key = decrypt_api_key(ai_interface.api_key_encrypted)
            
            explanation = call_ai_text_generation(
                api_endpoint=ai_interface.api_endpoint,
                api_key=api_key,
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                model_name=ai_interface.model_name,
                timeout=60.0,
            )
            
            logger.info(f"SQL解释生成成功: hospital_id={hospital_id}")
            return explanation
            
        except (AIConnectionError, AIResponseError, AIRateLimitError) as e:
            logger.error(f"AI调用失败: {str(e)}")
            return f"AI服务暂时不可用（{str(e)}），无法生成SQL解释。"
        except Exception as e:
            logger.error(f"SQL解释生成异常: {str(e)}", exc_info=True)
            raise SQLGenerationServiceError(f"解释生成失败: {str(e)}")
