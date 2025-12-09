"""
AI报告生成服务
"""
from typing import Optional, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.ai_config import AIConfig
from app.models.ai_prompt_config import AIPromptConfig, AIPromptCategory
from app.models.analysis_report import AnalysisReport
from app.models.department import Department
from app.models.hospital import Hospital
from app.utils.encryption import decrypt_api_key


# 默认提示词配置
DEFAULT_PROMPTS = {
    AIPromptCategory.CLASSIFICATION: {
        "system_prompt": """你是一个医院收费项目分类专家。请根据提供的医技项目列表和可选维度列表，为每个项目判断最适合归属的维度，并给出确信度（0-1之间的小数）。必须返回JSON格式：{"results": [{"item_id": <项目ID>, "dimension_id": <维度ID>, "confidence": <确信度>}, ...]}""",
        "user_prompt": """请为以下医技项目分类：

待分类项目列表：
{items}

可选维度列表：
{dimensions}

请返回JSON格式的分类结果。"""
    },
    AIPromptCategory.REPORT_ISSUES: {
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

请基于以上信息，分析该科室当前存在的问题和挑战，输出Markdown格式的分析报告。"""
    },
    AIPromptCategory.REPORT_PLANS: {
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

请基于以上信息，为该科室制定未来发展计划和建议，输出Markdown格式的规划报告。"""
    }
}


# 分类信息
CATEGORY_INFO = {
    AIPromptCategory.CLASSIFICATION: {
        "name": "智能分类分级",
        "description": "用于收费项目的智能分类",
        "placeholders": ["{items}", "{dimensions}"]
    },
    AIPromptCategory.REPORT_ISSUES: {
        "name": "业务价值报表-当前存在问题",
        "description": "用于生成科室运营分析报告中的当前存在问题部分",
        "placeholders": [
            "{hospital_name}", "{hospital_desc}", "{department_name}",
            "{department_alignments}", "{period}", "{dept_main_services}", "{dept_work_substance}"
        ]
    },
    AIPromptCategory.REPORT_PLANS: {
        "name": "业务价值报表-未来发展计划",
        "description": "用于生成科室运营分析报告中的未来发展计划部分",
        "placeholders": [
            "{hospital_name}", "{hospital_desc}", "{department_name}",
            "{department_alignments}", "{period}", "{dept_main_services}", "{dept_work_substance}"
        ]
    }
}


