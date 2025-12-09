"""
重新检查时间戳
"""
import os
import sys
sys.path.insert(0, 'backend')
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv('backend/.env')
DATABASE_URL = os.getenv('DATABASE_URL')
engine = create_engine(DATABASE_URL)

def recheck():
    with engine.connect() as conn:
        task_uuid = '83289d5f-df1f-4739-afdb-5aa76934eb2a'
        
        # 获取所有记录的插入时间分布
        print("=" * 80)
        print("所有记录的插入时间分布（精确到毫秒）")
        print("=" * 80)
        
        result = conn.execute(text("""
            SELECT 
                created_at,
                COUNT(*) as count,
                STRING_AGG(DISTINCT node_code, ', ' ORDER BY node_code) as sample_codes
            FROM calculation_results
            WHERE task_id = :task_id
            GROUP BY created_at
            ORDER BY created_at
        """), {"task_id": task_uuid})
        
        for row in result:
            codes = row.sample_codes[:100] + "..." if len(row.sample_codes) > 100 else row.sample_codes
            print(f"  {row.created_at}: {row.count} 条 - {codes}")
        
        # 检查步骤执行日志的时间
        print("\n" + "=" * 80)
        print("步骤执行日志的时间（原始）")
        print("=" * 80)
        
        result = conn.execute(text("""
            SELECT 
                csl.step_id,
                cs.name as step_name,
                csl.start_time,
                csl.end_time,
                csl.created_at as log_created_at
            FROM calculation_step_logs csl
            JOIN calculation_steps cs ON csl.step_id = cs.id
            WHERE csl.task_id = :task_id
            ORDER BY csl.start_time
        """), {"task_id": task_uuid})
        
        for row in result:
            print(f"  步骤 {row.step_id} ({row.step_name}):")
            print(f"    start_time: {row.start_time}")
            print(f"    end_time: {row.end_time}")
            print(f"    log_created_at: {row.log_created_at}")

if __name__ == '__main__':
    recheck()
