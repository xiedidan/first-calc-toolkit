"""
调试汇总表问题
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal
from app.models.calculation_task import CalculationTask, CalculationResult, CalculationSummary
from decimal import Decimal

def debug_summary():
    """调试汇总表"""
    db = SessionLocal()
    
    try:
        # 查找最新的任务
        task = db.query(CalculationTask).filter(
            CalculationTask.status == "completed"
        ).order_by(CalculationTask.completed_at.desc()).first()
        
        if not task:
            print("未找到已完成的计算任务")
            return
        
        print("=" * 80)
        print(f"任务ID: {task.task_id}")
        print(f"周期: {task.period}")
        print("=" * 80)
        
        # 选择一个科室进行调试（科室ID=3）
        dept_id = 3
        
        print(f"\n科室ID: {dept_id}")
        print("-" * 80)
        
        # 1. 查看序列结果
        print("\n1. 序列结果:")
        sequence_results = db.query(CalculationResult).filter(
            CalculationResult.task_id == task.task_id,
            CalculationResult.department_id == dept_id,
            CalculationResult.node_type == "sequence"
        ).all()
        
        print(f"找到 {len(sequence_results)} 个序列:\n")
        
        for seq in sequence_results:
            print(f"  节点ID: {seq.node_id}")
            print(f"  名称: {seq.node_name}")
            print(f"  价值: {seq.value}")
            
            # 判断序列类型
            node_name_lower = seq.node_name.lower()
            seq_type = "未识别"
            
            if "医生" in seq.node_name or "医疗" in seq.node_name or "医师" in seq.node_name or \
               "doctor" in node_name_lower or "physician" in node_name_lower:
                seq_type = "医生序列"
            elif "护理" in seq.node_name or "护士" in seq.node_name or \
                 "nurse" in node_name_lower or "nursing" in node_name_lower:
                seq_type = "护理序列"
            elif "医技" in seq.node_name or "技师" in seq.node_name or \
                 "tech" in node_name_lower or "technician" in node_name_lower:
                seq_type = "医技序列"
            
            print(f"  判断为: {seq_type}")
            print()
        
        # 2. 手动计算序列价值（验证）
        print("\n2. 手动验证序列价值:")
        
        all_dimensions = db.query(CalculationResult).filter(
            CalculationResult.task_id == task.task_id,
            CalculationResult.department_id == dept_id,
            CalculationResult.node_type == "dimension"
        ).all()
        
        print(f"找到 {len(all_dimensions)} 个维度\n")
        
        for seq in sequence_results:
            print(f"序列: {seq.node_name}")
            
            # 找出属于该序列的所有维度
            dimension_map = {d.node_id: d for d in all_dimensions}
            
            def belongs_to_sequence(dim_result, seq_id):
                """判断维度是否属于某个序列"""
                current = dim_result
                while current:
                    if current.parent_id == seq_id:
                        return True
                    current = dimension_map.get(current.parent_id)
                return False
            
            sequence_dimensions = [
                d for d in all_dimensions 
                if belongs_to_sequence(d, seq.node_id)
            ]
            
            # 找出末级维度
            parent_ids = {d.parent_id for d in all_dimensions}
            leaf_dimensions = [
                d for d in sequence_dimensions
                if d.node_id not in parent_ids
            ]
            
            # 计算总价值
            total_value = sum((d.value or Decimal("0")) for d in leaf_dimensions)
            
            print(f"  属于该序列的维度数: {len(sequence_dimensions)}")
            print(f"  末级维度数: {len(leaf_dimensions)}")
            print(f"  计算的总价值: {total_value}")
            print(f"  数据库中的价值: {seq.value}")
            print(f"  是否一致: {'✓' if total_value == seq.value else '✗'}")
            print()
        
        # 3. 查看汇总表
        print("\n3. 汇总表数据:")
        summary = db.query(CalculationSummary).filter(
            CalculationSummary.task_id == task.task_id,
            CalculationSummary.department_id == dept_id
        ).first()
        
        if summary:
            print(f"  医生价值: {summary.doctor_value}")
            print(f"  护理价值: {summary.nurse_value}")
            print(f"  医技价值: {summary.tech_value}")
            print(f"  总价值: {summary.total_value}")
        else:
            print("  未找到汇总数据")
        
        # 4. 对比
        print("\n4. 对比分析:")
        
        doctor_seq_value = Decimal("0")
        nurse_seq_value = Decimal("0")
        tech_seq_value = Decimal("0")
        
        for seq in sequence_results:
            value = seq.value or Decimal("0")
            node_name_lower = seq.node_name.lower()
            
            if "医生" in seq.node_name or "医疗" in seq.node_name or "医师" in seq.node_name or \
               "doctor" in node_name_lower or "physician" in node_name_lower:
                doctor_seq_value += value
            elif "护理" in seq.node_name or "护士" in seq.node_name or \
                 "nurse" in node_name_lower or "nursing" in node_name_lower:
                nurse_seq_value += value
            elif "医技" in seq.node_name or "技师" in seq.node_name or \
                 "tech" in node_name_lower or "technician" in node_name_lower:
                tech_seq_value += value
        
        print(f"  序列结果汇总:")
        print(f"    医生: {doctor_seq_value}")
        print(f"    护理: {nurse_seq_value}")
        print(f"    医技: {tech_seq_value}")
        print(f"    总计: {doctor_seq_value + nurse_seq_value + tech_seq_value}")
        
        if summary:
            print(f"\n  汇总表数据:")
            print(f"    医生: {summary.doctor_value}")
            print(f"    护理: {summary.nurse_value}")
            print(f"    医技: {summary.tech_value}")
            print(f"    总计: {summary.total_value}")
            
            print(f"\n  差异:")
            print(f"    医生: {abs(doctor_seq_value - summary.doctor_value)}")
            print(f"    护理: {abs(nurse_seq_value - summary.nurse_value)}")
            print(f"    医技: {abs(tech_seq_value - summary.tech_value)}")
        
        print("\n" + "=" * 80)
        
    finally:
        db.close()

if __name__ == "__main__":
    debug_summary()
