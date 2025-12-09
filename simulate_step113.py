"""
模拟执行步骤113的SQL，看看会产生多少条记录
"""
import os
import sys
sys.path.insert(0, 'backend')
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv('backend/.env')
DATABASE_URL = os.getenv('DATABASE_URL')
engine = create_engine(DATABASE_URL)

def simulate():
    with engine.connect() as conn:
        print("=" * 80)
        print("模拟执行步骤113的SQL（不实际插入）")
        print("=" * 80)
        
        # 模拟步骤113的SQL
        result = conn.execute(text("""
            SELECT 
                mn.id as node_id,
                d.id as department_id,
                mn.name as node_name,
                mn.code as node_code,
                SUM(ws.stat_value) as workload
            FROM workload_statistics ws
            INNER JOIN model_nodes mn ON ws.stat_type = mn.code
            INNER JOIN departments d ON ws.department_code = d.accounting_unit_code
            WHERE ws.stat_month = '2025-10'
              AND mn.version_id = 26
              AND mn.node_type = 'dimension'
              AND d.hospital_id = 1
              AND d.is_active = TRUE
              AND (
                mn.code LIKE 'dim-nur-bed%'
                OR mn.code LIKE 'dim-nur-trans%'
                OR mn.code LIKE 'dim-nur-op%'
                OR mn.code LIKE 'dim-nur-or%'
              )
            GROUP BY mn.id, d.id, mn.name, mn.code, mn.parent_id, mn.weight
        """))
        
        rows = list(result)
        print(f"模拟执行结果: {len(rows)} 条记录")
        
        if rows:
            print("\n样本数据:")
            for row in rows[:10]:
                print(f"  {row.node_code} - 科室{row.department_id}: workload={row.workload}")
        
        # 检查 workload_statistics 表中的数据
        print("\n" + "=" * 80)
        print("检查 workload_statistics 表中的数据")
        print("=" * 80)
        
        result = conn.execute(text("""
            SELECT 
                stat_type,
                COUNT(*) as count,
                COUNT(DISTINCT department_code) as dept_count
            FROM workload_statistics
            WHERE stat_month = '2025-10'
            GROUP BY stat_type
            ORDER BY stat_type
        """))
        
        for row in result:
            print(f"  {row.stat_type}: {row.count} 条记录, {row.dept_count} 个科室")

if __name__ == '__main__':
    simulate()
