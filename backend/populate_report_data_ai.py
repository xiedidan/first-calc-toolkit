"""
基于AI的业务价值报表数据智能生成脚本

功能：
1. 读取配置文件（医院信息、总工作量、科室信息）
2. 调用AI大模型，智能分配各科室的工作量
3. 调用AI大模型，智能分配各科室内各维度的工作量
4. 生成计算数据并保存到数据库
5. 自动计算序列汇总值和占比
6. 生成汇总表数据

使用方法：
    python populate_report_data_ai.py --config report_data_config.json --period 2025-10
    python populate_report_data_ai.py --config report_data_config.json --period 2025-10 --api-key YOUR_API_KEY
    python populate_report_data_ai.py --config report_data_config.json --period 2025-10 --model gpt-4
"""
import sys
import os
import json
from decimal import Decimal
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import argparse

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.calculation_task import CalculationTask, CalculationResult, CalculationSummary
from app.models.department import Department
from app.models.model_version import ModelVersion
from app.models.model_node import ModelNode


class AIDataGenerator:
    """AI数据生成器"""
    
    def __init__(self, api_key: str = None, model: str = "gpt-3.5-turbo", 
                 base_url: str = None, temperature: float = 0.7,
                 max_tokens: int = 4000, timeout: int = 60,
                 prompts_file: str = "ai_prompts.json"):
        """
        初始化AI数据生成器
        
        Args:
            api_key: OpenAI API密钥
            model: 使用的模型名称
            base_url: API基础URL（用于自定义端点）
            temperature: 温度参数（0-2）
            max_tokens: 最大token数
            timeout: 超时时间（秒）
            prompts_file: 提示词配置文件路径
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model
        self.base_url = base_url
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.timeout = timeout
        
        if not self.api_key:
            raise ValueError("未提供API密钥，请在配置文件中设置或通过环境变量提供")
        
        # 加载提示词模板
        with open(prompts_file, 'r', encoding='utf-8') as f:
            self.prompts = json.load(f)
        
        print(f"✓ AI模型初始化完成")
        print(f"  模型: {self.model}")
        print(f"  端点: {self.base_url or 'https://api.openai.com/v1'}")
        print(f"  温度: {self.temperature}")
        print(f"  最大tokens: {self.max_tokens}")
    
    def call_ai(self, system_prompt: str, user_prompt: str) -> str:
        """
        调用AI模型
        
        Args:
            system_prompt: 系统提示词
            user_prompt: 用户提示词
            
        Returns:
            AI返回的文本
        """
        try:
            import openai
            
            # 打印调试信息
            print(f"  提示词长度: 系统={len(system_prompt)}, 用户={len(user_prompt)}")
            
            client = openai.OpenAI(
                api_key=self.api_key,
                base_url=self.base_url,
                timeout=self.timeout
            )
            
            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            
            # 兼容不同的API返回格式
            result = None
            if isinstance(response, str):
                # 如果返回的是字符串，直接使用
                result = response.strip()
            elif hasattr(response, 'choices') and len(response.choices) > 0:
                # 标准OpenAI格式
                result = response.choices[0].message.content.strip()
            else:
                # 尝试其他可能的格式
                result = str(response).strip()
            
            if not result:
                raise ValueError("AI返回了空响应")
            
            print(f"  响应长度: {len(result)}")
            return result
        
        except Exception as e:
            print(f"❌ AI调用失败: {str(e)}")
            print(f"  API端点: {self.base_url}")
            print(f"  模型: {self.model}")
            import traceback
            traceback.print_exc()
            raise
    
    def parse_json_response(self, response: str) -> dict:
        """
        解析AI返回的JSON响应
        
        Args:
            response: AI返回的文本
            
        Returns:
            解析后的字典
        """
        if not response:
            raise ValueError("AI返回了空响应，无法解析")
        
        # 尝试提取JSON代码块
        if "```json" in response:
            start = response.find("```json") + 7
            end = response.find("```", start)
            if end == -1:
                # 没有找到结束标记，可能被截断了
                json_str = response[start:].strip()
            else:
                json_str = response[start:end].strip()
        elif "```" in response:
            start = response.find("```") + 3
            end = response.find("```", start)
            if end == -1:
                json_str = response[start:].strip()
            else:
                json_str = response[start:end].strip()
        else:
            json_str = response.strip()
        
        try:
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            error_msg = str(e)
            print(f"❌ JSON解析失败: {error_msg}")
            print(f"响应长度: {len(response)}")
            print(f"JSON长度: {len(json_str)}")
            print(f"原始响应（前500字符）: {response[:500]}")
            print(f"原始响应（后500字符）: {response[-500:]}")
            
            # 检查是否是因为截断导致的
            if "char" in error_msg:
                print("\n⚠️  JSON可能被截断了，请增加max_tokens配置")
                print(f"当前max_tokens: {self.max_tokens}")
                print(f"建议max_tokens: {self.max_tokens * 2}")
            
            raise
    
    def allocate_departments(self, config: dict) -> Dict[str, dict]:
        """
        为各科室分配工作量比例
        
        Args:
            config: 配置文件内容
            
        Returns:
            科室分配结果 {his_code: allocation_data}
        """
        print("\n" + "="*70)
        print("步骤1: AI分配各科室工作量比例")
        print("="*70)
        
        hospital_info = config['hospital_info']
        total_workload = config['total_workload']
        departments = config['departments']
        
        # 构建提示词
        hospital_characteristics = "\n".join([f"- {c}" for c in hospital_info['characteristics']])
        
        total_workload_info = ""
        for key, data in total_workload.items():
            total_workload_info += f"- {data['description']}: {data['value']}\n"
            if data.get('note'):
                total_workload_info += f"  备注: {data['note']}\n"
        
        departments_info = ""
        for dept in departments:
            departments_info += f"\n科室代码: {dept['his_code']}\n"
            departments_info += f"科室名称: {dept['his_name']}\n"
            departments_info += f"科室类别: {dept['category']}\n"
            departments_info += f"业务特点: {dept['business_characteristics']}\n"
        
        prompt_template = self.prompts['department_allocation_prompt']
        user_prompt = prompt_template['user_template'].format(
            hospital_name=hospital_info['name'],
            hospital_type=hospital_info['type'],
            hospital_specialty=hospital_info['specialty'],
            hospital_description=hospital_info['description'],
            hospital_characteristics=hospital_characteristics,
            total_workload_info=total_workload_info,
            departments_info=departments_info
        )
        
        print("正在调用AI模型进行科室工作量分配...")
        response = self.call_ai(prompt_template['system'], user_prompt)
        
        print("正在解析AI响应...")
        result = self.parse_json_response(response)
        
        # 转换为字典格式
        allocations = {}
        for alloc in result['allocations']:
            allocations[alloc['his_code']] = alloc
            print(f"  {alloc['his_code']} - {alloc['his_name']}")
            print(f"    工作量: {alloc['workload_based_ratio']:.1f}%")
            print(f"    会诊: {alloc['consultation_ratio']:.1f}%")
            print(f"    MDT: {alloc['mdt_ratio']:.1f}%")
            print(f"    病案: {alloc['case_ratio']:.1f}%")
            print(f"    床日: {alloc['nursing_bed_days_ratio']:.1f}%")
            print(f"    手术: {alloc['surgery_ratio']:.1f}%")
            print(f"    留观: {alloc['observation_ratio']:.1f}%")
            print(f"    理由: {alloc['reasoning']}")
        
        print(f"\n✓ 完成 {len(allocations)} 个科室的工作量分配")
        return allocations

    
    def allocate_dimensions(self, dept_config: dict, dept_allocation: dict, 
                           dimensions: List[ModelNode], total_workload: dict) -> Dict[int, dict]:
        """
        为科室的各维度分配工作量
        
        Args:
            dept_config: 科室配置信息
            dept_allocation: 科室的工作量分配
            dimensions: 维度节点列表
            total_workload: 总工作量配置
            
        Returns:
            维度分配结果 {node_id: allocation_data}
        """
        print(f"\n为科室 {dept_config['his_code']} - {dept_config['his_name']} 分配维度工作量...")
        
        # 计算该科室的总工作量
        dept_total = {}
        dept_total['workload_based'] = int(
            total_workload['workload_based_total']['value'] * 
            dept_allocation['workload_based_ratio'] / 100
        )
        dept_total['consultation'] = int(
            total_workload['consultation_total']['value'] * 
            dept_allocation['consultation_ratio'] / 100
        )
        dept_total['mdt'] = int(
            total_workload['mdt_total']['value'] * 
            dept_allocation['mdt_ratio'] / 100
        )
        dept_total['case'] = int(
            total_workload['case_total']['value'] * 
            dept_allocation['case_ratio'] / 100
        )
        dept_total['nursing_bed_days'] = int(
            total_workload['nursing_bed_days_total']['value'] * 
            dept_allocation['nursing_bed_days_ratio'] / 100
        )
        dept_total['surgery'] = int(
            total_workload['surgery_total']['value'] * 
            dept_allocation['surgery_ratio'] / 100
        )
        dept_total['observation'] = int(
            total_workload['observation_total']['value'] * 
            dept_allocation['observation_ratio'] / 100
        )
        
        dept_total_workload = f"""
