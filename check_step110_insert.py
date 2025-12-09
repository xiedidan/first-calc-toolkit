"""
检查步骤110的INSERT语句是否有问题
"""
import os
import sys
sys.path.insert(0, 'backend')
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv('backend/.env')
DATABASE_URL = os.getenv('DATABASE_URL')
engine = create_engine(DATABASE_URL)

def check():
    with engine.connect() as conn:
        # 检查步骤110的SQL中是否有多个INSERT语句
        result = conn.execute(text("""
            SELECT code_content
            FROM calculation_steps
            WHERE id = 110
        """))
        
        row = result.fetchone()
        if row:
            sql = row.code_content
            
            # 统计INSERT语句数量
            insert_count = sql.upper().count('INSERT INTO')
            print(f"步骤110中 INSERT INTO 出现次数: {insert_count}")
            
            # 检查SQL中是否有UNION ALL
            union_count = sql.upper().count('UNION ALL')
            print(f"步骤110中 UNION ALL 出现次数: {union_count}")
            
            # 检查SQL中是否有多个SELECT
            select_count = sql.upper().count('SELECT')
            print(f"步骤110中 SELECT 出现次数: {select_count}")
        
        # 检查步骤110实际插入的数据
        print("\n" + "=" * 80)
        print("检查步骤110实际插入的数据（批次1）")
        print("=" * 80)
        
        task_uuid = '83289d5f-df1f-4739-afdb-5aa76934eb2a'
        
        result = conn.execute(text("""
            SELECT 
                node_code,
                COUNT(*) as count
            FROM calculation_results
            WHERE task_id = :task_id
              AND created_at + INTERVAL '8 hours' = '2025-12-05 21:17:23.525747'
            GROUP BY node_code
            ORDER BY node_code
        """), {"task_id": task_uuid})
        
        print("批次1的维度分布:")
        for row in result:
            print(f"  {row.node_code}: {row.count} 条")

if __name__ == '__main__':
    check()
