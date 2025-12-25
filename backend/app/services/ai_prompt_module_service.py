"""
AI提示词模块服务 - 智能问数系统
负责提示词模块的初始化和管理
"""
import logging
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session

from app.models import AIPromptModule
from app.models.ai_prompt_module import PromptModuleCode

logger = logging.getLogger(__name__)


# 默认模块配置
DEFAULT_MODULES: List[Dict[str, Any]] = [
    {
        "module_code": PromptModuleCode.CLASSIFICATION,
        "module_name": "智能分类分级",
        "description": "用于收费项目的AI智能分类分级功能，根据项目名称自动推荐分类维度",
        "temperature": 0.3,
        "placeholders": [
            {"name": "items", "description": "待分类项目列表（JSON格式，包含id和name字段）"},
            {"name": "dimensions", "description": "可选维度列表（JSON格式，包含id、name、path字段）"},
        ],
        "system_prompt": """你是一个医技项目分类专家。请根据提供的医技项目列表和可选维度列表，为每个项目判断最适合归属的维度，并给出确信度（0-1之间的小数）。必须返回JSON格式：{"results": [{"item_id": <项目ID>, "dimension_id": <维度ID>, "confidence": <确信度>}, ...]}""",
        "user_prompt": """请为以下医技项目分类：

待分类项目列表：
{items}

可选维度列表：
{dimensions}

请返回JSON格式的分类结果。""",
    },
    {
        "module_code": PromptModuleCode.REPORT_ISSUES,
        "module_name": "业务价值报表-当前存在问题",
        "description": "用于生成业务价值报表中的'当前存在问题'分析内容",
        "temperature": 0.7,
        "placeholders": [
            {"name": "hospital_name", "description": "医院名称"},
            {"name": "hospital_desc", "description": "医院简介"},
            {"name": "department_name", "description": "科室名称"},
            {"name": "department_alignments", "description": "核算序列（如：医生、护理、医技）"},
            {"name": "period", "description": "统计周期（如：2025-01）"},
            {"name": "dept_main_services", "description": "科室主业（Top5维度及业务价值占比）"},
            {"name": "dept_work_substance", "description": "业务内涵（各维度Top5收费项目明细）"},
        ],
        "system_prompt": """你是一位资深的医院管理咨询专家，专注于科室运营分析和问题诊断。你需要根据提供的科室业务数据，分析该科室当前存在的问题和挑战。

请以专业、客观的角度进行分析，输出格式为Markdown，包含以下方面：
1. 业务结构问题（如业务单一、高价值业务占比低等）
2. 运营效率问题（如工作量与价值不匹配等）
3. 发展瓶颈（如技术能力、人才储备等）
4. 其他需要关注的问题

要求：
- 分析要具体、有针对性，避免泛泛而谈
- 结合数据进行分析，用数据说话
- 语言简洁专业，每个问题点控制在2-3句话
- 总字数控制在800字以内""",
        "user_prompt": """请分析以下科室当前存在的问题：

## 基本信息
- 医院名称：{hospital_name}
- 医院简介：{hospital_desc}
- 科室名称：{department_name}
- 核算序列：{department_alignments}
- 统计周期：{period}

## 业务数据
- 科室主业：{dept_main_services}
- 业务内涵：{dept_work_substance}

请基于以上信息，分析该科室当前存在的问题和挑战，输出Markdown格式的分析报告。""",
    },
    {
        "module_code": PromptModuleCode.REPORT_PLANS,
        "module_name": "业务价值报表-未来发展计划",
        "description": "用于生成业务价值报表中的'未来发展计划'建议内容",
        "temperature": 0.8,
        "placeholders": [
            {"name": "hospital_name", "description": "医院名称"},
            {"name": "hospital_desc", "description": "医院简介"},
            {"name": "department_name", "description": "科室名称"},
            {"name": "department_alignments", "description": "核算序列（如：医生、护理、医技）"},
            {"name": "period", "description": "统计周期（如：2025-01）"},
            {"name": "dept_main_services", "description": "科室主业（Top5维度及业务价值占比）"},
            {"name": "dept_work_substance", "description": "业务内涵（各维度Top5收费项目明细）"},
        ],
        "system_prompt": """你是一位资深的医院管理咨询专家，专注于科室发展规划和战略制定。你需要根据提供的科室业务数据，为该科室制定未来发展计划和建议。

请以专业、前瞻的角度进行规划，输出格式为Markdown，包含以下方面：
1. 业务发展方向（如拓展新业务、提升高价值业务占比等）
2. 能力建设计划（如技术提升、人才培养等）
3. 运营优化措施（如流程改进、效率提升等）
4. 短期目标（3-6个月）和中期目标（1-2年）

要求：
- 建议要具体可行，避免空洞的口号
- 结合科室实际情况，有针对性地提出建议
- 语言简洁专业，每个建议点控制在2-3句话
- 总字数控制在800字以内""",
        "user_prompt": """请为以下科室制定未来发展计划：

## 基本信息
- 医院名称：{hospital_name}
- 医院简介：{hospital_desc}
- 科室名称：{department_name}
- 核算序列：{department_alignments}
- 统计周期：{period}

## 业务数据
- 科室主业：{dept_main_services}
- 业务内涵：{dept_work_substance}

请基于以上信息，为该科室制定未来发展计划和建议，输出Markdown格式的规划报告。""",
    },
    {
        "module_code": PromptModuleCode.QUERY_CALIBER,
        "module_name": "智能问数-指标口径查询",
        "description": "用于智能问数系统中的指标口径查询功能，帮助用户理解指标定义",
        "temperature": 0.3,
        "placeholders": [
            {"name": "user_query", "description": "用户查询内容"},
            {"name": "metrics_context", "description": "相关指标信息JSON"},
        ],
        "system_prompt": """你是一个数据指标专家。你的任务是帮助用户理解数据指标的业务口径和技术实现。

回答要求：
1. 准确解释指标的业务含义
2. 说明计算公式和数据来源
3. 指出相关的维度和关联指标
4. 使用表格形式呈现结构化信息""",
        "user_prompt": """用户查询：{user_query}

相关指标信息：
{metrics_context}

请根据用户的查询，以表格形式返回相关指标的口径信息，包含：
- 指标名称
- 业务口径（业务定义和计算规则）
- 数据源表
- 相关维度

如果找到多个相关指标，请全部列出。如果没有找到匹配的指标，请说明并建议可能的替代搜索词。""",
    },
    {
        "module_code": PromptModuleCode.QUERY_KEYWORD,
        "module_name": "智能问数-指标关键字提取",
        "description": "用于从用户自然语言查询中提取指标搜索关键词，提高指标口径查询的准确性",
        "temperature": 0.1,
        "placeholders": [
            {"name": "user_query", "description": "用户查询内容"},
        ],
        "system_prompt": """你是一个关键词提取专家。你的任务是从用户的自然语言查询中提取用于搜索指标的关键词。

要求：
1. 提取与指标名称相关的核心词汇
2. 去除无关的修饰词（如"相关"、"有哪些"、"是什么"等）
3. 保留专业术语和业务词汇
4. 返回1-3个最相关的关键词
5. 必须返回JSON格式""",
        "user_prompt": """请从以下用户查询中提取指标搜索关键词：

用户查询：{user_query}

请返回JSON格式：
{{"keywords": ["关键词1", "关键词2"]}}

注意：
- 只提取与指标名称相关的核心词汇
- 去除"相关"、"有哪些"、"是什么"、"指标"等无关词
- 如果查询本身就是关键词，直接返回
- 最多返回3个关键词""",
    },
    {
        "module_code": PromptModuleCode.QUERY_DATA,
        "module_name": "智能问数-数据查询生成",
        "description": "用于智能问数系统中的数据智能查询功能，将自然语言转换为SQL查询",
        "temperature": 0.2,
        "placeholders": [
            {"name": "user_query", "description": "用户查询内容"},
            {"name": "schema_context", "description": "数据库表结构信息"},
            {"name": "metrics_context", "description": "相关指标信息JSON"},
        ],
        "system_prompt": """你是一个SQL专家。你的任务是将用户的自然语言查询转换为正确的SQL语句。

要求：
1. 生成的SQL必须语法正确
2. 使用提供的表结构信息
3. 考虑性能优化
4. 添加必要的注释说明""",
        "user_prompt": """用户查询：{user_query}

数据库表结构：
{schema_context}

相关指标信息：
{metrics_context}

请生成对应的SQL查询语句。要求：
1. SQL语法正确，可直接执行
2. 包含必要的WHERE条件
3. 合理使用JOIN和聚合函数
4. 添加中文注释说明查询逻辑

同时，请建议最适合展示查询结果的图表类型（折线图/柱状图/饼图/表格）。""",
    },
    {
        "module_code": PromptModuleCode.QUERY_SQL,
        "module_name": "智能问数-SQL代码编写",
        "description": "用于智能问数系统中的SQL代码编写功能，帮助用户生成指标计算SQL",
        "temperature": 0.2,
        "placeholders": [
            {"name": "user_request", "description": "用户需求描述"},
            {"name": "metric_definition", "description": "指标定义信息"},
            {"name": "schema_context", "description": "数据库表结构信息"},
        ],
        "system_prompt": """你是一个资深的ETL工程师。你的任务是根据指标定义生成高质量的SQL代码。

代码要求：
1. 遵循SQL最佳实践
2. 代码结构清晰，易于维护
3. 包含完整的注释
4. 考虑性能优化""",
        "user_prompt": """用户需求：{user_request}

指标定义：
{metric_definition}

数据库表结构：
{schema_context}

请生成对应的SQL代码。要求：
1. 代码结构清晰，使用CTE提高可读性
2. 包含详细的中文注释
3. 处理NULL值和边界情况
4. 如果指标定义有歧义，请先提出澄清问题

输出格式：
- 使用代码块包裹SQL
- 在代码前说明实现思路
- 在代码后说明注意事项""",
    },
]


