"""
获取工作流31的医生、护理、医技步骤SQL
"""
import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv('backend/.env')
DATABASE_URL = os.getenv('DATABASE_URL')
engine = create_engine(DATABASE_URL)

def get_step_sql(step_id):
    """获取步骤SQL"""
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT id, name, description, code_content 
            FROM calculation_steps 
            WHERE id = :step_id
        """), {"step_id": step_id})
        row = result.fetchone()
        if row:
            return {
                'id': row[0],
                'name': row[1],
                'description': row[2],
                'sql': row[3]
            }
    return None

if __name__ == '__main__':
    step_ids = [117, 118, 119]  # 医生、护理、医技
    
    for step_id in step_ids:
        step = get_step_sql(step_id)
        if step:
            print(f"\n{'='*80}")
            print(f"步骤ID: {step['id']}")
            print(f"名称: {step['name']}")
            print(f"描述: {step['description']}")
            print(f"{'='*80}")
            
            # 保存到文件
            filename = f"workflow31_step{step_id}_{step['name']}.sql"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(step['sql'])
            print(f"SQL已保存到: {filename}")
