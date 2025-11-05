"""
验证科室汇总表计算逻辑

检查：
1. 序列价值 = 该序列下所有维度的价值总和
2. 科室总价值 = 医 + 护 + 技三个序列的价值之和
3. 各序列占比 = 序列价值 / 科室总价值
"""
import sys
import os
from decimal import Decimal

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from sqlalchemy import text
from app.database import SessionLocal
from app.models.calculation_task import CalculationResult, CalculationSummary
from app.models.department import Department
from app.models.model_node import ModelNode


def verify_summary_calculation(db: Session, task_id: str):
    """验证汇总表计算逻辑"""
    
    print("="*80)
    print("科室汇总表计算验证")
    print("="*80)
    print(f"任务ID: {task_id}")
    print()
    
    # 获取该任务的所有科室
    summaries = db.query(CalculationSummary).filter(
        CalculationSummary.task_id == task_id
    ).all()
    
    if not summaries:
        print("❌ 未找到汇总数据")
        return False
    
    print(f"找到 {len(summaries)} 个科室的汇总数据")
    print()
    
    all_correct = True
    
    for summary in summaries:
        dept = db.query(Department).filter(Department.id == summary.department_id).first()
        dept_name = f"{dept.his_code} - {dept.his_name}" if dept else f"科室ID: {summary.department_id}"
        
        print("-"*80)
        print(f"科室: {dept_name}")
        print("-"*80)
        
        # 获取该科室的所有序列结果
        sequence_results = db.query(CalculationResult).filter(
            CalculationResult.task_id == task_id,
            CalculationResult.department_id == summary.department_id,
            CalculationResult.node_type == "sequence"
        ).all()
        
        # 获取该科室的所有维度结果
        dimension_results = db.query(CalculationResult).filter(
            CalculationResult.task_id == task_id,
            CalculationResult.department_id == summary.department_id,
            CalculationResult.node_type == "dimension"
        ).all()
        
        print(f"\n1. 序列数据 ({len(sequence_results)} 个):")
        
        # 验证每个序列的价值
        doctor_value_calc = Decimal("0")
        nurse_value_calc = Decimal("0")
        tech_value_calc = Decimal("0")
        
        for seq_result in sequence_results:
            # 找出属于该序列的所有维度
            def belongs_to_sequence(node_id: int, seq_id: int, visited: set = None) -> bool:
                """递归判断节点是否属于某个序列"""
                if visited is None:
                    visited = set()
                
                if node_id in visited:
                    return False
                visited.add(node_id)
                
                # 查找节点
                model_node = db.query(ModelNode).filter(ModelNode.id == node_id).first()
                if model_node:
                    if model_node.parent_id == seq_id:
                        return True
                    if model_node.parent_id:
                        return belongs_to_sequence(model_node.parent_id, seq_id, visited)
                
                return False
            
            # 找出属于该序列的所有维度
            seq_dimensions = [
                d for d in dimension_results
                if belongs_to_sequence(d.node_id, seq_result.node_id)
            ]
            
            # 计算该序列下所有维度的价值总和
            expected_value = sum((d.value or Decimal("0")) for d in seq_dimensions)
            actual_value = seq_result.value or Decimal("0")
            
            is_correct = abs(expected_value - actual_value) < Decimal("0.01")
            status = "✅" if is_correct else "❌"
            
            print(f"  {status} {seq_result.node_name}:")
            print(f"      序列价值: {actual_value}")
            print(f"      维度总和: {expected_value} ({len(seq_dimensions)} 个维度)")
            
            if not is_correct:
                print(f"      ⚠️  差异: {actual_value - expected_value}")
                all_correct = False
                
                # 显示维度明细
                print(f"      维度明细:")
                for dim in seq_dimensions:
                    print(f"        - {dim.node_name}: {dim.value}")
            
            # 累加到对应序列
            node_name_lower = seq_result.node_name.lower()
            if "医生" in seq_result.node_name or "医疗" in seq_result.node_name or "医师" in seq_result.node_name or \
               "doctor" in node_name_lower or "physician" in node_name_lower:
                doctor_value_calc += actual_value
            elif "护理" in seq_result.node_name or "护士" in seq_result.node_name or \
                 "nurse" in node_name_lower or "nursing" in node_name_lower:
                nurse_value_calc += actual_value
            elif "医技" in seq_result.node_name or "技师" in seq_result.node_name or \
                 "tech" in node_name_lower or "technician" in node_name_lower:
                tech_value_calc += actual_value
        
        print(f"\n2. 汇总表数据:")
        
        # 验证汇总表的序列价值
        doctor_correct = abs(summary.doctor_value - doctor_value_calc) < Decimal("0.01")
        nurse_correct = abs(summary.nurse_value - nurse_value_calc) < Decimal("0.01")
        tech_correct = abs(summary.tech_value - tech_value_calc) < Decimal("0.01")
        
        print(f"  {'✅' if doctor_correct else '❌'} 医生价值: {summary.doctor_value} (计算值: {doctor_value_calc})")
        print(f"  {'✅' if nurse_correct else '❌'} 护理价值: {summary.nurse_value} (计算值: {nurse_value_calc})")
        print(f"  {'✅' if tech_correct else '❌'} 医技价值: {summary.tech_value} (计算值: {tech_value_calc})")
        
        if not (doctor_correct and nurse_correct and tech_correct):
            all_correct = False
        
        # 验证总价值
        total_calc = doctor_value_calc + nurse_value_calc + tech_value_calc
        total_correct = abs(summary.total_value - total_calc) < Decimal("0.01")
        
        print(f"  {'✅' if total_correct else '❌'} 科室总价值: {summary.total_value} (计算值: {total_calc})")
        
        if not total_correct:
            all_correct = False
        
        # 验证占比
        print(f"\n3. 占比验证:")
        
        if summary.total_value > 0:
            doctor_ratio_calc = (summary.doctor_value / summary.total_value * 100).quantize(Decimal("0.01"))
            nurse_ratio_calc = (summary.nurse_value / summary.total_value * 100).quantize(Decimal("0.01"))
            tech_ratio_calc = (summary.tech_value / summary.total_value * 100).quantize(Decimal("0.01"))
            
            doctor_ratio_correct = abs(summary.doctor_ratio - doctor_ratio_calc) < Decimal("0.01")
            nurse_ratio_correct = abs(summary.nurse_ratio - nurse_ratio_calc) < Decimal("0.01")
            tech_ratio_correct = abs(summary.tech_ratio - tech_ratio_calc) < Decimal("0.01")
            
            print(f"  {'✅' if doctor_ratio_correct else '❌'} 医生占比: {summary.doctor_ratio}% (计算值: {doctor_ratio_calc}%)")
            print(f"  {'✅' if nurse_ratio_correct else '❌'} 护理占比: {summary.nurse_ratio}% (计算值: {nurse_ratio_calc}%)")
            print(f"  {'✅' if tech_ratio_correct else '❌'} 医技占比: {summary.tech_ratio}% (计算值: {tech_ratio_calc}%)")
            
            total_ratio = summary.doctor_ratio + summary.nurse_ratio + summary.tech_ratio
            ratio_sum_correct = abs(total_ratio - Decimal("100")) < Decimal("0.1")
            
            print(f"  {'✅' if ratio_sum_correct else '❌'} 占比总和: {total_ratio}% (应为 100%)")
            
            if not (doctor_ratio_correct and nurse_ratio_correct and tech_ratio_correct and ratio_sum_correct):
                all_correct = False
        else:
            print(f"  ⚠️  总价值为0，跳过占比验证")
        
        print()
    
    print("="*80)
    if all_correct:
        print("✅ 所有科室的汇总数据计算正确!")
    else:
        print("❌ 发现计算错误，请检查上述标记为 ❌ 的项目")
    print("="*80)
    
    return all_correct


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="验证科室汇总表计算逻辑")
    parser.add_argument("--task-id", help="任务ID")
    parser.add_argument("--period", help="计算周期 (YYYY-MM)")
    
    args = parser.parse_args()
    
    db = SessionLocal()
    try:
        # 如果没有指定task_id，查找最新的任务
        if not args.task_id:
            if args.period:
                # 查找指定周期的最新任务
                from app.models.calculation_task import CalculationTask
                task = db.query(CalculationTask).filter(
                    CalculationTask.period == args.period
                ).order_by(CalculationTask.created_at.desc()).first()
            else:
                # 查找最新的任务
                from app.models.calculation_task import CalculationTask
                task = db.query(CalculationTask).order_by(
                    CalculationTask.created_at.desc()
                ).first()
            
            if not task:
                print("❌ 未找到任务")
                sys.exit(1)
            
            task_id = task.task_id
            print(f"使用最新任务: {task_id} (周期: {task.period})")
            print()
        else:
            task_id = args.task_id
        
        success = verify_summary_calculation(db, task_id)
        
        if not success:
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
