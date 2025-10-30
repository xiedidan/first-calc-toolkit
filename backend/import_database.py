#!/usr/bin/env python3
"""
数据库导入脚本
从JSON文件导入数据到数据库
"""
import json
import os
from sqlalchemy import create_engine, MetaData, inspect
from sqlalchemy.orm import sessionmaker
from datetime import datetime

def import_database(database_url, input_file):
    """导入数据库数据"""
    print(f"连接数据库: {database_url.split('@')[1] if '@' in database_url else database_url}")
    
    # 创建引擎
    engine = create_engine(database_url)
    metadata = MetaData()
    metadata.reflect(bind=engine)
    
    # 读取数据文件
    print(f"读取数据文件: {input_file}")
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    export_time = data.get("export_time", "未知")
    print(f"数据导出时间: {export_time}")
    print(f"包含 {len(data['tables'])} 个表")
    
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # 按表导入数据
        for table_name, table_info in data["tables"].items():
            print(f"\n导入表: {table_name}...", end=" ")
            
            if table_name not in metadata.tables:
                print(f"⚠ 表不存在，跳过")
                continue
            
            table = metadata.tables[table_name]
            table_data = table_info["data"]
            
            if not table_data:
                print("✓ 无数据")
                continue
            
            # 清空表（可选）
            # session.execute(table.delete())
            
            # 批量插入数据
            try:
                session.execute(table.insert(), table_data)
                session.commit()
                print(f"✓ {len(table_data)} 行")
            except Exception as e:
                session.rollback()
                print(f"✗ 失败: {e}")
        
        print("\n✓ 数据导入完成")
        
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
    
    input_file = "database_export.json"
    
    if not os.path.exists(input_file):
        print(f"错误: 数据文件不存在: {input_file}")
        exit(1)
    
    try:
        import_database(database_url, input_file)
        print("\n数据库导入成功！")
    except Exception as e:
        print(f"\n错误: {e}")
        exit(1)