class AIPromptModuleService:
    """AI提示词模块服务"""
    
    @staticmethod
    def ensure_modules_initialized(db: Session, hospital_id: int) -> None:
        """
        确保指定医疗机构的提示词模块已初始化
        如果模块不存在，则创建默认配置
        """
        # 获取已存在的模块代码
        existing_codes = set(
            code[0]
            for code in db.query(AIPromptModule.module_code)
            .filter(AIPromptModule.hospital_id == hospital_id)
            .all()
        )
        
        # 检查是否所有模块都已存在
        default_codes = set(m["module_code"] for m in DEFAULT_MODULES)
        if existing_codes >= default_codes:
            return  # 所有模块都已初始化
        
        # 创建缺失的模块
        created_count = 0
        for module_config in DEFAULT_MODULES:
            if module_config["module_code"] not in existing_codes:
                module = AIPromptModule(
                    hospital_id=hospital_id,
                    module_code=module_config["module_code"],
                    module_name=module_config["module_name"],
                    description=module_config["description"],
                    temperature=module_config["temperature"],
                    placeholders=module_config["placeholders"],
                    system_prompt=module_config["system_prompt"],
                    user_prompt=module_config["user_prompt"],
                )
                db.add(module)
                created_count += 1
                logger.info(
                    f"初始化提示词模块: {module_config['module_code']} for hospital_id={hospital_id}"
                )
        
        if created_count > 0:
            db.commit()
    
    @staticmethod
    def get_module_config(
        db: Session, 
        hospital_id: int, 
        module_code: str
    ) -> Optional[AIPromptModule]:
        """
        获取指定模块的配置
        如果模块不存在，会先初始化
        """
        AIPromptModuleService.ensure_modules_initialized(db, hospital_id)
        
        return db.query(AIPromptModule).filter(
            AIPromptModule.hospital_id == hospital_id,
            AIPromptModule.module_code == module_code
        ).first()
    
    @staticmethod
    def check_module_ready(
        db: Session, 
        hospital_id: int, 
        module_code: str
    ) -> tuple[bool, Optional[str]]:
        """
        检查模块是否已准备就绪（已配置AI接口）
        
        Returns:
            (is_ready, error_message)
        """
        module = AIPromptModuleService.get_module_config(db, hospital_id, module_code)
        
        if not module:
            return False, f"模块 '{module_code}' 不存在"
        
        if not module.ai_interface_id:
            return False, f"模块 '{module.module_name}' 未配置AI接口"
        
        # 检查AI接口是否启用
        from app.models import AIInterface
        ai_interface = db.query(AIInterface).filter(
            AIInterface.id == module.ai_interface_id
        ).first()
        
        if not ai_interface:
            return False, f"模块 '{module.module_name}' 关联的AI接口不存在"
        
        if not ai_interface.is_active:
            return False, f"模块 '{module.module_name}' 关联的AI接口已禁用"
        
        return True, None
