"""
检查序列名称，诊断汇总表问题
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal
from app.models.model_node import ModelNode
from app.models.model_version import ModelVersion
from app.models.calculation_task import CalculationResult

def check_sequence_names():
    """检查序列名称"""
    db = SessionLocal()
    
    try:
        # 1. 查看模型中的序列节点
        print("=" * 80)
        print("模型中的序列节点")
        print("=" * 80)
        
        active_version = db.query(ModelVersion).filter(
            ModelVersion.is_active == True
        ).first()
        
        if not active_version:
            print("未找到激活的模型版本")
            return
        
        print(f"模型版本: {active_version.name} (ID: {active_version.id})\n")
        
        sequences = db.query(ModelNode).filter(
            ModelNode.version_id == active_version.id,
            ModelNode.node_type == "sequence"
        ).order_by(ModelNode.sort_order).all()
        
        print(f"找到 {len(sequences)} 个序列节点:\n")
        
        for seq in sequences:
            print(f"ID: {seq.id:3d} | 名称: {seq.name:30s} | 编码: {seq.code}")
            
            # 判断序列类型
            seq_type = "未知"
            if "医生" in seq.name or "医疗" in seq.name or "医师" in seq.name:
                seq_type = "医生序列"
            elif "护理" in seq.name or "护士" in seq.name:
                seq_type = "护理序列"
            elif "医技" in seq.name or "技师" in seq.name:
                seq_type = "医技序列"
            
            print(f"      判断为: {seq_type}")
            print()
        
        # 2. 查看计算结果中的序列数据
        print("=" * 80)
        print("计算结果中的序列数据（示例：科室ID=3）")
        print("=" * 80)
        
        # 查找最新的任务
        from app.models.calculation_task import CalculationTask
        task = db.query(CalculationTask).filter(
            CalculationTask.status == "completed"
        ).order_by(CalculationTask.completed_at.desc()).first()
        
        if not task:
            print("未找到已完成的计算任务")
            return
        
        print(f"任务ID: {task.task_id}")
        print(f"周期: {task.period}\n")
        
        seq_results = db.query(CalculationResult).filter(
            CalculationResult.task_id == task.task_id,
            CalculationResult.department_id == 3,
            CalculationResult.node_type == "sequence"
        ).all()
        
        print(f"找到 {len(seq_results)} 条序列结果:\n")
        
        total_doctor = 0
        total_nurse = 0
        total_tech = 0
        
        for result in seq_results:
            value = result.value or 0
            
            # 判断序列类型
            seq_type = "未知"
            if "医生" in result.node_name or "医疗" in result.node_name or "医师" in result.node_name:
                seq_type = "医生序列"
                total_doctor += value
            elif "护理" in result.node_name or "护士" in result.node_name:
                seq_type = "护理序列"
                total_nurse += value
            elif "医技" in result.node_name or "技师" in result.node_name:
                seq_type = "医技序列"
                total_tech += value
            
            print(f"节点ID: {result.node_id:3d} | 名称: {result.node_name:30s} | 价值: {value:12,.2f}")
            print(f"            判断为: {seq_type}")
            print()
        
        print("-" * 80)
        print(f"汇总:")
        print(f"  医生序列总价值: {total_doctor:12,.2f}")
        print(f"  护理序列总价值: {total_nurse:12,.2f}")
        print(f"  医技序列总价值: {total_tech:12,.2f}")
        print(f"  总计: {total_doctor + total_nurse + total_tech:12,.2f}")
        print("=" * 80)
        
        # 3. 查看汇总表数据
        print("\n汇总表数据（科室ID=3）")
        print("=" * 80)
        
        from app.models.calculation_task import CalculationSummary
        summary = db.query(CalculationSummary).filter(
            CalculationSummary.task_id == task.task_id,
            CalculationSummary.department_id == 3
        ).first()
        
        if summary:
            print(f"医生价值: {summary.doctor_value:12,.2f}")
            print(f"护理价值: {summary.nurse_value:12,.2f}")
            print(f"医技价值: {summary.tech_value:12,.2f}")
            print(f"总价值: {summary.total_value:12,.2f}")
        else:
            print("未找到汇总数据")
        
        print("=" * 80)
        
        # 4. 诊断问题
        if summary:
            print("\n问题诊断:")
            print("=" * 80)
            
            issues = []
            
            if total_doctor != float(summary.doctor_value):
                issues.append(f"医生序列: 计算结果={total_doctor:,.2f}, 汇总表={float(summary.doctor_value):,.2f}")
            
            if total_nurse != float(summary.nurse_value):
                issues.append(f"护理序列: 计算结果={total_nurse:,.2f}, 汇总表={float(summary.nurse_value):,.2f}")
            
            if total_tech != float(summary.tech_value):
                issues.append(f"医技序列: 计算结果={total_tech:,.2f}, 汇总表={float(summary.tech_value):,.2f}")
            
            if issues:
                print("⚠️  发现不一致:")
                for issue in issues:
                    print(f"  - {issue}")
                
                print("\n可能原因:")
                print("1. 序列名称不包含关键字（医生/医疗/医师、护理/护士、医技/技师）")
                print("2. 序列名称判断逻辑有误")
                print("3. 数据生成时序列价值计算错误")
            else:
                print("✓ 数据一致，无问题")
            
            print("=" * 80)
    
    finally:
        db.close()

if __name__ == "__main__":
    check_sequence_names()