工作量总额: {dept_total['workload_based']}
会诊数: {dept_total['consultation']}
MDT数: {dept_total['mdt']}
病案数: {dept_total['case']}
床日数: {dept_total['nursing_bed_days']}
手术台次: {dept_total['surgery']}
留观数: {dept_total['observation']}
"""
        
        # 构建维度树形结构信息
        dimensions_info = self._build_dimensions_tree_info(dimensions)
        
        # 构建约束信息
        dept_constraints = "\n".join([f"- {c}" for c in dept_config['constraints']])
        
        prompt_template = self.prompts['dimension_allocation_prompt']
        user_prompt = prompt_template['user_template'].format(
            dept_code=dept_config['his_code'],
            dept_name=dept_config['his_name'],
            dept_category=dept_config['category'],
            dept_characteristics=dept_config['business_characteristics'],
            dept_constraints=dept_constraints,
            dept_total_workload=dept_total_workload,
            dimensions_info=dimensions_info
        )
        
        print("  正在调用AI模型进行维度工作量分配...")
        response = self.call_ai(prompt_template['system'], user_prompt)
        
        print("  正在解析AI响应...")
        result = self.parse_json_response(response)
        
        # 转换为字典格式（按node_id索引）
        allocations = {}
        code_to_node = {d.code: d for d in dimensions}
        
        print(f"  数据库中的维度代码（前10个）: {list(code_to_node.keys())[:10]}")
        print(f"  AI返回的分配数量: {len(result.get('allocations', []))}")
        
        matched_count = 0
        unmatched_codes = []
        
        # 使用工作量总额作为基数（这是最主要的工作量指标）
        base_workload = dept_total['workload_based']
        
        # 第一遍：收集所有匹配的分配和原始比例
        temp_allocations = []
        total_ratio = 0.0
        
        for alloc in result.get('allocations', []):
            dimension_code = alloc.get('dimension_code')
            node = code_to_node.get(dimension_code)
            
            if node:
                matched_count += 1
                ratio = alloc.get('ratio', 0.0)
                total_ratio += ratio
                temp_allocations.append({
                    'node': node,
                    'original_ratio': ratio,
                    'dimension_name': alloc['dimension_name'],
                    'reasoning': alloc['reasoning']
                })
            else:
                unmatched_codes.append(dimension_code)
        
        # 归一化比例，确保总和为100%
        if total_ratio > 0:
            normalization_factor = 100.0 / total_ratio
            print(f"  原始总比例: {total_ratio:.1f}%, 归一化系数: {normalization_factor:.4f}")
        else:
            normalization_factor = 1.0
            print(f"  ⚠️  警告: 总比例为0，无法归一化")
        
        # 第二遍：应用归一化并计算工作量
        actual_total_workload = 0
        for temp_alloc in temp_allocations:
            node = temp_alloc['node']
            normalized_ratio = temp_alloc['original_ratio'] * normalization_factor
            workload = int(base_workload * normalized_ratio / 100)
            actual_total_workload += workload
            
            allocations[node.id] = {
                'node_id': node.id,
                'node_code': node.code,
                'node_name': temp_alloc['dimension_name'],
                'original_ratio': temp_alloc['original_ratio'],
                'normalized_ratio': normalized_ratio,
                'workload': workload,
                'reasoning': temp_alloc['reasoning']
            }
            
            if temp_alloc['original_ratio'] > 0:  # 只显示非零的
                print(f"    ✓ {temp_alloc['dimension_name']}: 原始比例={temp_alloc['original_ratio']:.1f}%, 归一化比例={normalized_ratio:.1f}%, 工作量={workload}")
        
        if unmatched_codes:
            print(f"\n  ⚠️  有 {len(unmatched_codes)} 个维度代码未匹配:")
            print(f"  未匹配的代码: {unmatched_codes[:10]}")
        
        print(f"  ✓ 完成 {matched_count}/{len(result.get('allocations', []))} 个维度的工作量分配")
        print(f"  科室工作量总额: {base_workload}, 实际分配工作量: {actual_total_workload}")
        
        return allocations
    
    def _build_dimensions_tree_info(self, dimensions: List[ModelNode]) -> str:
        """构建维度树形结构信息"""
        info = "**重要：请严格使用以下维度代码，不要修改或编造代码**\n\n"
        
        # 先列出所有叶子维度（没有子节点的维度）
        all_node_ids = {d.id for d in dimensions}
        parent_ids = {d.parent_id for d in dimensions if d.parent_id is not None}
        leaf_nodes = [d for d in dimensions if d.id not in parent_ids]
        
        info += "## 叶子维度（只为这些维度分配工作量）：\n"
        for node in sorted(leaf_nodes, key=lambda x: x.sort_order):
            info += f"- **代码: {node.code}** | 名称: {node.name} | 权重: {node.weight or 0}\n"
        
        info += "\n## 完整维度树形结构：\n"
        
        # 按层级组织维度
        root_dimensions = [d for d in dimensions if d.parent_id is None]
        
        def add_node_info(node: ModelNode, level: int = 0):
            nonlocal info
            indent = "  " * level
            is_leaf = node.id not in parent_ids
            leaf_mark = " [叶子维度]" if is_leaf else " [父维度-自动汇总]"
            info += f"{indent}- **代码: {node.code}** | 名称: {node.name} | 权重: {node.weight or 0}{leaf_mark}\n"
            
            # 添加子节点
            children = [d for d in dimensions if d.parent_id == node.id]
            for child in sorted(children, key=lambda x: x.sort_order):
                add_node_info(child, level + 1)
        
        for root in sorted(root_dimensions, key=lambda x: x.sort_order):
            add_node_info(root)
        
        return info


def load_config(config_file: str) -> dict:
    """加载配置文件"""
    print(f"加载配置文件: {config_file}")
    with open(config_file, 'r', encoding='utf-8') as f:
        config = json.load(f)
    print(f"✓ 配置文件加载成功")
    return config


def resolve_env_variable(value: str) -> str:
    """
    解析环境变量
    支持格式：${VAR_NAME} 或 $VAR_NAME
    
    Args:
        value: 可能包含环境变量的字符串
        
    Returns:
        解析后的字符串
    """
    if not isinstance(value, str):
        return value
    
    import re
    
    # 匹配 ${VAR_NAME} 格式
    pattern1 = r'\$\{([^}]+)\}'
    matches1 = re.findall(pattern1, value)
    for var_name in matches1:
        env_value = os.getenv(var_name, '')
        value = value.replace(f'${{{var_name}}}', env_value)
    
    # 匹配 $VAR_NAME 格式
    pattern2 = r'\$([A-Z_][A-Z0-9_]*)'
    matches2 = re.findall(pattern2, value)
    for var_name in matches2:
        env_value = os.getenv(var_name, '')
        value = value.replace(f'${var_name}', env_value)
    
    return value


def load_ai_config_from_file(config: dict) -> dict:
    """
    从配置文件加载AI配置
    
    Args:
        config: 配置文件内容
        
    Returns:
        AI配置字典
    """
    if 'ai_config' not in config:
        return {}
    
    ai_config = config['ai_config'].copy()
    
    # 解析环境变量
    if 'api_key' in ai_config:
        ai_config['api_key'] = resolve_env_variable(ai_config['api_key'])
    
    if 'base_url' in ai_config:
        ai_config['base_url'] = resolve_env_variable(ai_config['base_url'])
    
    # 移除note字段（仅用于说明）
    ai_config.pop('note', None)
    
    return ai_config


def clean_existing_data(db: Session, period: str):
    """清理指定周期的现有数据"""
    print(f"\n清理周期 {period} 的现有数据...")
    
    tasks = db.query(CalculationTask).filter(
        CalculationTask.period == period
    ).all()
    
    if not tasks:
        print("  未找到现有数据")
        return
    
    task_ids = [task.task_id for task in tasks]
    
    result_count = db.query(CalculationResult).filter(
        CalculationResult.task_id.in_(task_ids)
    ).delete(synchronize_session=False)
    
    summary_count = db.query(CalculationSummary).filter(
        CalculationSummary.task_id.in_(task_ids)
    ).delete(synchronize_session=False)
    
    task_count = db.query(CalculationTask).filter(
        CalculationTask.period == period
    ).delete(synchronize_session=False)
    
    db.commit()
    
    print(f"  删除 {task_count} 个任务")
    print(f"  删除 {result_count} 条计算结果")
    print(f"  删除 {summary_count} 条汇总数据")


def calculate_all_dimension_ratios(db: Session, task_id: str, dept_id: int):
    """计算所有维度的占比"""
    all_dimensions = db.query(CalculationResult).filter(
        CalculationResult.task_id == task_id,
        CalculationResult.department_id == dept_id,
        CalculationResult.node_type == "dimension"
    ).all()
    
    from collections import defaultdict
    parent_groups = defaultdict(list)
    for dim in all_dimensions:
        parent_groups[dim.parent_id].append(dim)
    
    for parent_id, siblings in parent_groups.items():
        total_value = sum((d.value or Decimal("0")) for d in siblings)
        
        if total_value > 0:
            for dim in siblings:
                dim_value = dim.value or Decimal("0")
                dim.ratio = (dim_value / total_value * 100).quantize(Decimal("0.01"))
        else:
            for dim in siblings:
                dim.ratio = Decimal("0")
    
    db.commit()



def populate_report_data_with_ai(
    db: Session,
    config: dict,
    period: str,
    ai_generator: AIDataGenerator,
    model_version_id: int = None,
    clean_first: bool = True
):
    """
    使用AI智能生成报表数据
    
    Args:
        db: 数据库会话
        config: 配置文件内容
        period: 计算周期 (YYYY-MM)
        ai_generator: AI数据生成器
        model_version_id: 模型版本ID
        clean_first: 是否先清理现有数据
    """
    print("\n" + "="*70)
    print("基于AI的业务价值报表数据智能生成")
    print("="*70)
    print(f"计算周期: {period}")
    print(f"医院名称: {config['hospital_info']['name']}")
    print(f"医院类型: {config['hospital_info']['type']}")
    print("="*70)
    
    # 1. 清理现有数据
    if clean_first:
        clean_existing_data(db, period)
    
    # 2. 获取模型版本
    if model_version_id:
        model_version = db.query(ModelVersion).filter(
            ModelVersion.id == model_version_id
        ).first()
    else:
        model_version = db.query(ModelVersion).filter(
            ModelVersion.is_active == True
        ).first()
    
    if not model_version:
        print("❌ 错误: 未找到模型版本")
        return False
    
    print(f"\n使用模型版本: {model_version.name} (ID: {model_version.id})")
    
    # 3. 获取配置中的科室
    config_depts = {d['his_code']: d for d in config['departments']}
    
    # 4. 获取数据库中的科室
    db_departments = db.query(Department).filter(
        Department.is_active == True,
        Department.his_code.in_(list(config_depts.keys()))
    ).order_by(Department.sort_order).all()
    
    if not db_departments:
        print("❌ 错误: 未找到配置中的科室")
        return False
    
    print(f"找到 {len(db_departments)} 个配置的科室")
    
    # 5. 获取模型结构
    all_nodes = db.query(ModelNode).filter(
        ModelNode.version_id == model_version.id
    ).order_by(ModelNode.sort_order).all()
    
    if not all_nodes:
        print("❌ 错误: 模型版本没有节点")
        return False
    
    sequence_nodes = [n for n in all_nodes if n.node_type == "sequence"]
    dimension_nodes = [n for n in all_nodes if n.node_type == "dimension"]
    
    print(f"找到 {len(sequence_nodes)} 个序列节点")
    print(f"找到 {len(dimension_nodes)} 个维度节点")
    
    # 6. AI分配各科室工作量
    dept_allocations = ai_generator.allocate_departments(config)
    
    # 7. 创建计算任务
    task_id = f"report-ai-{period}-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    task = CalculationTask(
        task_id=task_id,
        model_version_id=model_version.id,
        workflow_id=None,
        period=period,
        status="completed",
        progress=Decimal("100.00"),
        description=f"AI智能数据生成 - {period}",
        created_at=datetime.now(),
        started_at=datetime.now(),
        completed_at=datetime.now()
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    
    print(f"\n创建计算任务: {task_id}")
    
    # 8. 为每个科室生成数据
    print("\n" + "="*70)
    print("步骤2: 为各科室生成维度数据")
    print("="*70)
    
    for idx, dept in enumerate(db_departments, 1):
        print(f"\n[{idx}/{len(db_departments)}] {dept.his_code} - {dept.his_name}")
        
        dept_config = config_depts[dept.his_code]
        dept_allocation = dept_allocations[dept.his_code]
        
        # 8.1 AI分配该科室的维度工作量
        dim_allocations = ai_generator.allocate_dimensions(
            dept_config,
            dept_allocation,
            dimension_nodes,
            config['total_workload']
        )
        
        # 8.2 为每个维度创建结果记录
        for dim_node in dimension_nodes:
            allocation = dim_allocations.get(dim_node.id)
            
            if allocation:
                workload = Decimal(str(allocation['workload']))
            else:
                workload = Decimal("0")
            
            weight = dim_node.weight if dim_node.weight is not None else Decimal("0")
            value = workload * weight
            
            result = CalculationResult(
                task_id=task_id,
                department_id=dept.id,
                node_id=dim_node.id,
                node_name=dim_node.name,
                node_code=dim_node.code,
                node_type="dimension",
                parent_id=dim_node.parent_id,
                workload=workload,
                weight=weight,
                value=value,
                ratio=Decimal("0")
            )
            db.add(result)
        
        db.commit()
        
        # 8.3 计算维度占比
        calculate_all_dimension_ratios(db, task_id, dept.id)
        
        # 8.4 计算序列汇总值
        all_dimensions = db.query(CalculationResult).filter(
            CalculationResult.task_id == task_id,
            CalculationResult.department_id == dept.id,
            CalculationResult.node_type == "dimension"
        ).all()
        
        result_map = {d.node_id: d for d in all_dimensions}
        
        def calculate_sum_from_children(node_id: int) -> Decimal:
            result = result_map.get(node_id)
            if not result:
                return Decimal("0")
            
            children = [d for d in all_dimensions if d.parent_id == node_id]
            
            if not children:
                return result.value or Decimal("0")
            
            total_value = Decimal("0")
            for child in children:
                child_value = calculate_sum_from_children(child.node_id)
                total_value += child_value
            
            return total_value
        
        for seq_node in sequence_nodes:
            first_level_dimensions = [
                d for d in all_dimensions 
                if d.parent_id == seq_node.id
            ]
            
            sequence_value = Decimal("0")
            for dim in first_level_dimensions:
                dim_value = calculate_sum_from_children(dim.node_id)
                sequence_value += dim_value
            
            seq_result = CalculationResult(
                task_id=task_id,
                department_id=dept.id,
                node_id=seq_node.id,
                node_name=seq_node.name,
                node_code=seq_node.code,
                node_type="sequence",
                parent_id=None,
                workload=None,
                weight=None,
                value=sequence_value,
                ratio=None
            )
            db.add(seq_result)
        
        db.commit()
        print(f"  ✓ 科室 {dept.his_name} 数据生成完成")
    
    # 9. 生成汇总数据
    print("\n" + "="*70)
    print("步骤3: 生成汇总数据")
    print("="*70)
    
    for idx, dept in enumerate(db_departments, 1):
        print(f"[{idx}/{len(db_departments)}] {dept.his_code} - {dept.his_name}")
        
        sequence_results = db.query(CalculationResult).filter(
            CalculationResult.task_id == task_id,
            CalculationResult.department_id == dept.id,
            CalculationResult.node_type == "sequence"
        ).all()
        
        doctor_value = Decimal("0")
        nurse_value = Decimal("0")
        tech_value = Decimal("0")
        
        for result in sequence_results:
            value = result.value or Decimal("0")
            node_name_lower = result.node_name.lower()
            
            if "医生" in result.node_name or "医疗" in result.node_name or "医师" in result.node_name or \
               "doctor" in node_name_lower or "physician" in node_name_lower:
                doctor_value += value
            elif "护理" in result.node_name or "护士" in result.node_name or \
                 "nurse" in node_name_lower or "nursing" in node_name_lower:
                nurse_value += value
            elif "医技" in result.node_name or "技师" in result.node_name or \
                 "tech" in node_name_lower or "technician" in node_name_lower:
                tech_value += value
        
        total_value = doctor_value + nurse_value + tech_value
        
        if total_value > 0:
            doctor_ratio = (doctor_value / total_value * 100).quantize(Decimal("0.01"))
            nurse_ratio = (nurse_value / total_value * 100).quantize(Decimal("0.01"))
            tech_ratio = (tech_value / total_value * 100).quantize(Decimal("0.01"))
        else:
            doctor_ratio = Decimal("0")
            nurse_ratio = Decimal("0")
            tech_ratio = Decimal("0")
        
        summary = CalculationSummary(
            task_id=task_id,
            department_id=dept.id,
            doctor_value=doctor_value,
            doctor_ratio=doctor_ratio,
            nurse_value=nurse_value,
            nurse_ratio=nurse_ratio,
            tech_value=tech_value,
            tech_ratio=tech_ratio,
            total_value=total_value,
            created_at=datetime.now()
        )
        db.add(summary)
        
        print(f"  医生={doctor_value}, 护理={nurse_value}, 医技={tech_value}, 总计={total_value}")
    
    db.commit()
    
    # 10. 输出统计信息
    result_count = db.query(CalculationResult).filter(
        CalculationResult.task_id == task_id
    ).count()
    
    summary_count = db.query(CalculationSummary).filter(
        CalculationSummary.task_id == task_id
    ).count()
    
    print("\n" + "="*70)
    print("✅ AI智能数据生成完成!")
    print("="*70)
    print(f"任务ID: {task_id}")
    print(f"计算周期: {period}")
    print(f"模型版本: {model_version.name}")
    print(f"科室数量: {len(db_departments)}")
    print(f"计算结果总数: {result_count}")
    print(f"汇总记录数: {summary_count}")
    print("="*70)
    
    return True


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="基于AI的业务价值报表数据智能生成脚本",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 使用配置文件生成数据（AI配置在配置文件中）
  python populate_report_data_ai.py --config report_data_config.json --period 2025-10
  
  # 命令行参数会覆盖配置文件中的AI配置
  python populate_report_data_ai.py --config report_data_config.json --period 2025-10 --api-key YOUR_KEY
  
  # 使用DeepSeek API（在配置文件中设置）
  python populate_report_data_ai.py --config report_data_config.json --period 2025-10
  
  # 不清理现有数据
  python populate_report_data_ai.py --config report_data_config.json --period 2025-10 --no-clean
        """
    )
    
    parser.add_argument(
        "--config",
        required=True,
        help="配置文件路径（JSON格式，包含AI配置）"
    )
    parser.add_argument(
        "--period",
        default=datetime.now().strftime("%Y-%m"),
        help="计算周期 (YYYY-MM)，默认为当前年月"
    )
    parser.add_argument(
        "--api-key",
        help="API密钥（覆盖配置文件中的设置）"
    )
    parser.add_argument(
        "--model",
        help="AI模型名称（覆盖配置文件中的设置）"
    )
    parser.add_argument(
        "--base-url",
        help="API基础URL（覆盖配置文件中的设置）"
    )
    parser.add_argument(
        "--temperature",
        type=float,
        help="温度参数0-2（覆盖配置文件中的设置）"
    )
    parser.add_argument(
        "--max-tokens",
        type=int,
        help="最大token数（覆盖配置文件中的设置）"
    )
    parser.add_argument(
        "--prompts-file",
        default="ai_prompts.json",
        help="提示词配置文件路径（默认: ai_prompts.json）"
    )
    parser.add_argument(
        "--model-version-id",
        type=int,
        help="模型版本ID（默认使用激活版本）"
    )
    parser.add_argument(
        "--no-clean",
        action="store_true",
        help="不清理现有数据（追加模式）"
    )
    
    args = parser.parse_args()
    
    try:
        # 加载配置
        config = load_config(args.config)
        
        # 从配置文件加载AI配置
        ai_config = load_ai_config_from_file(config)
        
        # 命令行参数覆盖配置文件
        if args.api_key:
            ai_config['api_key'] = args.api_key
        if args.model:
            ai_config['model'] = args.model
        if args.base_url:
            ai_config['base_url'] = args.base_url
        if args.temperature is not None:
            ai_config['temperature'] = args.temperature
        if args.max_tokens:
            ai_config['max_tokens'] = args.max_tokens
        
        # 初始化AI生成器
        ai_generator = AIDataGenerator(
            prompts_file=args.prompts_file,
            **ai_config
        )
        
        # 生成数据
        db = SessionLocal()
        try:
            success = populate_report_data_with_ai(
                db=db,
                config=config,
                period=args.period,
                ai_generator=ai_generator,
                model_version_id=args.model_version_id,
                clean_first=not args.no_clean
            )
            
            if success:
                print("\n💡 下一步:")
                print("1. 启动后端服务查看数据")
                print("2. 访问前端报表页面验证")
                print("3. 检查汇总表和明细表数据")
            else:
                print("\n❌ 数据生成失败!")
                sys.exit(1)
        
        finally:
            db.close()
    
    except Exception as e:
        print(f"\n❌ 错误: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
