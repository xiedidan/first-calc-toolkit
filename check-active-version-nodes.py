import sys
sys.path.insert(0, 'backend')

from app.database import SessionLocal
from sqlalchemy import text

db = SessionLocal()

# 查询当前激活版本
result = db.execute(text("""
    SELECT id, hospital_id, name, is_active 
    FROM model_versions 
    WHERE hospital_id = 1 
    ORDER BY is_active DESC, id DESC 
    LIMIT 5
"""))

print("=== 模型版本 ===")
print('id | hospital_id | name | is_active')
print('-' * 80)
for r in result.fetchall():
    print(f'{r[0]} | {r[1]} | {r[2]} | {r[3]}')

# 查询激活版本的维度节点
result = db.execute(text("""
    SELECT mn.id, mn.code, mn.name, mn.parent_id, mn.version_id
    FROM model_nodes mn 
    INNER JOIN model_versions mv ON mn.version_id = mv.id 
    WHERE mv.hospital_id = 1 
      AND mv.is_active = TRUE 
      AND mn.node_type = 'dimension' 
    ORDER BY mn.id
    LIMIT 20
"""))

print("\n=== 激活版本的维度节点 ===")
print('id | code | name | parent_id | version_id')
print('-' * 100)
for r in result.fetchall():
    print(f'{r[0]} | {r[1]} | {r[2]} | {r[3]} | {r[4]}')

db.close()
