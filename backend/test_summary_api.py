"""
测试科室汇总API
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal
from app.models.calculation_task import CalculationTask
from app.api.calculation_tasks import get_results_summary
from app.models.user import User
from unittest.mock import Mock


def test_summary_api():
    """测试汇总API"""
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
        result = get_results_summary(
            period=task.period,
            model_version_id=None,
            department_id=None,
            db=db,
            current_user=mock_user
        )
        
        print("API返回结果:")
        print(f"任务ID: {result['task_id']}")
        print()
        
        print("全院汇总:")
        summary = result['summary']
        print(f"  医生: {summary.doctor_value} ({summary.doctor_ratio:.2f}%)")
        print(f"  护理: {summary.nurse_value} ({summary.nurse_ratio:.2f}%)")
        print(f"  医技: {summary.tech_value} ({summary.tech_ratio:.2f}%)")
        print(f"  总计: {summary.total_value}")
        print()
        
        print(f"科室数据 ({len(result['departments'])} 个):")
        for dept in result['departments'][:5]:  # 只显示前5个
            print(f"\n  {dept.department_name}:")
            print(f"    医生: {dept.doctor_value} ({dept.doctor_ratio:.2f}%)")
            print(f"    护理: {dept.nurse_value} ({dept.nurse_ratio:.2f}%)")
            print(f"    医技: {dept.tech_value} ({dept.tech_ratio:.2f}%)")
            print(f"    总计: {dept.total_value}")
        
        if len(result['departments']) > 5:
            print(f"\n  ... 还有 {len(result['departments']) - 5} 个科室")
        
        print()
        print("✅ API测试完成")
        
    except Exception as e:
        print(f"❌ 错误: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    test_summary_api()
