"""
测试医生业务价值计算流程
"""
import sys
import os
from dotenv import load_dotenv
from datetime import datetime
import uuid

# 加载环境变量
load_dotenv('backend/.env')

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.calculation_workflow import CalculationWorkflow
from app.models.calculation_step import CalculationStep
from app.models.calculation_task import CalculationTask
from app.models.model_version import ModelVersion


def test_doctor_workflow():
    """测试医生业务价值计算流程"""
    db = SessionLocal()
    
    try:
        # 参数配置
        workflow_id = 31  # 医生业务价值计算流程ID
        version_id = 26   # 模型版本ID
        period = "2023-10"  # 测试周期（根据charge_details中的数据）
        
        # 获取流程
        workflow = db.query(CalculationWorkflow).filter(
            CalculationWorkflow.id == workflow_id
        ).first()
        
        if not workflow:
            print(f"错误: 流程 {workflow_id} 不存在")
            return
        
        print(f"找到流程: {workflow.name} (ID: {workflow.id})")
        print(f"版本ID: {workflow.version_id}")
        print(f"描述: {workflow.description}")
        
        # 获取版本信息
        version = db.query(ModelVersion).filter(ModelVersion.id == version_id).first()
        if not version:
            print(f"错误: 版本 {version_id} 不存在")
            return
        
        print(f"\n模型版本: {version.name}")
        print(f"医院ID: {version.hospital_id}")
        
        # 获取步骤
        steps = db.query(CalculationStep).filter(
            CalculationStep.workflow_id == workflow_id,
            CalculationStep.is_enabled == True
        ).order_by(CalculationStep.sort_order).all()
        
        print(f"\n找到 {len(steps)} 个启用的步骤:")
        for step in steps:
            print(f"  - {step.name} (ID: {step.id}, 顺序: {step.sort_order})")
            print(f"    代码类型: {step.code_type}")
            print(f"    数据源ID: {step.data_source_id}")
        
        # 创建测试任务
        task_id = f"test-doctor-{datetime.now().strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:8]}"
        
        print(f"\n创建测试任务: {task_id}")
        print(f"测试周期: {period}")
        
        task = CalculationTask(
            task_id=task_id,
            model_version_id=version_id,
            workflow_id=workflow_id,
            period=period,
            status="pending",
            progress=0,
            description="测试医生业务价值计算流程"
        )
        db.add(task)
        db.commit()
        
        print(f"\n✓ 测试任务创建成功!")
        print(f"  任务ID: {task_id}")
        print(f"\n可以通过以下方式执行:")
        print(f"  1. 在前端「计算任务管理」中查看并执行")
        print(f"  2. 或使用Celery执行: celery -A app.celery_app worker --loglevel=info")
        print(f"\n查询结果:")
        print(f"  SELECT * FROM calculation_results WHERE task_id = '{task_id}' LIMIT 10;")
        
    except Exception as e:
        db.rollback()
        print(f"\n✗ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    test_doctor_workflow()
