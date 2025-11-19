"""检查数据源列表"""
from app.database import SessionLocal
from app.models.data_source import DataSource

db = SessionLocal()
try:
    sources = db.query(DataSource).all()
    print(f'数据源总数: {len(sources)}')
    for s in sources:
        print(f'ID: {s.id}, 名称: {s.name}, 类型: {s.db_type}, 主机: {s.host}')
finally:
    db.close()
