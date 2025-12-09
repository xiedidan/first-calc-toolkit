"""更新指定的Step 5步骤"""
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

# 指定要更新的步骤ID
STEP_IDS = [67, 75, 80, 85]

print("更新Step 5权重问题")
print("=" * 80)

with engine.connect() as conn:
    # 查询这些步骤的信息
    result = conn.execute(text("""
        SELECT 
            cs.id,
            cs.workflow_id,
            w.name as workflow_name,
            cs.name as step_name
        FROM calculation_steps cs
        INNER JOIN calculation_workflows w ON cs.workflow_id = w.id
        WHERE cs.id = ANY(:step_ids)
        ORDER BY cs.id
    """), {"step_ids": STEP_IDS})
    
    steps = result.fetchall()
    
    if not steps:
        print("未找到指定的步骤")
        exit(1)
    
    print(f"\n将更新以下 {len(steps)} 个步骤:")
    for step in steps:
        print(f"  - 步骤ID: {step.id}, 工作流: {step.workflow_name}, 步骤: {step.step_name}")
    
    # 更新每个步骤的SQL
    updated_count = 0
    for step in steps:
        try:
            conn.execute(
                text("""
                    UPDATE calculation_steps
                    SET code_content = :sql,
                        updated_at = NOW()
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
print("修复内容:")
print("1. dimension_results CTE: 使用cr.weight（调整后）而不是ms.weight（原始）")
print("2. 非叶子节点: original_weight设置为NULL")
print("\n下一步:")
print("1. 删除旧的计算结果")
print("2. 重新运行计算任务")
print("3. 验证weight和original_weight字段")
