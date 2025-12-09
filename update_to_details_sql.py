"""
更新数据库使用带明细记录的业务导向调整SQL
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv('backend/.env')
DATABASE_URL = os.getenv('DATABASE_URL')
engine = create_engine(DATABASE_URL)

# 读取带明细的SQL
with open('backend/standard_workflow_templates/step3a_orientation_adjustment_with_details.sql', 'r', encoding='utf-8') as f:
    new_sql = f.read()

print(f"SQL长度: {len(new_sql)} 字符")
print(f"包含 'orientation_adjustment_details': {'orientation_adjustment_details' in new_sql}")
print(f"包含 'orientation_rule_ids': {'orientation_rule_ids' in new_sql}")
print(f"包含 'UNNEST': {'UNNEST' in new_sql}")

with engine.connect() as conn:
    # 更新步骤83（流程26）
    conn.execute(text("""
        UPDATE calculation_steps
        SET code_content = :sql,
            description = '根据业务导向规则调整维度权重，并记录完整计算过程'
        WHERE id = 83
    """), {"sql": new_sql})
    
    # 也更新步骤78（流程25）
    conn.execute(text("""
        UPDATE calculation_steps
        SET code_content = :sql,
            description = '根据业务导向规则调整维度权重，并记录完整计算过程'
        WHERE id = 78
    """), {"sql": new_sql})
    
    conn.commit()
    print("\n✓ 已更新步骤78和83")
    
    # 验证
    result = conn.execute(text("""
        SELECT id, LENGTH(code_content) as sql_length,
               code_content LIKE '%orientation_adjustment_details%' as has_details,
               code_content LIKE '%UNNEST%' as has_unnest
        FROM calculation_steps
        WHERE id IN (78, 83)
    """))
    
    print("\n验证结果:")
    for row in result:
        print(f"  步骤{row.id}: 长度={row.sql_length}, 含明细表={row.has_details}, 含UNNEST={row.has_unnest}")

print("\n✓ 完成！现在SQL会插入 orientation_adjustment_details 表")
