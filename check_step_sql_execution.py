"""
检查步骤SQL的实际执行情况
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
        # 检查步骤110的SQL是否包含多个INSERT语句
        print("=" * 80)
        print("检查步骤110的SQL结构")
        print("=" * 80)
        
        result = conn.execute(text("""
            SELECT code_content
            FROM calculation_steps
            WHERE id = 110
        """))
        
        row = result.fetchone()
        if row:
            sql = row.code_content
            
            # 分割SQL语句
            statements = []
            for s in sql.split(';'):
                s = s.strip()
                if not s:
                    continue
                # 过滤掉纯注释的语句
                lines = [line.strip() for line in s.split('\n') if line.strip() and not line.strip().startswith('--')]
                if lines:
                    statements.append(s)
            
            print(f"步骤110包含 {len(statements)} 个SQL语句")
            
            for i, stmt in enumerate(statements):
                if 'INSERT' in stmt:
                    print(f"\n语句 {i+1}: INSERT语句")
                elif 'SELECT' in stmt:
                    print(f"\n语句 {i+1}: SELECT语句")
                else:
                    print(f"\n语句 {i+1}: 其他语句")
                print(f"  前100字符: {stmt[:100]}...")
        
        # 检查步骤110的执行结果
        print("\n" + "=" * 80)
        print("检查步骤110的执行日志")
        print("=" * 80)
        
        task_uuid = '83289d5f-df1f-4739-afdb-5aa76934eb2a'
        
        result = conn.execute(text("""
            SELECT 
                result_data,
                execution_info
            FROM calculation_step_logs
            WHERE task_id = :task_id
              AND step_id = 110
        """), {"task_id": task_uuid})
        
        row = result.fetchone()
        if row:
            print(f"result_data: {row.result_data}")
            print(f"execution_info: {row.execution_info}")

if __name__ == '__main__':
    check()
