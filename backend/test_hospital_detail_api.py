"""
测试全院汇总明细API
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal
from app.models.calculation_task import CalculationTask
from app.api.calculation_tasks import get_hospital_detail
from app.models.user import User
from unittest.mock import Mock


def test_hospital_detail_api():
    """测试全院汇总明细API"""
    db = SessionLocal()
    try:
        # 找最新任务
        task = db.query(CalculationTask).filter(
            CalculationTask.status == "completed"
        ).order_by(CalculationTask.created_at.desc()).first()
        
        if not task:
            print("❌ 未找到已完成的任务")
            return
        
        print(f"测试任务: {task.task_id}")
        print(f"周期: {task.period}")
        print()
        
        # 模拟用户
        mock_user = Mock(spec=User)
        mock_user.id = 1
        
        # 调用API
        result = get_hospital_detail(
            task_id=task.task_id,
            db=db,
            current_user=mock_user
        )
        
        print("API返回结果:")
        print(f"科室: {result['department_name']}")
        print(f"周期: {result['period']}")
        print()
        
        print(f"序列数据 ({len(result['sequences'])} 个):")
        for seq in result['sequences']:
            print(f"  {seq.sequence_name}: {seq.total_value}")
            print(f"    维度数: {len(seq.dimensions)}")
        print()
        
        print("医生序列表格数据:")
        print(f"  行数: {len(result['doctor'])}")
        if result['doctor']:
            first_row = result['doctor'][0]
            print(f"  第一行: {first_row['dimension_name']}")
            print(f"    工作量: {first_row['workload']}")
            print(f"    金额: {first_row['amount']}")
            print(f"    占比: {first_row['ratio']}%")
            if 'children' in first_row:
                print(f"    子节点数: {len(first_row['children'])}")
        print()
        
        print("护理序列表格数据:")
        print(f"  行数: {len(result['nurse'])}")
        print()
        
        print("医技序列表格数据:")
        print(f"  行数: {len(result['tech'])}")
        print()
        
        print("✅ API测试完成")
        
    except Exception as e:
        print(f"❌ 错误: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    test_hospital_detail_api()
