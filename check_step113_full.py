"""
检查步骤113的完整SQL
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
        result = conn.execute(text("""
            SELECT code_content
            FROM calculation_steps
            WHERE id = 113
        """))
        
        row = result.fetchone()
        if row:
            sql = row.code_content
            
            # 统计INSERT语句数量
            insert_count = sql.upper().count('INSERT INTO')
            print(f"INSERT INTO 出现次数: {insert_count}")
            
            # 找到所有INSERT语句的位置
            positions = []
            pos = 0
            while True:
                pos = sql.upper().find('INSERT INTO', pos)
                if pos == -1:
                    break
                positions.append(pos)
                pos += 1
            
            print(f"INSERT INTO 位置: {positions}")
            
            # 显示每个INSERT语句的前200个字符
            for i, pos in enumerate(positions):
                print(f"\n第 {i+1} 个INSERT语句 (位置 {pos}):")
                print(sql[pos:pos+300])

if __name__ == '__main__':
    check()
