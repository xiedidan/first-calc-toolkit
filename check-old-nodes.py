import sys
sys.path.insert(0, 'backend')

from app.database import SessionLocal
from sqlalchemy import text

db = SessionLocal()

# 查询旧节点的版本信息
result = db.execute(text("""
    SELECT id, code, name, parent_id, version_id 
    FROM model_nodes 
    WHERE id IN (22, 47, 223, 224, 225)
"""))

print("=== 旧节点信息 ===")
print('id | code | name | parent_id | version_id')
print('-' * 100)
for r in result.fetchall():
    print(f'{r[0]} | {r[1]} | {r[2]} | {r[3]} | {r[4]}')

# 查询这些版本的信息
result = db.execute(text("""
    SELECT DISTINCT mv.id, mv.name, mv.is_active, mv.hospital_id
    FROM model_versions mv
    INNER JOIN model_nodes mn ON mn.version_id = mv.id
    WHERE mn.id IN (22, 47, 223, 224, 225)
"""))

print("\n=== 对应的版本信息 ===")
print('version_id | name | is_active | hospital_id')
print('-' * 100)
for r in result.fetchall():
    print(f'{r[0]} | {r[1]} | {r[2]} | {r[3]}')

db.close()
