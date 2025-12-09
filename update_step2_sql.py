"""
更新数据库中step2的SQL，修复门诊/住院业务类别匹配逻辑
"""
import os
import sys
sys.path.insert(0, 'backend')

from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv('backend/.env')

DATABASE_URL = os.getenv('DATABASE_URL')
engine = create_engine(DATABASE_URL)

# 读取更新后的SQL文件
with open('backend/standard_workflow_templates/step2_dimension_catalog.sql', 'r', encoding='utf-8') as f:
    new_sql = f.read()

print(f"新SQL长度: {len(new_sql)} 字符")

with engine.connect() as conn:
    # 查找所有step2步骤 - 只更新"维度目录统计"
    result = conn.execute(text("""
        SELECT cs.id, cs.name, cw.name as workflow_name, LENGTH(cs.code_content) as sql_len
        FROM calculation_steps cs
        JOIN calculation_workflows cw ON cs.workflow_id = cw.id
        WHERE cs.name = '维度目录统计'
        ORDER BY cw.name, cs.sort_order
    """))
    
    steps = list(result)
    print(f"\n找到 {len(steps)} 个相关步骤:")
    for step in steps:
        print(f"  ID={step.id}, 名称={step.name}, 流程={step.workflow_name}, SQL长度={step.sql_len}")
    
    if steps:
        confirm = input("\n是否更新这些步骤的SQL? (y/n): ")
        if confirm.lower() == 'y':
            for step in steps:
                conn.execute(text("""
                    UPDATE calculation_steps 
                    SET code_content = :sql
                    WHERE id = :id
                """), {"sql": new_sql, "id": step.id})
            conn.commit()
            print(f"\n已更新 {len(steps)} 个步骤的SQL")
        else:
            print("\n取消更新")
    else:
        print("\n没有找到需要更新的步骤")
