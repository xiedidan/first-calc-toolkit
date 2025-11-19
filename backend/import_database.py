#!/usr/bin/env python3
"""
数据库导入脚本
从JSON文件导入数据到数据库
"""
import json
import os
from sqlalchemy import create_engine, MetaData, inspect, text
from sqlalchemy.orm import sessionmaker
from datetime import datetime

# 定义表的导入顺序（按照外键依赖关系）
TABLE_IMPORT_ORDER = [
    # 1. 基础表（无外键依赖）
    "alembic_version",
    "permissions",
    "roles",                    # 角色表（必须在users之前）
    "hospitals",                # 医疗机构表（必须在users之前）
    "data_sources",
    "system_settings",
    
    # 2. 依赖基础表的表
    "users",                    # 用户表（依赖roles和hospitals）
    "role_permissions",         # 角色权限关联表（依赖roles和permissions）
    "departments",              # 科室表（依赖hospitals）
    "model_versions",           # 模型版本表（依赖hospitals）
    "data_templates",           # 数据模板表（依赖hospitals）
    
    # 3. 依赖用户和角色的表
    "user_roles",               # 用户角色关联表（依赖users和roles）
    
    # 4. 依赖医院和科室的表
    "charge_items",             # 收费项目表（依赖hospitals和departments）
    
    # 5. 依赖模型版本的表
    "model_nodes",              # 模型节点表（依赖model_versions）
    "calculation_workflows",    # 计算工作流表（依赖model_versions）
    "model_version_imports",    # 模型版本导入记录表（依赖model_versions）
    
    # 6. 依赖工作流的表
    "calculation_steps",        # 计算步骤表（依赖calculation_workflows）
    
    # 7. 依赖计算步骤的表
    "calculation_tasks",        # 计算任务表（依赖calculation_steps和model_versions）
    "dimension_item_mappings",  # 维度项映射表（依赖charge_items）
    
    # 8. 依赖任务的表
    "calculation_step_logs",    # 计算步骤日志表（依赖calculation_tasks）
    "calculation_results",      # 计算结果表（依赖calculation_tasks）
    "calculation_summaries",    # 计算汇总表（依赖calculation_tasks）
]

def import_database(database_url, input_file, skip_existing=True):
    """导入数据库数据
    
    Args:
        database_url: 数据库连接URL
        input_file: 数据文件路径
        skip_existing: 是否跳过已存在的记录（避免主键冲突）
    """
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
    print(f"导入模式: {'跳过已存在记录' if skip_existing else '覆盖已存在记录'}")
    
    Session = sessionmaker(bind=engine)
    session = Session()
    
    # 统计信息
    stats = {
        "success": 0,
        "skipped": 0,
        "failed": 0,
        "total_rows": 0
    }
    
    try:
        # 按照定义的顺序导入表
        for table_name in TABLE_IMPORT_ORDER:
            if table_name not in data["tables"]:
                continue
                
            print(f"\n导入表: {table_name}...", end=" ")
            
            if table_name not in metadata.tables:
                print(f"⚠ 表不存在，跳过")
                stats["skipped"] += 1
                continue
            
            table = metadata.tables[table_name]
            table_info = data["tables"][table_name]
            table_data = table_info["data"]
            
            if not table_data:
                print("✓ 无数据")
                stats["skipped"] += 1
                continue
            
            # 获取主键列
            primary_keys = [col.name for col in table.primary_key.columns]
            
            # 导入数据
            try:
                if skip_existing and primary_keys:
                    # 逐行检查并插入（跳过已存在的记录）
                    inserted = 0
                    skipped = 0
                    
                    for row in table_data:
                        # 检查记录是否已存在
                        pk_conditions = [table.c[pk] == row[pk] for pk in primary_keys if pk in row]
                        
                        if pk_conditions:
                            exists = session.query(table).filter(*pk_conditions).first()
                            if exists:
                                skipped += 1
                                continue
                        
                        # 插入新记录
                        try:
                            session.execute(table.insert(), [row])
                            inserted += 1
                        except Exception as e:
                            # 单条记录失败，继续处理其他记录
                            session.rollback()
                            skipped += 1
                            continue
                    
                    session.commit()
                    
                    if inserted > 0:
                        print(f"✓ 插入 {inserted} 行", end="")
                        stats["success"] += 1
                        stats["total_rows"] += inserted
                    if skipped > 0:
                        print(f" (跳过 {skipped} 行)", end="")
                    print()
                else:
                    # 批量插入（可能会失败）
                    session.execute(table.insert(), table_data)
                    session.commit()
                    print(f"✓ {len(table_data)} 行")
                    stats["success"] += 1
                    stats["total_rows"] += len(table_data)
                    
            except Exception as e:
                session.rollback()
                print(f"✗ 失败: {str(e)[:200]}")
                stats["failed"] += 1
        
        # 处理不在顺序列表中的其他表
        for table_name in data["tables"].keys():
            if table_name in TABLE_IMPORT_ORDER:
                continue
                
            print(f"\n导入表: {table_name} (未定义顺序)...", end=" ")
            
            if table_name not in metadata.tables:
                print(f"⚠ 表不存在，跳过")
                stats["skipped"] += 1
                continue
            
            table = metadata.tables[table_name]
            table_info = data["tables"][table_name]
            table_data = table_info["data"]
            
            if not table_data:
                print("✓ 无数据")
                stats["skipped"] += 1
                continue
            
            try:
                session.execute(table.insert(), table_data)
                session.commit()
                print(f"✓ {len(table_data)} 行")
                stats["success"] += 1
                stats["total_rows"] += len(table_data)
            except Exception as e:
                session.rollback()
                print(f"✗ 失败: {str(e)[:200]}")
                stats["failed"] += 1
        
        print("\n" + "="*50)
        print("数据导入完成")
        print("="*50)
        print(f"成功: {stats['success']} 个表")
        print(f"失败: {stats['failed']} 个表")
        print(f"跳过: {stats['skipped']} 个表")
        print(f"总计导入: {stats['total_rows']} 行数据")
        print("="*50)
        
        # 重置所有表的序列
        print("\n>>> 重置数据库序列...")
        reset_sequences(session, metadata)
        
    finally:
        session.close()


def reset_sequences(session, metadata):
    """重置所有表的自增序列到正确的值"""
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
                            session.execute(
                                text(f"SELECT setval('{sequence_name}', :max_id, true)"),
                                {"max_id": result}
                            )
                            print(f"  ✓ {table_name}: 序列重置到 {result}")
                    except Exception as e:
                        # 某些表可能没有序列，跳过
                        pass
        
        session.commit()
        print("✓ 序列重置完成")
        
    except Exception as e:
        print(f"⚠ 序列重置失败: {e}")
        session.rollback()

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
