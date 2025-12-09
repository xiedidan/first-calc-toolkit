import sys
sys.path.insert(0, 'backend')

from app.database import SessionLocal
from sqlalchemy import text

db = SessionLocal()

# 读取测试 SQL
with open('test-step3-new.sql', 'r', encoding='utf-8') as f:
    sql = f.read()

try:
    result = db.execute(text(sql))
    rows = result.fetchall()
    
    print("=== Step3 序列节点汇总结果（预览）===")
    print('node_id | dept_id | node_type | node_name | node_code | parent_id | value')
    print('-' * 100)
    
    if rows:
        for r in rows:
            print(f'{r[0]} | {r[1]} | {r[2]} | {r[3]} | {r[4]} | {r[5]} | {r[6]}')
        print(f"\n总记录数: {len(rows)}")
    else:
        print("没有找到序列节点数据！")
        
except Exception as e:
    print(f"执行出错: {e}")
    import traceback
    traceback.print_exc()
finally:
    db.close()
