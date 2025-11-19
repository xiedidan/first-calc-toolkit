"""手动添加缺失的列"""
import sys
sys.path.insert(0, '.')

from sqlalchemy import create_engine, text, inspect
from app.core.config import settings

engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI))

with engine.connect() as conn:
    inspector = inspect(conn)
    columns = [col['name'] for col in inspector.get_columns('calculation_steps')]
    
    print("当前 calculation_steps 表的列:")
    for col in columns:
        print(f"  - {col}")
    
    # 添加 python_env 列
    if 'python_env' not in columns:
        print("\n添加 python_env 列...")
        conn.execute(text("""
            ALTER TABLE calculation_steps 
            ADD COLUMN python_env VARCHAR(200)
        """))
        conn.commit()
        print("✓ python_env 列添加成功")
    else:
        print("\n✓ python_env 列已存在")
    
    # 检查 data_source_id 列
    if 'data_source_id' not in columns:
        print("\n添加 data_source_id 列...")
        conn.execute(text("""
            ALTER TABLE calculation_steps 
            ADD COLUMN data_source_id INTEGER
        """))
        conn.commit()
        print("✓ data_source_id 列添加成功")
        
        # 添加外键
        print("\n添加外键约束...")
        conn.execute(text("""
            ALTER TABLE calculation_steps 
            ADD CONSTRAINT fk_calculation_steps_data_source_id 
            FOREIGN KEY (data_source_id) REFERENCES data_sources(id) ON DELETE SET NULL
        """))
        conn.commit()
        print("✓ 外键约束添加成功")
        
        # 添加索引
        print("\n添加索引...")
        conn.execute(text("""
            CREATE INDEX ix_calculation_steps_data_source_id 
            ON calculation_steps(data_source_id)
        """))
        conn.commit()
        print("✓ 索引添加成功")
    else:
        print("\n✓ data_source_id 列已存在")
    
    print("\n所有列添加完成！")
