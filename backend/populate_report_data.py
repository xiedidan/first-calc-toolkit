"""
业务价值报表数据填充脚本

功能：
1. 清理指定周期的现有数据
2. 为所有启用科室的所有维度生成计算数据
3. 自动计算序列汇总值
4. 自动计算占比（基于真实数据）
5. 生成汇总表数据

使用方法：
    python populate_report_data.py --period 2025-10
    python populate_report_data.py --period 2025-10 --random  # 使用随机值
    python populate_report_data.py --period 2025-10 --model-version-id 1  # 指定模型版本
"""
import sys
import os
from decimal import Decimal
from datetime import datetime
import random
from typing import Dict, List

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.calculation_task import CalculationTask, CalculationResult, CalculationSummary
from app.models.department import Department
from app.models.model_version import ModelVersion
from app.models.model_node import ModelNode


def clean_existing_data(db: Session, period: str):
    """清理指定周期的现有数据"""
    print(f"清理周期 {period} 的现有数据...")
    
    # 查找该周期的所有任务
    tasks = db.query(CalculationTask).filter(
        CalculationTask.period == period
    ).all()
    
    if not tasks:
        print("  未找到现有数据")
        return
    
    task_ids = [task.task_id for task in tasks]
    
    # 删除计算结果
    result_count = db.query(CalculationResult).filter(
        CalculationResult.task_id.in_(task_ids)
    ).delete(synchronize_session=False)
    
    # 删除汇总数据
    summary_count = db.query(CalculationSummary).filter(
        CalculationSummary.task_id.in_(task_ids)
    ).delete(synchronize_session=False)
    
    # 删除任务
    task_count = db.query(CalculationTask).filter(
        CalculationTask.period == period
    ).delete(synchronize_session=False)
    
    db.commit()
    
    print(f"  删除 {task_count} 个任务")
    print(f"  删除 {result_count} 条计算结果")
    print(f"  删除 {summary_count} 条汇总数据")


def generate_workload_value(node: ModelNode, use_random: bool) -> tuple:
    """
    根据节点类型生成工作量和价值
    
    Returns:
        (workload, weight, value)
    """
    # 权重始终从模型节点读取
    weight = node.weight if node.weight is not None else Decimal("0")
    
    if use_random:
        # 根据节点名称生成合理的随机工作量
        if "门诊" in node.name or "诊察" in node.name:
            workload = Decimal(str(random.randint(500, 2000)))
        elif "住院" in node.name or "床日" in node.name:
            workload = Decimal(str(random.randint(200, 800)))
        elif "手术" in node.name:
            workload = Decimal(str(random.randint(50, 300)))
        elif "护理" in node.name:
            workload = Decimal(str(random.randint(300, 1500)))
        elif "检查" in node.name or "检验" in node.name or "放射" in node.name:
            workload = Decimal(str(random.randint(200, 1000)))
        else:
            workload = Decimal(str(random.randint(100, 1000)))
        
        # 价值 = 工作量 × 权重
        value = workload * weight
    else:
        # 使用0值
        workload = Decimal("0")
        value = Decimal("0")
    
    return workload, weight, value


def calculate_all_dimension_ratios(db: Session, task_id: str, dept_id: int):
    """计算所有维度的占比
    
    占比 = 该维度的价值 / 同一父节点下所有兄弟节点的价值总和 × 100%
    """
    # 获取该科室的所有维度结果
    all_dimensions = db.query(CalculationResult).filter(
        CalculationResult.task_id == task_id,
        CalculationResult.department_id == dept_id,
        CalculationResult.node_type == "dimension"
    ).all()
    
    # 按父节点分组
    from collections import defaultdict
    parent_groups = defaultdict(list)
    for dim in all_dimensions:
        parent_groups[dim.parent_id].append(dim)
    
    # 为每个分组计算占比
    for parent_id, siblings in parent_groups.items():
        # 计算该父节点下所有子节点的价值总和
        total_value = sum((d.value or Decimal("0")) for d in siblings)
        
        # 更新每个子节点的占比
        if total_value > 0:
            for dim in siblings:
                dim_value = dim.value or Decimal("0")
                dim.ratio = (dim_value / total_value * 100).quantize(Decimal("0.01"))
        else:
            for dim in siblings:
                dim.ratio = Decimal("0")
    
    db.commit()


