"""
修复业务导向调整步骤的SQL - 使用orientation_rule_ids数组字段
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# 加载环境变量
load_dotenv('backend/.env')

DATABASE_URL = os.getenv('DATABASE_URL')
engine = create_engine(DATABASE_URL)

# 读取修复后的SQL文件
with open('backend/standard_workflow_templates/step3a_orientation_adjustment.sql', 'r', encoding='utf-8') as f:
    new_sql = f.read()

print(f"SQL长度: {len(new_sql)} 字符")

# 更新数据库
with engine.connect() as conn:
    # 查找业务导向调整步骤
    result = conn.execute(text("""
        SELECT cs.id, cs.workflow_id, cw.name as workflow_name
        FROM calculation_steps cs
        JOIN calculation_workflows cw ON cs.workflow_id = cw.id
        WHERE cs.name = '业务导向调整'
    """))
    
    steps = result.fetchall()
    print(f"\n找到 {len(steps)} 个业务导向调整步骤:")
    for step in steps:
        print(f"  步骤ID: {step.id}, 流程ID: {step.workflow_id}, 流程名称: {step.workflow_name}")
    
    if not steps:
        print("错误: 未找到业务导向调整步骤")
        sys.exit(1)
    
    # 更新所有业务导向调整步骤的SQL
    for step in steps:
        conn.execute(text("""
            UPDATE calculation_steps
            SET code_content = :sql,
                updated_at = NOW()
            WHERE id = :step_id
        """), {"sql": new_sql, "step_id": step.id})
        print(f"\n✓ 已更新步骤 {step.id} 的SQL")
    
    conn.commit()
    print("\n✓ 所有步骤SQL已更新")
    
    # 验证更新
    result = conn.execute(text("""
        SELECT id, LENGTH(code_content) as sql_length
        FROM calculation_steps
        WHERE name = '业务导向调整'
    """))
    
    print("\n验证结果:")
    for row in result:
        print(f"  步骤ID: {row.id}, SQL长度: {row.sql_length}")

print("\n✓ 修复完成！")
