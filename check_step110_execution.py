"""
检查步骤110的执行情况
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
        task_uuid = '83289d5f-df1f-4739-afdb-5aa76934eb2a'
        
        # 检查步骤110的SQL
        print("=" * 80)
        print("步骤110的SQL内容")
        print("=" * 80)
        
        result = conn.execute(text("""
            SELECT code_content
            FROM calculation_steps
            WHERE id = 110
        """))
        
        row = result.fetchone()
        if row:
            sql = row.code_content
            # 检查SQL中是否有多个INSERT语句
            insert_count = sql.count('INSERT INTO calculation_results')
            print(f"SQL中INSERT语句数量: {insert_count}")
            
            # 检查SQL中是否有循环或重复逻辑
            if 'UNION ALL' in sql:
                union_count = sql.count('UNION ALL')
                print(f"SQL中UNION ALL数量: {union_count}")
        
        # 检查第一批和第二批插入的记录是否完全相同
        print("\n" + "=" * 80)
        print("比较第一批和第二批插入的记录")
        print("=" * 80)
        
        result = conn.execute(text("""
            WITH batch1 AS (
                SELECT node_code, node_name, department_id, workload, value
                FROM calculation_results
                WHERE task_id = :task_id
                  AND created_at = '2025-12-05 13:17:23.525747'
            ),
            batch2 AS (
                SELECT node_code, node_name, department_id, workload, value
                FROM calculation_results
                WHERE task_id = :task_id
                  AND created_at = '2025-12-05 13:17:25.001773'
            )
            SELECT 
                b1.node_code,
                b1.department_id,
                b1.workload as workload1,
                b2.workload as workload2,
                CASE WHEN b1.workload = b2.workload THEN '相同' ELSE '不同' END as comparison
            FROM batch1 b1
            FULL OUTER JOIN batch2 b2 ON b1.node_code = b2.node_code AND b1.department_id = b2.department_id
            WHERE b1.workload != b2.workload OR b1.workload IS NULL OR b2.workload IS NULL
            LIMIT 10
        """), {"task_id": task_uuid})
        
        diffs = list(result)
        if diffs:
            print("发现不同的记录:")
            for row in diffs:
                print(f"  {row.node_code} - 科室{row.department_id}: {row.workload1} vs {row.workload2}")
        else:
            print("两批记录完全相同！")
        
        # 检查是否有多个步骤使用了相同的SQL
        print("\n" + "=" * 80)
        print("检查是否有多个步骤使用了相同的SQL")
        print("=" * 80)
        
        result = conn.execute(text("""
            SELECT 
                id,
                name,
                sort_order,
                LENGTH(code_content) as sql_length
            FROM calculation_steps
            WHERE workflow_id = 30
            ORDER BY sort_order
        """))
        
        for row in result:
            print(f"  步骤 {row.id} ({row.name}): {row.sql_length} 字符")

if __name__ == '__main__':
    check()
