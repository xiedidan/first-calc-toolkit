"""
直接更新数据库中的业务导向调整SQL
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv('backend/.env')
DATABASE_URL = os.getenv('DATABASE_URL')
engine = create_engine(DATABASE_URL)

# 读取修复后的SQL
with open('backend/standard_workflow_templates/step3a_orientation_adjustment.sql', 'r', encoding='utf-8') as f:
    new_sql = f.read()

print(f"SQL长度: {len(new_sql)} 字符")
print(f"检查是否包含 'updated_at': {'updated_at' in new_sql}")

with engine.connect() as conn:
    # 更新步骤83
    result = conn.execute(text("""
        SELECT LENGTH(code_content) as old_length
        FROM calculation_steps
        WHERE id = 83
    """))
    old_length = result.fetchone()[0]
    print(f"\n步骤83旧SQL长度: {old_length}")
    
    conn.execute(text("""
        UPDATE calculation_steps
        SET code_content = :sql
        WHERE id = 83
    """), {"sql": new_sql})
    
    conn.commit()
    print("✓ 已更新步骤83")
    
    # 验证
    result = conn.execute(text("""
        SELECT code_content
        FROM calculation_steps
        WHERE id = 83
    """))
    
    updated_sql = result.fetchone()[0]
    print(f"\n验证:")
    print(f"  新SQL长度: {len(updated_sql)}")
    print(f"  包含 'updated_at': {'updated_at' in updated_sql}")
    print(f"  包含 'orientation_rule_ids': {'orientation_rule_ids' in updated_sql}")

print("\n✓ 完成")
