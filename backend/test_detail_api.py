"""
测试明细API返回的数据结构
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal
from app.models.calculation_task import CalculationTask
from sqlalchemy import desc

def test_detail_structure():
    """测试明细数据结构"""
    db = SessionLocal()
    
    try:
        # 获取最新的任务
        task = db.query(CalculationTask).filter(
            CalculationTask.status == "completed"
        ).order_by(desc(CalculationTask.created_at)).first()
        
        if not task:
            print("❌ 没有找到已完成的任务")
            return
        
        print(f"✅ 找到任务: {task.task_id}")
        print(f"   周期: {task.period}")
        print(f"   状态: {task.status}")
        print()
        
        # 模拟API调用
        from app.api.calculation_tasks import get_results_detail
        from app.models.department import Department
        from app.api.deps import get_db
        
        # 获取第一个科室
        dept = db.query(Department).filter(Department.is_active == True).first()
        if not dept:
            print("❌ 没有找到启用的科室")
            return
        
        print(f"✅ 测试科室: {dept.his_name} (ID: {dept.id})")
        print()
        
        # 直接调用API逻辑（不通过HTTP）
        from app.models.calculation_task import CalculationResult
        from app.models.model_node import ModelNode
        
        results = db.query(CalculationResult).filter(
            CalculationResult.task_id == task.task_id,
            CalculationResult.department_id == dept.id
        ).order_by(CalculationResult.node_id).all()
        
        print(f"✅ 找到 {len(results)} 条计算结果")
        print()
        
        # 查看前几条数据
        print("前5条数据:")
        print("-" * 80)
        for i, result in enumerate(results[:5], 1):
            print(f"{i}. 节点: {result.node_name}")
            print(f"   类型: {result.node_type}")
            print(f"   父节点ID: {result.parent_id}")
            print(f"   工作量: {result.workload}")
            print(f"   权重: {result.weight}")
            print(f"   价值: {result.value}")
            print(f"   占比: {result.ratio}")
            
            # 查询节点信息
            node = db.query(ModelNode).filter(ModelNode.id == result.node_id).first()
            if node:
                print(f"   业务导向: {node.business_guide}")
            print()
        
        print("=" * 80)
        print("✅ 测试完成")
        
    except Exception as e:
        print(f"❌ 错误: {str(e)}")
        import traceback
        traceback.print_exc()
    
    finally:
        db.close()

if __name__ == "__main__":
    test_detail_structure()
