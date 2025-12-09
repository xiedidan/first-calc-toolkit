"""
测试护理业务价值计算步骤
"""
import sys
import os
from dotenv import load_dotenv

load_dotenv('backend/.env')
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.calculation_workflow import CalculationWorkflow
from app.models.calculation_step import CalculationStep
from app.models.calculation_task import CalculationTask
from app.models.model_version import ModelVersion
import uuid
from datetime import datetime

def test_nursing_workflow():
    """测试护理业务价值计算步骤"""
    db = SessionLocal()
    
    try:
        workflow_id = 31
        version_id = 26
        period = "2023-10"
        hospital_id = 1
        
        # 检查工作流
        workflow = db.query(CalculationWorkflow).filter(CalculationWorkflow.id == workflow_id).first()
        if not workflow:
            print(f"错误: 工作流 {workflow_id} 不存在")
            return
        
        print(f"工作流: {workflow.name}")
        
        # 检查步骤
        steps = db.query(CalculationStep).filter(
            CalculationStep.workflow_id == workflow_id
        ).order_by(CalculationStep.sort_order).all()
        
        print(f"\n步骤列表:")
        for step in steps:
            print(f"  {step.sort_order}. {step.name}")
        
        # 检查护理步骤
        nursing_step = db.query(CalculationStep).filter(
            CalculationStep.workflow_id == workflow_id,
            CalculationStep.name == "护理业务价值计算"
        ).first()
        
        if not nursing_step:
            print("\n错误: 护理业务价值计算步骤不存在")
            return
        
        print(f"\n护理步骤详情:")
        print(f"  ID: {nursing_step.id}")
        print(f"  名称: {nursing_step.name}")
        print(f"  排序: {nursing_step.sort_order}")
        print(f"  数据源ID: {nursing_step.data_source_id}")
        
        # 检查数据可用性
        print(f"\n数据可用性检查:")
        
        # 检查charge_details中的护理数据
        from sqlalchemy import text
        
        charge_query = text("""
            SELECT COUNT(DISTINCT cd.item_code) as item_count,
                   COUNT(*) as record_count,
                   SUM(cd.amount) as total_amount
            FROM charge_details cd
            INNER JOIN dimension_item_mappings dim ON cd.item_code = dim.item_code
            WHERE dim.dimension_code LIKE 'dim-nur%'
              AND TO_CHAR(cd.charge_time, 'YYYY-MM') = :period
        """)
        
        result = db.execute(charge_query, {"period": period}).fetchone()
        print(f"  charge_details中的护理数据:")
        print(f"    项目数: {result[0]}")
        print(f"    记录数: {result[1]}")
        print(f"    总金额: {result[2]}")
        
        # 检查workload_statistics中的护理数据
        workload_query = text("""
            SELECT COUNT(*) as record_count,
                   SUM(stat_value) as total_workload
            FROM workload_statistics
            WHERE stat_type LIKE 'dim-nur%'
              AND stat_month = :period
        """)
        
        result = db.execute(workload_query, {"period": period}).fetchone()
        print(f"  workload_statistics中的护理数据:")
        print(f"    记录数: {result[0]}")
        print(f"    总工作量: {result[1]}")
        
        # 检查科室对照
        dept_query = text("""
            SELECT COUNT(*) as dept_count
            FROM departments
            WHERE hospital_id = :hospital_id
              AND is_active = TRUE
              AND accounting_unit_code IS NOT NULL
        """)
        
        result = db.execute(dept_query, {"hospital_id": hospital_id}).fetchone()
        print(f"  可用科室数(有核算单元): {result[0]}")
        
        print(f"\n✓ 护理业务价值计算步骤已就绪")
        print(f"\n提示:")
        print(f"  1. 可以在前端「计算流程管理」中测试完整流程")
        print(f"  2. 选择周期: {period}")
        print(f"  3. 当前有8个维度未覆盖(需要workload_statistics数据):")
        print(f"     - 监测护理、手术管理(4个)、手术室(3个)")
        
    except Exception as e:
        print(f"错误: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    test_nursing_workflow()
