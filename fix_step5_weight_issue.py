"""修复Step 5使用原始权重而不是调整后权重的问题"""
import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# 加载环境变量
load_dotenv('backend/.env')

DATABASE_URL = os.getenv('DATABASE_URL')
if not DATABASE_URL:
    raise ValueError("DATABASE_URL not found in environment")

engine = create_engine(DATABASE_URL)

# 读取修复后的SQL文件
with open('backend/standard_workflow_templates/step5_value_aggregation.sql', 'r', encoding='utf-8') as f:
    new_sql = f.read()

print("修复Step 5权重问题")
print("=" * 80)

with engine.connect() as conn:
    # 查找所有使用Step 5的工作流步骤
    result = conn.execute(text("""
        SELECT 
            cs.id,
            cs.workflow_id,
            w.name as workflow_name,
            cs.name as step_name,
            cs.sort_order
        FROM calculation_steps cs
        INNER JOIN calculation_workflows w ON cs.workflow_id = w.id
        WHERE cs.name LIKE '%价值汇总%'
           OR cs.name LIKE '%value%aggregation%'
           OR cs.sort_order >= 5.0
        ORDER BY cs.workflow_id, cs.sort_order
    """))
    
    steps = result.fetchall()
    
    if not steps:
        print("未找到需要更新的步骤")
        exit(0)
    
    print(f"\n找到 {len(steps)} 个步骤需要更新:")
    for step in steps:
        print(f"  - 步骤ID: {step.id}, 工作流: {step.workflow_name}, 步骤: {step.step_name}")
    
    print("\n确认更新? (y/n): ", end='')
    confirm = input().strip().lower()
    
    if confirm != 'y':
        print("取消更新")
        exit(0)
    
    # 更新每个步骤的SQL
    updated_count = 0
    for step in steps:
        try:
            conn.execute(
                text("""
                    UPDATE calculation_steps
                    SET code_content = :sql
                    WHERE id = :step_id
                """),
                {"sql": new_sql, "step_id": step.id}
            )
            conn.commit()
            updated_count += 1
            print(f"✓ 已更新步骤 {step.id}: {step.step_name}")
        except Exception as e:
            print(f"✗ 更新步骤 {step.id} 失败: {e}")
            conn.rollback()
    
    print(f"\n更新完成: {updated_count}/{len(steps)} 个步骤")

print("\n" + "=" * 80)
print("修复说明:")
print("1. dimension_results CTE现在使用cr.weight（调整后）而不是ms.weight（原始）")
print("2. 非叶子节点的original_weight设置为NULL（因为是汇总值）")
print("3. 需要重新运行计算任务以应用修复")
print("\n下一步:")
print("1. 删除旧的计算结果: DELETE FROM calculation_results WHERE task_id = 'xxx'")
print("2. 重新运行计算任务")
print("3. 验证weight和original_weight字段是否正确")
