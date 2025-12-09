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

def create_missing_tables(session, table_name, table_info):
    """根据导出的表结构信息创建缺失的表"""
    try:
        columns_def = []
        for col_name, col_info in table_info.get("columns", {}).items():
            col_type = col_info.get("type", "TEXT")
            nullable = "NULL" if col_info.get("nullable", True) else "NOT NULL"
            columns_def.append(f'"{col_name}" {col_type} {nullable}')
        
        if not columns_def:
            return False
        
        create_sql = f'CREATE TABLE IF NOT EXISTS "{table_name}" ({", ".join(columns_def)})'
        session.execute(text(create_sql))
        session.commit()
        print(f"  ✓ 表 {table_name} 创建成功")
        return True
    except Exception as e:
        print(f"  ✗ 创建表失败: {e}")
        session.rollback()
        return False


def run_migrations(database_url):
    """运行数据库迁移，创建所有表结构"""
    print("\n>>> 检查并创建表结构...")
    try:
        import subprocess
        import sys
        
        # 设置环境变量
        env = os.environ.copy()
        env['DATABASE_URL'] = database_url
        
        # 运行 alembic upgrade head
        result = subprocess.run(
            [sys.executable, '-m', 'alembic', 'upgrade', 'head'],
            cwd=os.path.dirname(__file__),
            env=env,
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("✓ 表结构创建/更新完成")
            return True
        else:
            print(f"⚠ 迁移执行警告: {result.stderr}")
            # 即使有警告也继续，因为表可能已经存在
            return True
            
    except Exception as e:
        print(f"⚠ 无法运行迁移: {e}")
        print("  将尝试直接导入数据...")
        return False


def clean_alembic_version(session):
    """清理 alembic_version 表，避免迁移版本冲突"""
    try:
        print("\n>>> 清理旧的迁移版本记录...")
        result = session.execute(text("DELETE FROM alembic_version"))
        deleted = result.rowcount
        session.commit()
        if deleted > 0:
            print(f"✓ 已清理 {deleted} 条旧的迁移版本记录")
        else:
            print("✓ 无需清理（表为空或不存在）")
        return True
    except Exception as e:
        # 表可能不存在，这是正常的
        session.rollback()
        print(f"✓ alembic_version 表不存在或已清空")
        return True


def import_database(database_url, input_file, skip_existing=True):
    """导入数据库数据
    
    Args:
        database_url: 数据库连接URL
        input_file: 数据文件路径
        skip_existing: 是否跳过已存在的记录（避免主键冲突）
    """
    print(f"连接数据库: {database_url.split('@')[1] if '@' in database_url else database_url}")
    
    # 创建引擎和会话（用于清理）
    engine = create_engine(database_url)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    # 先清理 alembic_version 表，避免版本冲突
    clean_alembic_version(session)
    session.close()
    
    # 运行迁移，确保表结构存在
    run_migrations(database_url)
    
    # 重新创建会话用于数据导入
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
    
    # 创建新的会话用于数据导入
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
            # 跳过 alembic_version 表（迁移版本由 alembic upgrade 管理）
            if table_name == 'alembic_version':
                continue
            if table_name not in data["tables"]:
                continue
                
            print(f"\n导入表: {table_name}...", end=" ")
            
            if table_name not in metadata.tables:
                print(f"表不存在，尝试创建...")
                table_info = data["tables"][table_name]
                if create_missing_tables(session, table_name, table_info):
                    # 重新加载元数据
                    metadata.clear()
                    metadata.reflect(bind=engine)
                    if table_name not in metadata.tables:
                        print(f"  ⚠ 创建后仍无法找到表，跳过")
                        stats["skipped"] += 1
                        continue
                else:
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
        missing_tables = []
        for table_name in data["tables"].keys():
            # 跳过 alembic_version 表
            if table_name == 'alembic_version':
                continue
            if table_name in TABLE_IMPORT_ORDER:
                continue
                
            print(f"\n导入表: {table_name} (未定义顺序)...", end=" ")
            
            if table_name not in metadata.tables:
                print(f"表不存在，尝试创建...")
                table_info = data["tables"][table_name]
                if create_missing_tables(session, table_name, table_info):
                    # 重新加载元数据
                    metadata.clear()
                    metadata.reflect(bind=engine)
                    if table_name not in metadata.tables:
                        print(f"  ⚠ 创建后仍无法找到表")
                        missing_tables.append(table_name)
                        stats["skipped"] += 1
                        continue
                else:
                    missing_tables.append(table_name)
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
        
        # 如果有缺失的表，给出提示
        if missing_tables:
            print("\n⚠ 警告: 以下表不存在，数据未导入:")
            for table in missing_tables:
                print(f"  - {table}")
            print("\n这些表可能是:")
            print("  1. 业务数据表（如 charge_details, TB_MZ_SFMXB 等）")
            print("  2. 临时表或中间表")
            print("\n如果这些表应该存在，请检查:")
            print("  1. 数据库迁移是否完整执行")
            print("  2. 表结构定义是否正确")
            print("  3. 是否需要手动创建这些表")
        
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
