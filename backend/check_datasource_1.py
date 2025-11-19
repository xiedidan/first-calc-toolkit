"""
检查数据源ID=1的配置
"""
import sys
sys.path.insert(0, 'backend')

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.data_source import DataSource
from app.utils.encryption import decrypt_password
from app.config import settings

# 创建数据库连接
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

try:
    # 查询ID=1的数据源
    ds = db.query(DataSource).filter(DataSource.id == 1).first()
    
    if ds:
        print("数据源信息:")
        print(f"ID: {ds.id}")
        print(f"名称: {ds.name}")
        print(f"数据库类型: {ds.db_type}")
        print(f"主机: {ds.host}")
        print(f"端口: {ds.port}")
        print(f"数据库名: {ds.database_name}")
        print(f"用户名: {ds.username}")
        print(f"加密后的密码: {ds.password[:50]}..." if len(ds.password) > 50 else f"加密后的密码: {ds.password}")
        
        try:
            decrypted_pwd = decrypt_password(ds.password)
            print(f"解密后的密码: {decrypted_pwd}")
        except Exception as e:
            print(f"解密失败: {str(e)}")
        
        print(f"\nSchema: {ds.schema_name}")
        print(f"是否启用: {ds.is_enabled}")
        print(f"是否默认: {ds.is_default}")
        
        # 尝试测试连接
        print("\n尝试测试连接...")
        from app.services.data_source_service import connection_manager
        result = connection_manager.test_connection(ds)
        print(f"测试结果: {result}")
        
    else:
        print("未找到ID=1的数据源")
        
finally:
    db.close()