class AIReportService:
    """AI报告生成服务"""
    
    @staticmethod
    def get_category_info() -> list:
        """获取所有分类信息"""
        return [
            {
                "category": cat,
                "name": info["name"],
                "description": info["description"],
                "placeholders": info["placeholders"]
            }
            for cat, info in CATEGORY_INFO.items()
        ]
    
    @staticmethod
    def get_prompt_config(
        db: Session,
        hospital_id: int,
        category: str
    ) -> Dict[str, Any]:
        """
        获取指定分类的提示词配置
        
        Args:
            db: 数据库会话
            hospital_id: 医疗机构ID
            category: 提示词分类
            
        Returns:
            提示词配置字典
        """
        # 查询自定义配置
        config = db.query(AIPromptConfig).filter(
            AIPromptConfig.hospital_id == hospital_id,
            AIPromptConfig.category == category
        ).first()
        
        if config:
            return {
                "id": config.id,
                "hospital_id": config.hospital_id,
                "category": config.category,
                "system_prompt": config.system_prompt,
                "user_prompt": config.user_prompt,
                "created_at": config.created_at,
                "updated_at": config.updated_at,
            }
        
        # 返回默认配置
        default = DEFAULT_PROMPTS.get(category, {})
        return {
            "id": None,
            "hospital_id": hospital_id,
            "category": category,
            "system_prompt": default.get("system_prompt", ""),
            "user_prompt": default.get("user_prompt", ""),
            "created_at": None,
            "updated_at": None,
        }
    
    @staticmethod
    def get_all_prompt_configs(
        db: Session,
        hospital_id: int
    ) -> list:
        """
        获取所有分类的提示词配置
        
        Args:
            db: 数据库会话
            hospital_id: 医疗机构ID
            
        Returns:
            所有分类的提示词配置列表
        """
        result = []
        for category in [AIPromptCategory.CLASSIFICATION, AIPromptCategory.REPORT_ISSUES, AIPromptCategory.REPORT_PLANS]:
            config = AIReportService.get_prompt_config(db, hospital_id, category)
            result.append(config)
        return result
    
    @staticmethod
    def save_prompt_config(
        db: Session,
        hospital_id: int,
        category: str,
        system_prompt: Optional[str],
        user_prompt: str
    ) -> Dict[str, Any]:
        """
        保存提示词配置
        
        Args:
            db: 数据库会话
            hospital_id: 医疗机构ID
            category: 提示词分类
            system_prompt: 系统提示词
            user_prompt: 用户提示词模板
            
        Returns:
            保存后的配置
        """
        # 验证分类
        if category not in CATEGORY_INFO:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"无效的提示词分类: {category}"
            )
        
        # 查询现有配置
        config = db.query(AIPromptConfig).filter(
            AIPromptConfig.hospital_id == hospital_id,
            AIPromptConfig.category == category
        ).first()
        
        if config:
            # 更新
            config.system_prompt = system_prompt
            config.user_prompt = user_prompt
            config.updated_at = datetime.utcnow()
        else:
            # 创建
            config = AIPromptConfig(
                hospital_id=hospital_id,
                category=category,
                system_prompt=system_prompt,
                user_prompt=user_prompt,
            )
            db.add(config)
        
        db.commit()
        db.refresh(config)
        
        return {
            "id": config.id,
            "hospital_id": config.hospital_id,
            "category": config.category,
            "system_prompt": config.system_prompt,
            "user_prompt": config.user_prompt,
            "created_at": config.created_at,
            "updated_at": config.updated_at,
        }
    
    @staticmethod
    def generate_report_content(
        db: Session,
        hospital_id: int,
        report_id: int,
        category: str
    ) -> Dict[str, Any]:
        """
        生成报告内容
        
        Args:
            db: 数据库会话
            hospital_id: 医疗机构ID
            report_id: 报告ID
            category: 生成类型（report_issues 或 report_plans）
            
        Returns:
            生成结果
        """
        from app.utils.ai_interface import call_ai_text_generation
        
        # 验证分类
        if category not in [AIPromptCategory.REPORT_ISSUES, AIPromptCategory.REPORT_PLANS]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="无效的生成类型，仅支持 report_issues 或 report_plans"
            )
        
        # 获取报告信息
        report = db.query(AnalysisReport).filter(
            AnalysisReport.id == report_id,
            AnalysisReport.hospital_id == hospital_id
        ).first()
        
        if not report:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="报告不存在"
            )
        
        # 获取科室信息
        department = db.query(Department).filter(
            Department.id == report.department_id
        ).first()
        
        if not department:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="科室不存在"
            )
        
        # 获取医院信息
        hospital = db.query(Hospital).filter(
            Hospital.id == hospital_id
        ).first()
        
        if not hospital:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="医疗机构不存在"
            )
        
        # 获取AI配置
        ai_config = db.query(AIConfig).filter(
            AIConfig.hospital_id == hospital_id
        ).first()
        
        if not ai_config:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="请先配置AI接口"
            )
        
        # 获取提示词配置
        prompt_config = AIReportService.get_prompt_config(db, hospital_id, category)
        
        # 准备占位符数据
        placeholders = AIReportService._prepare_placeholders(
            db, hospital, department, report
        )
        
        # 替换占位符
        system_prompt = prompt_config["system_prompt"] or ""
        user_prompt = prompt_config["user_prompt"] or ""
        
        for key, value in placeholders.items():
            system_prompt = system_prompt.replace(f"{{{key}}}", value)
            user_prompt = user_prompt.replace(f"{{{key}}}", value)
        
        # 解密API密钥
        api_key = decrypt_api_key(ai_config.api_key_encrypted)
        
        try:
            # 调用AI接口
            start_time = datetime.utcnow()
            content = call_ai_text_generation(
                api_endpoint=ai_config.api_endpoint,
                api_key=api_key,
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                model_name=ai_config.model_name or "deepseek-chat"
            )
            end_time = datetime.utcnow()
            duration = (end_time - start_time).total_seconds()
            
            return {
                "success": True,
                "content": content,
                "error": None,
                "duration": duration,
            }
        except Exception as e:
            return {
                "success": False,
                "content": None,
                "error": str(e),
                "duration": None,
            }
    
    @staticmethod
    def _prepare_placeholders(
        db: Session,
        hospital: Hospital,
        department: Department,
        report: AnalysisReport
    ) -> Dict[str, str]:
        """
        准备占位符数据
        
        Args:
            db: 数据库会话
            hospital: 医院对象
            department: 科室对象
            report: 报告对象
            
        Returns:
            占位符字典
        """
        from decimal import Decimal
        from sqlalchemy import desc, text
        from app.models.calculation_task import CalculationTask, CalculationResult
        from app.models.model_version import ModelVersion
        from app.models.dimension_item_mapping import DimensionItemMapping
        from app.models.charge_item import ChargeItem
        
        # 基本信息
        hospital_name = hospital.name or ""
        hospital_desc = ""  # 医院简介字段暂无，可后续扩展
        department_name = department.accounting_unit_name or department.his_name or ""
        dept_code = department.his_code
        
        # 核算序列
        alignments = department.accounting_sequences or []
        alignment_map = {"doctor": "医生", "nursing": "护理", "tech": "医技"}
        department_alignments = "、".join([alignment_map.get(a, a) for a in alignments]) or "未配置"
        
        # 获取业务数据
        dept_main_services = ""
        dept_work_substance = ""
        
        try:
            # 查找激活版本的最新完成任务
            active_version = db.query(ModelVersion).filter(
                ModelVersion.hospital_id == hospital.id,
                ModelVersion.is_active == True
            ).first()
            
            if active_version:
                task = db.query(CalculationTask).filter(
                    CalculationTask.model_version_id == active_version.id,
                    CalculationTask.period == report.period,
                    CalculationTask.status == "completed"
                ).order_by(desc(CalculationTask.completed_at)).first()
                
                if task:
                    # 获取该科室的所有计算结果（包括序列和维度）
                    all_nodes = db.query(CalculationResult).filter(
                        CalculationResult.task_id == task.task_id,
                        CalculationResult.department_id == department.id
                    ).all()
                    
                    if all_nodes:
                        # 构建 node_id -> result 的映射
                        node_map = {r.node_id: r for r in all_nodes}
                        
                        # 构建完整路径的辅助函数
                        def build_full_path(result):
                            path_parts = []
                            current = result
                            while current:
                                path_parts.insert(0, current.node_name)
                                if current.parent_id and current.parent_id in node_map:
                                    current = node_map[current.parent_id]
                                else:
                                    break
                            return "-".join(path_parts)
                        
                        # 筛选维度节点
                        dimension_results = [r for r in all_nodes if r.node_type == "dimension"]
                        
                        # 找出叶子节点
                        parent_node_ids = set(r.parent_id for r in dimension_results if r.parent_id)
                        leaf_results = [r for r in dimension_results if r.node_id not in parent_node_ids]
                        
                        # 按业务价值降序排序，取 Top 5
                        top_dims = sorted(leaf_results, key=lambda x: x.value or Decimal('0'), reverse=True)[:5]
                        
                        # 计算科室总业务价值（所有叶子维度的业务价值之和）
                        total_dept_value = sum((r.value or Decimal('0')) for r in leaf_results)
                        
                        # 构建主业描述（使用完整维度路径，包含占比）
                        main_services = []
                        for dim in top_dims:
                            full_path = build_full_path(dim)
                            value = dim.value or Decimal('0')
                            workload = dim.workload or Decimal('0')
                            # 计算该维度业务价值在科室总业务价值中的占比
                            ratio = (float(value) / float(total_dept_value) * 100) if total_dept_value > 0 else 0
                            main_services.append(f"- {full_path}：业务价值 {float(value):,.2f}（占比 {ratio:.1f}%），工作量金额 {float(workload):,.2f}")
                        
                        dept_main_services = "\n".join(main_services) if main_services else "暂无数据"
                        
                        # 构建业务内涵描述（Top5维度的Top5项目）
                        work_substance_parts = []
                        for dim in top_dims:
                            if not dim.node_code:
                                continue
                            
                            full_path = build_full_path(dim)
                            
                            # 查询该维度对应的收费项目映射
                            dim_mappings = db.query(DimensionItemMapping).filter(
                                DimensionItemMapping.hospital_id == hospital.id,
                                DimensionItemMapping.dimension_code == dim.node_code
                            ).all()
                            
                            if not dim_mappings:
                                continue
                            
                            dim_item_codes = [m.item_code for m in dim_mappings]
                            
                            # 查询收费项目信息
                            charge_items = db.query(ChargeItem).filter(
                                ChargeItem.hospital_id == hospital.id,
                                ChargeItem.item_code.in_(dim_item_codes)
                            ).all()
                            
                            item_info_map = {ci.item_code: ci for ci in charge_items}
                            
                            # 从 charge_details 查询该维度收入 Top 5 的项目
                            try:
                                sql = text("""
                                    SELECT 
                                        item_code,
                                        item_name,
                                        SUM(amount) as total_amount,
                                        SUM(quantity) as total_quantity
                                    FROM charge_details
                                    WHERE prescribing_dept_code = :dept_code
                                    AND TO_CHAR(charge_time, 'YYYY-MM') = :period
                                    AND item_code = ANY(:item_codes)
                                    GROUP BY item_code, item_name
                                    ORDER BY total_amount DESC
                                    LIMIT 5
                                """)
                                
                                result = db.execute(sql, {
                                    "dept_code": dept_code,
                                    "period": report.period,
                                    "item_codes": dim_item_codes
                                })
                                
                                charge_details_data = result.fetchall()
                                
                                if charge_details_data:
                                    dim_items = []
                                    for row in charge_details_data:
                                        item_code = row[0]
                                        charge_item = item_info_map.get(item_code)
                                        item_name = row[1] or (charge_item.item_name if charge_item else item_code)
                                        amount = Decimal(str(row[2])) if row[2] else Decimal('0')
                                        quantity = Decimal(str(row[3])) if row[3] else Decimal('0')
                                        
                                        dim_items.append(f"    - {item_name}：金额 {float(amount):,.2f}，数量 {float(quantity):,.0f}")
                                    
                                    if dim_items:
                                        work_substance_parts.append(f"### {full_path}\n" + "\n".join(dim_items))
                                        
                            except Exception as e:
                                print(f"查询维度 {dim.node_code} 的 charge_details 失败: {str(e)}")
                                continue
                        
                        dept_work_substance = "\n\n".join(work_substance_parts) if work_substance_parts else "暂无数据"
                        
        except Exception as e:
            print(f"获取业务数据失败: {str(e)}")
            import traceback
            traceback.print_exc()
            dept_main_services = "数据获取失败"
            dept_work_substance = "数据获取失败"
        
        return {
            "hospital_name": hospital_name,
            "hospital_desc": hospital_desc,
            "department_name": department_name,
            "department_alignments": department_alignments,
            "period": report.period or "",
            "dept_main_services": dept_main_services,
            "dept_work_substance": dept_work_substance,
        }
