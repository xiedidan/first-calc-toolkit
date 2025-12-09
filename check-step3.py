import sys
sys.path.insert(0, 'backend')

from app.database import SessionLocal
from sqlalchemy import text

db = SessionLocal()

task_id = '124694a7-3f17-4ff3-831e-5e7efb6febe2'

# 检查 calculation_summaries 表中是否有这个任务的数据
result = db.execute(text(f"""
    SELECT 
        task_id,
        department_id,
        doctor_value,
        nurse_value,
        tech_value,
        total_value
    FROM calculation_summaries
    WHERE task_id = '{task_id}'
    ORDER BY department_id
    LIMIT 10
"""))

print(f"=== calculation_summaries 表中的数据 ===")
print('task_id | dept_id | doctor | nurse | tech | total')
print('-' * 100)
rows = result.fetchall()
if rows:
    for r in rows:
        print(f'{r[0]} | {r[1]} | {r[2]} | {r[3]} | {r[4]} | {r[5]}')
    print(f"\n总记录数: {len(rows)}")
else:
    print("没有数据！Step3 可能没有执行。")

db.close()
