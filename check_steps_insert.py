"""
检查步骤113、114、115的INSERT语句
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
        for step_id in [110, 112, 113, 114, 115]:
            result = conn.execute(text("""
                SELECT name, code_content
                FROM calculation_steps
                WHERE id = :step_id
            """), {"step_id": step_id})
            
            row = result.fetchone()
            if row:
                sql = row.code_content
                
                # 检查INSERT语句
                insert_count = sql.count('INSERT INTO calculation_results')
                
                print("=" * 80)
                print(f"步骤 {step_id}: {row.name}")
                print(f"  INSERT INTO calculation_results 出现次数: {insert_count}")
                
                # 显示INSERT语句的前200个字符
                if 'INSERT INTO calculation_results' in sql:
                    insert_pos = sql.find('INSERT INTO calculation_results')
                    insert_sql = sql[insert_pos:insert_pos+500]
                    print(f"  INSERT语句预览:")
                    for line in insert_sql.split('\n')[:15]:
                        print(f"    {line}")

if __name__ == '__main__':
    check()
