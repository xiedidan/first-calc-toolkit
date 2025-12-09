"""
检查数据库中各步骤的SQL
"""
import os
import sys
sys.path.insert(0, 'backend')

from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv('backend/.env')

DATABASE_URL = os.getenv('DATABASE_URL')
engine = create_engine(DATABASE_URL)

with engine.connect().execution_options(isolation_level="AUTOCOMMIT") as conn:
    # 获取流程30的步骤
    result = conn.execute(text("""
        SELECT cs.id, cs.name, cs.sort_order, LENGTH(cs.code_content) as sql_len,
               SUBSTRING(cs.code_content, 1, 500) as sql_preview
        FROM calculation_steps cs
        WHERE cs.workflow_id = 30
        ORDER BY cs.sort_order
    """))
    
    for row in result:
        print("=" * 80)
        print(f"步骤 {row.id}: {row.name} (排序: {row.sort_order}, SQL长度: {row.sql_len})")
        print("-" * 80)
        print(row.sql_preview)
        print()
