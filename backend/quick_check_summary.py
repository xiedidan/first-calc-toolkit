"""
快速检查汇总表数据状态
"""
import sys
import os
from decimal import Decimal

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal
from app.models.calculation_task import CalculationResult, CalculationSummary, CalculationTask
from app.models.department import Department


def quick_check():
    """快速检查"""
    db = SessionLocal()
    try:
        # 找最新任务
        task = db.query(CalculationTask).order_by(
            CalculationTask.created_at.desc()
        ).first()
        
        if not task:
            print("❌ 未找到任务")
            return
        
        print(f"最新任务: {task.task_id}")
        print(f"周期: {task.period}")
        print(f"状态: {task.status}")
        print()
        
        # 找第一个科室
        summary = db.query(CalculationSummary).filter(
            CalculationSummary.task_id == task.task_id
        ).first()
        
        if not summary:
            print("❌ 未找到汇总数据")
            return
        
        dept = db.query(Department).filter(Department.id == summary.department_id).first()
        print(f"科室: {dept.his_code} - {dept.his_name}")
        print()
        
        # 查看序列数据
        sequences = db.query(CalculationResult).filter(
            CalculationResult.task_id == task.task_id,
            CalculationResult.department_id == summary.department_id,
            CalculationResult.node_type == "sequence"
        ).all()
        
        print(f"序列数据 ({len(sequences)} 个):")
        for seq in sequences:
            print(f"  {seq.node_name}: {seq.value}")
        print()
        
        # 查看维度数据
        dimensions = db.query(CalculationResult).filter(
            CalculationResult.task_id == task.task_id,
            CalculationResult.department_id == summary.department_id,
            CalculationResult.node_type == "dimension"
        ).all()
        
        print(f"维度数据 ({len(dimensions)} 个):")
        
        # 按parent_id分组
        from collections import defaultdict
        by_parent = defaultdict(list)
        for dim in dimensions:
            by_parent[dim.parent_id].append(dim)
        
        for parent_id in sorted(by_parent.keys()):
            dims = by_parent[parent_id]
            parent_name = "根" if parent_id is None else f"父节点{parent_id}"
            
            # 查找父节点名称
            if parent_id:
                parent = next((s for s in sequences if s.node_id == parent_id), None)
                if parent:
                    parent_name = f"序列: {parent.node_name}"
                else:
                    parent_dim = next((d for d in dimensions if d.node_id == parent_id), None)
                    if parent_dim:
                        parent_name = f"维度: {parent_dim.node_name}"
            
            print(f"\n  {parent_name} 的子维度:")
            for dim in dims:
                print(f"    [{dim.node_id}] {dim.node_name}: 工作量={dim.workload}, 权重={dim.weight}, 价值={dim.value}")
        
        print()
        print("汇总表数据:")
        print(f"  医生: {summary.doctor_value} ({summary.doctor_ratio}%)")
        print(f"  护理: {summary.nurse_value} ({summary.nurse_ratio}%)")
        print(f"  医技: {summary.tech_value} ({summary.tech_ratio}%)")
        print(f"  总计: {summary.total_value}")
        
        # 验证
        print()
        print("验证:")
        seq_total = sum((s.value or Decimal("0")) for s in sequences)
        print(f"  序列价值总和: {seq_total}")
        print(f"  汇总表总价值: {summary.total_value}")
        print(f"  匹配: {'✅' if abs(seq_total - summary.total_value) < Decimal('0.01') else '❌'}")
        
    finally:
        db.close()


if __name__ == "__main__":
    quick_check()
