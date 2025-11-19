#!/usr/bin/env python3
"""
重置数据库序列脚本
用于修复导入数据后序列未更新的问题
"""
import os
from sqlalchemy import create_engine, MetaData, text
from sqlalchemy.orm import sessionmaker


def reset_sequences(database_url):
    """重置所有表的自增序列到正确的值"""
    print(f"连接数据库: {database_url.split('@')[1] if '@' in database_url else database_url}")
    
    # 创建引擎
    engine = create_engine(database_url)
    metadata = MetaData()
    metadata.reflect(bind=engine)
    
    Session = sessionmaker(bind=engine)
    session = Session()
    
    print("\n>>> 开始重置序列...")
    print("="*60)
    
    reset_count = 0
    
    try:
        # 获取所有表
        for table_name, table in metadata.tables.items():
            # 获取主键列
            primary_keys = [col for col in table.primary_key.columns]
            
            # 只处理单一主键且为整数类型的表
            if len(primary_keys) == 1:
                pk_col = primary_keys[0]
                
                # 检查是否是整数类型（通常是自增主键）
                if hasattr(pk_col.type, 'python_type') and pk_col.type.python_type == int:
                    try:
                        # 获取当前最大ID
                        result = session.execute(
                            text(f"SELECT MAX({pk_col.name}) FROM {table_name}")
                        ).scalar()
                        
                        if result is not None:
                            # 重置序列
                            sequence_name = f"{table_name}_{pk_col.name}_seq"
                            
                            # 先检查序列是否存在
                            seq_exists = session.execute(
                                text("""
                                    SELECT EXISTS (
                                        SELECT 1 FROM pg_sequences 
                                        WHERE schemaname = 'public' 
                                        AND sequencename = :seq_name
                                    )
                                """),
                                {"seq_name": sequence_name}
                            ).scalar()
                            
                            if seq_exists:
                                session.execute(
                                    text(f"SELECT setval('{sequence_name}', :max_id, true)"),
                                    {"max_id": result}
                                )
                                print(f"✓ {table_name:40s} 序列重置到 {result}")
                                reset_count += 1
                            else:
                                print(f"⊘ {table_name:40s} 无序列")
                        else:
                            print(f"- {table_name:40s} 无数据")
                            
                    except Exception as e:
                        print(f"✗ {table_name:40s} 失败: {str(e)[:50]}")
        
        session.commit()
        
        print("="*60)
        print(f"\n✓ 序列重置完成！共重置 {reset_count} 个序列")
        
    except Exception as e:
        print(f"\n✗ 错误: {e}")
        session.rollback()
        raise
    finally:
        session.close()


if __name__ == "__main__":
    # 从环境变量读取数据库URL
    database_url = os.getenv("DATABASE_URL")
    
    if not database_url:
        # 尝试从.env文件读取
        env_file = os.path.join(os.path.dirname(__file__), ".env")
        if os.path.exists(env_file):
            with open(env_file) as f:
                for line in f:
                    if line.startswith("DATABASE_URL="):
                        database_url = line.split("=", 1)[1].strip()
                        break
    
    if not database_url:
        print("错误: 未找到DATABASE_URL")
        print("请设置环境变量或在.env文件中配置")
        exit(1)
    
    try:
        reset_sequences(database_url)
        print("\n数据库序列重置成功！")
    except Exception as e:
        print(f"\n错误: {e}")
        exit(1)