def populate_report_data(
    db: Session,
    period: str,
    use_random_values: bool = False,
    model_version_id: int = None,
    clean_first: bool = True
):
    """
    填充报表数据
    
    Args:
        db: 数据库会话
        period: 计算周期 (YYYY-MM)
        use_random_values: 是否使用随机值（False则填0）
        model_version_id: 模型版本ID（如果不指定，使用激活版本）
        clean_first: 是否先清理现有数据
    """
    print("="*70)
    print("业务价值报表数据填充")
    print("="*70)
    print(f"计算周期: {period}")
    print(f"使用随机值: {use_random_values}")
    print(f"清理现有数据: {clean_first}")
    print("="*70)
    
    # 1. 清理现有数据
    if clean_first:
        clean_existing_data(db, period)
        print()
    
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
    
    print(f"使用模型版本: {model_version.name} (ID: {model_version.id})")
    
    # 3. 获取所有启用的科室
    departments = db.query(Department).filter(
        Department.is_active == True
    ).order_by(Department.sort_order).all()
    
    if not departments:
        print("❌ 错误: 未找到启用的科室")
        return False
    
    print(f"找到 {len(departments)} 个启用的科室")
    
    # 4. 获取模型结构
    all_nodes = db.query(ModelNode).filter(
        ModelNode.version_id == model_version.id
    ).order_by(ModelNode.sort_order).all()
    
    if not all_nodes:
        print("❌ 错误: 模型版本没有节点")
        return False
    
    # 分类节点
    sequence_nodes = [n for n in all_nodes if n.node_type == "sequence"]
    dimension_nodes = [n for n in all_nodes if n.node_type == "dimension"]
    
    print(f"找到 {len(sequence_nodes)} 个序列节点")
    print(f"找到 {len(dimension_nodes)} 个维度节点")
    print()
    
    # 5. 创建计算任务
    task_id = f"report-{period}-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    task = CalculationTask(
        task_id=task_id,
        model_version_id=model_version.id,
        workflow_id=None,
        period=period,
        status="completed",
        progress=Decimal("100.00"),
        description=f"报表数据填充 - {period}",
        created_at=datetime.now(),
        started_at=datetime.now(),
        completed_at=datetime.now()
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    
    print(f"创建计算任务: {task_id}")
    print()
    
    # 6. 为每个科室生成数据
    print("开始生成计算结果...")
    print("-"*70)
    
    for idx, dept in enumerate(departments, 1):
        print(f"[{idx}/{len(departments)}] {dept.his_code} - {dept.his_name}")
        
        # 6.1 为每个维度生成结果
        for dim_node in dimension_nodes:
            workload, weight, value = generate_workload_value(dim_node, use_random_values)
            
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
                ratio=Decimal("0")  # 稍后计算
            )
            db.add(result)
        
        db.commit()
        
        # 6.2 计算所有维度的占比（一次性计算所有层级）
        calculate_all_dimension_ratios(db, task_id, dept.id)
        
        # 6.3 计算序列汇总值（基于维度值求和）
        for seq_node in sequence_nodes:
            # 查询该序列下所有末级维度的价值总和
            # 使用递归查询找出该序列下的所有维度（包括多层嵌套）
            
            # 方法1：查询所有维度，然后筛选出属于该序列的
            all_dimensions = db.query(CalculationResult).filter(
                CalculationResult.task_id == task_id,
                CalculationResult.department_id == dept.id,
                CalculationResult.node_type == "dimension"
            ).all()
            
            # 构建父子关系映射
            dimension_map = {d.node_id: d for d in all_dimensions}
            
            # 找出属于该序列的所有维度
            def belongs_to_sequence(dim_result, seq_id):
                """判断维度是否属于某个序列"""
                current = dim_result
                while current:
                    if current.parent_id == seq_id:
                        return True
                    # 查找父节点
                    current = dimension_map.get(current.parent_id)
                return False
            
            # 只统计末级维度（叶子节点）的价值
            sequence_dimensions = [
                d for d in all_dimensions 
                if belongs_to_sequence(d, seq_node.id)
            ]
            
            # 找出末级维度（没有子节点的维度）
            # 收集所有作为父节点的维度ID
            parent_node_ids = {d.parent_id for d in all_dimensions if d.parent_id in dimension_map}
            leaf_dimensions = [
                d for d in sequence_dimensions
                if d.node_id not in parent_node_ids
            ]
            
            # 汇总末级维度的价值
            sequence_value = sum((d.value or Decimal("0")) for d in leaf_dimensions)
            
            # 创建序列结果记录
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
                ratio=None  # 序列不需要占比
            )
            db.add(seq_result)
        
        db.commit()
    
    print("-"*70)
    print("计算结果生成完成")
    print()
    
    # 7. 生成汇总数据
    print("开始生成汇总数据...")
    print("-"*70)
    
    for idx, dept in enumerate(departments, 1):
        print(f"[{idx}/{len(departments)}] {dept.his_code} - {dept.his_name}")
        
        # 查询该科室的所有序列结果
        sequence_results = db.query(CalculationResult).filter(
            CalculationResult.task_id == task_id,
            CalculationResult.department_id == dept.id,
            CalculationResult.node_type == "sequence"
        ).all()
        
        # 初始化序列价值
        doctor_value = Decimal("0")
        nurse_value = Decimal("0")
        tech_value = Decimal("0")
        
        # 根据序列名称分类汇总
        for result in sequence_results:
            value = result.value or Decimal("0")
            
            # 根据节点名称判断序列类型（不区分大小写）
            node_name_lower = result.node_name.lower()
            
            if "医生" in result.node_name or "医疗" in result.node_name or "医师" in result.node_name or \
               "doctor" in node_name_lower or "physician" in node_name_lower:
                doctor_value += value
                print(f"    医生序列: {result.node_name} = {value}")
            elif "护理" in result.node_name or "护士" in result.node_name or \
                 "nurse" in node_name_lower or "nursing" in node_name_lower:
                nurse_value += value
                print(f"    护理序列: {result.node_name} = {value}")
            elif "医技" in result.node_name or "技师" in result.node_name or \
                 "tech" in node_name_lower or "technician" in node_name_lower:
                tech_value += value
                print(f"    医技序列: {result.node_name} = {value}")
            else:
                print(f"    ⚠️  未识别的序列: {result.node_name} = {value}")
        
        # 计算总价值
        total_value = doctor_value + nurse_value + tech_value
        
        print(f"    汇总: 医生={doctor_value}, 护理={nurse_value}, 医技={tech_value}, 总计={total_value}")
        
        # 计算占比
        if total_value > 0:
            doctor_ratio = (doctor_value / total_value * 100).quantize(Decimal("0.01"))
            nurse_ratio = (nurse_value / total_value * 100).quantize(Decimal("0.01"))
            tech_ratio = (tech_value / total_value * 100).quantize(Decimal("0.01"))
        else:
            doctor_ratio = Decimal("0")
            nurse_ratio = Decimal("0")
            tech_ratio = Decimal("0")
        
        # 创建汇总记录
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
    
    db.commit()
    
    print("-"*70)
    print("汇总数据生成完成")
    print()
    
    # 8. 输出统计信息
    result_count = db.query(CalculationResult).filter(
        CalculationResult.task_id == task_id
    ).count()
    
    summary_count = db.query(CalculationSummary).filter(
        CalculationSummary.task_id == task_id
    ).count()
    
    dimension_count = db.query(CalculationResult).filter(
        CalculationResult.task_id == task_id,
        CalculationResult.node_type == "dimension"
    ).count()
    
    sequence_count = db.query(CalculationResult).filter(
        CalculationResult.task_id == task_id,
        CalculationResult.node_type == "sequence"
    ).count()
    
    print("="*70)
    print("✅ 数据填充完成!")
    print("="*70)
    print(f"任务ID: {task_id}")
    print(f"计算周期: {period}")
    print(f"模型版本: {model_version.name}")
    print(f"科室数量: {len(departments)}")
    print(f"序列节点数: {len(sequence_nodes)}")
    print(f"维度节点数: {len(dimension_nodes)}")
    print("-"*70)
    print(f"计算结果总数: {result_count}")
    print(f"  - 维度结果: {dimension_count}")
    print(f"  - 序列结果: {sequence_count}")
    print(f"汇总记录数: {summary_count}")
    print(f"平均每科室记录数: {result_count / len(departments):.1f}")
    print("="*70)
    
    return True


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="业务价值报表数据填充脚本",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 填充当前年月数据（使用0值）
  python populate_report_data.py --period 2025-10
  
  # 填充随机值数据
  python populate_report_data.py --period 2025-10 --random
  
  # 指定模型版本
  python populate_report_data.py --period 2025-10 --model-version-id 1
  
  # 不清理现有数据（追加模式）
  python populate_report_data.py --period 2025-10 --no-clean
        """
    )
    
    parser.add_argument(
        "--period",
        default=datetime.now().strftime("%Y-%m"),
        help="计算周期 (YYYY-MM)，默认为当前年月"
    )
    parser.add_argument(
        "--random",
        action="store_true",
        help="使用随机值（默认填0）"
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
    
    db = SessionLocal()
    try:
        success = populate_report_data(
            db=db,
            period=args.period,
            use_random_values=args.random,
            model_version_id=args.model_version_id,
            clean_first=not args.no_clean
        )
        
        if success:
            print("\n💡 下一步:")
            print("1. 启动后端服务查看数据")
            print("2. 访问前端报表页面验证")
            print("3. 检查汇总表和明细表数据")
        else:
            print("\n❌ 数据填充失败!")
            sys.exit(1)
    
    except Exception as e:
        print(f"\n❌ 错误: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    finally:
        db.close()


if __name__ == "__main__":
    main()
