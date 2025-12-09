"""
分析步骤113为什么会插入重复数据
"""
import os
import sys
sys.path.insert(0, 'backend')
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv('backend/.env')
DATABASE_URL = os.getenv('DATABASE_URL')
engine = create_engine(DATABASE_URL)

def analyze():
    with engine.connect() as conn:
        # 检查步骤113的过滤条件
        print("=" * 80)
        print("步骤113应该只插入以下维度（根据过滤条件）:")
        print("  mn.code LIKE 'dim-nur-bed%'")
        print("  OR mn.code LIKE 'dim-nur-trans%'")
        print("  OR mn.code LIKE 'dim-nur-op%'")
        print("  OR mn.code LIKE 'dim-nur-or%'")
        print("=" * 80)
        
        # 检查批次3实际插入的维度
        task_uuid = '83289d5f-df1f-4739-afdb-5aa76934eb2a'
        
        result = conn.execute(text("""
            SELECT DISTINCT node_code, node_name
            FROM calculation_results
            WHERE task_id = :task_id
              AND created_at + INTERVAL '8 hours' = '2025-12-05 21:17:25.785584'
            ORDER BY node_code
        """), {"task_id": task_uuid})
        
        print("\n批次3实际插入的维度:")
        for row in result:
            matches_filter = (
                row.node_code.startswith('dim-nur-bed') or
                row.node_code.startswith('dim-nur-trans') or
                row.node_code.startswith('dim-nur-op') or
                row.node_code.startswith('dim-nur-or')
            )
            status = "✓ 符合" if matches_filter else "✗ 不符合"
            print(f"  {row.node_code} ({row.node_name}) - {status}")
        
        # 检查步骤113的SQL是否被正确执行
        print("\n" + "=" * 80)
        print("检查步骤113的SQL")
        print("=" * 80)
        
        result = conn.execute(text("""
            SELECT code_content
            FROM calculation_steps
            WHERE id = 113
        """))
        
        row = result.fetchone()
        if row:
            sql = row.code_content
            # 检查WHERE条件
            if 'dim-nur-bed' in sql:
                print("SQL中包含 'dim-nur-bed' 过滤条件")
            else:
                print("SQL中不包含 'dim-nur-bed' 过滤条件！")
            
            # 显示WHERE子句
            where_pos = sql.find('WHERE')
            if where_pos > 0:
                where_clause = sql[where_pos:where_pos+500]
                print(f"\nWHERE子句:")
                for line in where_clause.split('\n')[:15]:
                    print(f"  {line}")

if __name__ == '__main__':
    analyze()
