import sys
sys.path.insert(0, 'backend')

from app.database import SessionLocal
from sqlalchemy import text

db = SessionLocal()

# 测试查询 model_nodes 的 parent_id
result = db.execute(text("""
    SELECT mn.id, mn.code, mn.name, mn.parent_id 
    FROM model_nodes mn 
    INNER JOIN model_versions mv ON mn.version_id = mv.id 
    WHERE mv.hospital_id = 1 
      AND mv.is_active = TRUE 
      AND mn.node_type = 'dimension' 
    LIMIT 10
"""))

rows = result.fetchall()
print('id | code | name | parent_id')
print('-' * 80)
for r in rows:
    print(f'{r[0]} | {r[1]} | {r[2]} | {r[3]}')

db.close()
