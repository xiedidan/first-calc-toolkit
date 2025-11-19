"""
验证医疗机构管理数据迁移
"""
import sys
from sqlalchemy import create_engine, inspect, text
from app.config import settings

def verify_migration():
    """验证数据迁移完整性"""
    engine = create_engine(settings.DATABASE_URL)
    inspector = inspect(engine)
    
    print("=" * 60)
    print("医疗机构管理数据迁移验证")
    print("=" * 60)
    
    errors = []
    warnings = []
    
    # 1. 检查 hospitals 表是否存在
    print("\n1. 检查 hospitals 表...")
    if 'hospitals' not in inspector.get_table_names():
        errors.append("❌ hospitals 表不存在")
    else:
        print("✓ hospitals 表存在")
        
        # 检查字段
        columns = {col['name']: col for col in inspector.get_columns('hospitals')}
        required_columns = ['id', 'code', 'name', 'is_active', 'created_at', 'updated_at']
        for col_name in required_columns:
            if col_name not in columns:
                errors.append(f"❌ hospitals 表缺少字段: {col_name}")
            else:
                print(f"  ✓ 字段 {col_name} 存在")
        
        # 检查唯一约束
        constraints = inspector.get_unique_constraints('hospitals')
        code_unique = any('code' in c['column_names'] for c in constraints)
        if not code_unique:
            errors.append("❌ hospitals 表的 code 字段缺少唯一约束")
        else:
            print("  ✓ code 字段有唯一约束")
        
        # 检查默认医疗机构
        with engine.connect() as conn:
            result = conn.execute(text("SELECT * FROM hospitals WHERE code = 'nbeye'"))
            hospital = result.fetchone()
            if not hospital:
                errors.append("❌ 默认医疗机构'宁波市眼科医院'不存在")
            else:
                print(f"  ✓ 默认医疗机构存在: {hospital.name}")
    
    # 2. 检查 users 表的 hospital_id 字段
    print("\n2. 检查 users 表...")
    if 'users' not in inspector.get_table_names():
        errors.append("❌ users 表不存在")
    else:
        columns = {col['name']: col for col in inspector.get_columns('users')}
        if 'hospital_id' not in columns:
            errors.append("❌ users 表缺少 hospital_id 字段")
        else:
            print("  ✓ hospital_id 字段存在")
            if columns['hospital_id']['nullable']:
                print("  ✓ hospital_id 字段可为空（支持超级用户）")
            else:
                warnings.append("⚠ hospital_id 字段不可为空")
        
        # 检查外键
        fks = inspector.get_foreign_keys('users')
        hospital_fk = any('hospital_id' in fk['constrained_columns'] for fk in fks)
        if not hospital_fk:
            errors.append("❌ users 表的 hospital_id 缺少外键约束")
        else:
            print("  ✓ hospital_id 有外键约束")
    
    # 3. 检查 departments 表的 hospital_id 字段
    print("\n3. 检查 departments 表...")
    if 'departments' not in inspector.get_table_names():
        errors.append("❌ departments 表不存在")
    else:
        columns = {col['name']: col for col in inspector.get_columns('departments')}
        if 'hospital_id' not in columns:
            errors.append("❌ departments 表缺少 hospital_id 字段")
        else:
            print("  ✓ hospital_id 字段存在")
            if not columns['hospital_id']['nullable']:
                print("  ✓ hospital_id 字段不可为空")
            else:
                errors.append("❌ hospital_id 字段应该不可为空")
        
        # 检查外键
        fks = inspector.get_foreign_keys('departments')
        hospital_fk = any('hospital_id' in fk['constrained_columns'] for fk in fks)
        if not hospital_fk:
            errors.append("❌ departments 表的 hospital_id 缺少外键约束")
        else:
            print("  ✓ hospital_id 有外键约束")
        
        # 检查数据迁移
        with engine.connect() as conn:
            result = conn.execute(text("SELECT COUNT(*) as count FROM departments WHERE hospital_id IS NULL"))
            null_count = result.fetchone().count
            if null_count > 0:
                errors.append(f"❌ 有 {null_count} 条 departments 记录的 hospital_id 为空")
            else:
                result = conn.execute(text("SELECT COUNT(*) as count FROM departments"))
                total_count = result.fetchone().count
                if total_count > 0:
                    print(f"  ✓ 所有 {total_count} 条 departments 记录都已关联到医疗机构")
    
    # 4. 检查 model_versions 表的 hospital_id 字段
    print("\n4. 检查 model_versions 表...")
    if 'model_versions' not in inspector.get_table_names():
        errors.append("❌ model_versions 表不存在")
    else:
        columns = {col['name']: col for col in inspector.get_columns('model_versions')}
        if 'hospital_id' not in columns:
            errors.append("❌ model_versions 表缺少 hospital_id 字段")
        else:
            print("  ✓ hospital_id 字段存在")
            if not columns['hospital_id']['nullable']:
                print("  ✓ hospital_id 字段不可为空")
            else:
                errors.append("❌ hospital_id 字段应该不可为空")
        
        # 检查外键
        fks = inspector.get_foreign_keys('model_versions')
        hospital_fk = any('hospital_id' in fk['constrained_columns'] for fk in fks)
        if not hospital_fk:
            errors.append("❌ model_versions 表的 hospital_id 缺少外键约束")
        else:
            print("  ✓ hospital_id 有外键约束")
        
        # 检查数据迁移
        with engine.connect() as conn:
            result = conn.execute(text("SELECT COUNT(*) as count FROM model_versions WHERE hospital_id IS NULL"))
            null_count = result.fetchone().count
            if null_count > 0:
                errors.append(f"❌ 有 {null_count} 条 model_versions 记录的 hospital_id 为空")
            else:
                result = conn.execute(text("SELECT COUNT(*) as count FROM model_versions"))
                total_count = result.fetchone().count
                if total_count > 0:
                    print(f"  ✓ 所有 {total_count} 条 model_versions 记录都已关联到医疗机构")
    
    # 5. 检查索引
    print("\n5. 检查索引...")
    tables_to_check = ['users', 'departments', 'model_versions']
    for table in tables_to_check:
        if table in inspector.get_table_names():
            indexes = inspector.get_indexes(table)
            hospital_index = any('hospital_id' in idx['column_names'] for idx in indexes)
            if hospital_index:
                print(f"  ✓ {table} 表的 hospital_id 有索引")
            else:
                warnings.append(f"⚠ {table} 表的 hospital_id 缺少索引")
    
    # 输出结果
    print("\n" + "=" * 60)
    print("验证结果")
    print("=" * 60)
    
    if errors:
        print(f"\n❌ 发现 {len(errors)} 个错误:")
        for error in errors:
            print(f"  {error}")
    
    if warnings:
        print(f"\n⚠ 发现 {len(warnings)} 个警告:")
        for warning in warnings:
            print(f"  {warning}")
    
    if not errors and not warnings:
        print("\n✓ 所有检查通过！数据迁移成功。")
        return 0
    elif not errors:
        print("\n✓ 数据迁移基本成功，但有一些警告需要注意。")
        return 0
    else:
        print("\n❌ 数据迁移验证失败，请检查错误并修复。")
        return 1


if __name__ == "__main__":
    sys.exit(verify_migration())
