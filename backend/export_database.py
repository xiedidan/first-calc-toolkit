#!/usr/bin/env python3
"""
数据库导出脚本
将数据库数据导出为JSON格式，便于迁移
"""
import json
import os
from sqlalchemy import create_engine, MetaData, inspect
from sqlalchemy.orm import sessionmaker
from datetime import datetime, date
from decimal import Decimal

def json_serializer(obj):
    """JSON序列化辅助函数"""
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    elif isinstance(obj, Decimal):
        return float(obj)
    elif isinstance(obj, bytes):
        return obj.decode('utf-8')
    raise TypeError(f"Type {type(obj)} not serializable")

def export_database(database_url, output_file):
    """导出数据库数据"""
    print(f"连接数据库: {database_url.split('@')[1] if '@' in database_url else database_url}")
    
    # 创建引擎
    engine = create_engine(database_url)
    metadata = MetaData()
    metadata.reflect(bind=engine)
    
    # 获取所有表
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    
    print(f"找到 {len(tables)} 个表")
    
    # 导出数据
    data = {
        "export_time": datetime.now().isoformat(),
        "tables": {}
    }
    
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        for table_name in tables:
            print(f"导出表: {table_name}...", end=" ")
            
            # 获取表对象
            table = metadata.tables[table_name]
            
            # 查询所有数据
            result = session.execute(table.select())
            rows = result.fetchall()
            
            # 转换为字典列表
            table_data = []
            for row in rows:
                row_dict = {}
                for column, value in zip(result.keys(), row):
                    row_dict[column] = value
                table_data.append(row_dict)
            
            data["tables"][table_name] = {
                "row_count": len(table_data),
                "data": table_data
            }
            
            print(f"✓ {len(table_data)} 行")
        
        # 保存到文件
        print(f"\n保存到文件: {output_file}")
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2, default=json_serializer)
        
        # 显示文件大小
        file_size = os.path.getsize(output_file) / (1024 * 1024)
        print(f"✓ 导出完成，文件大小: {file_size:.2f} MB")
        
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
        print("请设置环境变量或在backend/.env文件中配置")
        exit(1)
    
    output_file = "database_export.json"
    
    try:
        export_database(database_url, output_file)
        print("\n数据库导出成功！")
    except Exception as e:
        print(f"\n错误: {e}")
        exit(1)
