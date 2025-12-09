"""
详细检查步骤113、114、115的INSERT语句
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
        for step_id in [113, 114, 115]:
            result = conn.execute(text("""
                SELECT name, code_content
                FROM calculation_steps
                WHERE id = :step_id
            """), {"step_id": step_id})
            
            row = result.fetchone()
            if row:
                sql = row.code_content
                
                print("=" * 80)
                print(f"步骤 {step_id}: {row.name}")
                print("=" * 80)
                
                # 分割SQL语句
                statements = []
                for s in sql.split(';'):
                    s = s.strip()
                    if not s:
                        continue
                    lines = [line.strip() for line in s.split('\n') if line.strip() and not line.strip().startswith('--')]
                    if lines:
                        statements.append(s)
                
                print(f"包含 {len(statements)} 个SQL语句")
                
                for i, stmt in enumerate(statements):
                    if 'INSERT' in stmt.upper():
                        print(f"\n语句 {i+1}: INSERT语句")
                        # 显示FROM和WHERE部分
                        from_pos = stmt.upper().find('FROM')
                        if from_pos > 0:
                            from_clause = stmt[from_pos:from_pos+800]
                            print(f"  FROM子句:")
                            for line in from_clause.split('\n')[:20]:
                                print(f"    {line}")
                    elif 'SELECT' in stmt.upper():
                        print(f"\n语句 {i+1}: SELECT语句 (前100字符)")
                        print(f"  {stmt[:100]}...")

if __name__ == '__main__':
    check()
