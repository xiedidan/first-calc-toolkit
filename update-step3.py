import sys
sys.path.insert(0, 'backend')

from app.database import SessionLocal
from app.models.calculation_step import CalculationStep

db = SessionLocal()

# 读取新的 Step3 SQL
with open('backend/standard_workflow_templates/step3_value_aggregation.sql', 'r', encoding='utf-8') as f:
    new_sql = f.read()

# 查找 workflow_id=20 的 Step3
step3 = db.query(CalculationStep).filter(
    CalculationStep.workflow_id == 20,
    CalculationStep.sort_order == 3.00
).first()

if step3:
    print(f"找到 Step3: {step3.name}")
    print(f"当前 SQL 长度: {len(step3.code_content)} 字符")
    
    # 更新 SQL
    step3.code_content = new_sql
    step3.description = '根据模型结构和权重汇总各科室的业务价值，并将序列节点数据插入到 calculation_results'
    
    db.commit()
    
    print(f"更新后 SQL 长度: {len(step3.code_content)} 字符")
    print("Step3 更新成功！")
else:
    print("未找到 Step3")

db.close()
