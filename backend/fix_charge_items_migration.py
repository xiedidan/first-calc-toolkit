"""
修复收费项目迁移 - 清理失败的迁移状态
"""
import sys
from sqlalchemy import create_engine, text
from app.config import settings

def fix_migration():
    """修复迁移状态"""
    engine = create_engine(settings.DATABASE_URL)
    
    print("=" * 60)
    print("修复收费项目迁移状态")
    print("=" * 60)
    
    with engine.connect() as conn:
        # 开始新事务
        trans = conn.begin()
        
        try:
            print("\n1. 检查 charge_items 表结构...")
            
            # 检查 hospital_id 列是否存在
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'charge_items' 
                AND column_name = 'hospital_id'
            """))
            
            has_hospital_id = result.fetchone() is not None
            print(f"   - hospital_id 列存在: {has_hospital_id}")
            
            if has_hospital_id:
                print("\n2. 删除 hospital_id 列（如果存在）...")
                
                # 先删除可能存在的约束和索引
                print("   - 删除外键约束...")
                try:
                    conn.execute(text("""
                        ALTER TABLE charge_items 
                        DROP CONSTRAINT IF EXISTS fk_charge_items_hospital_id
                    """))
                except Exception as e:
                    print(f"     警告: {e}")
                
                print("   - 删除索引...")
                try:
                    conn.execute(text("""
                        DROP INDEX IF EXISTS ix_charge_items_hospital_id
                    """))
                except Exception as e:
                    print(f"     警告: {e}")
                
                print("   - 删除复合唯一约束...")
                try:
                    conn.execute(text("""
                        ALTER TABLE charge_items 
                        DROP CONSTRAINT IF EXISTS uq_hospital_item_code
                    """))
                except Exception as e:
                    print(f"     警告: {e}")
                
                print("   - 删除 hospital_id 列...")
                conn.execute(text("""
                    ALTER TABLE charge_items 
                    DROP COLUMN IF EXISTS hospital_id
                """))
                
                print("   ✓ hospital_id 列已删除")
            
            print("\n3. 检查 alembic_version 表...")
            result = conn.execute(text("""
                SELECT version_num 
                FROM alembic_version
            """))
            
            current_version = result.fetchone()
            if current_version:
                print(f"   - 当前版本: {current_version[0]}")
                
                if current_version[0] == '20251104_charge_items_hospital':
                    print("   - 回滚到上一个版本...")
                    conn.execute(text("""
                        UPDATE alembic_version 
                        SET version_num = '20251103_hospital'
                    """))
                    print("   ✓ 版本已回滚")
            
            trans.commit()
            
            print("\n" + "=" * 60)
            print("✓ 修复完成！现在可以重新运行迁移:")
            print("  alembic upgrade head")
            print("=" * 60)
            
        except Exception as e:
            trans.rollback()
            print(f"\n❌ 修复失败: {str(e)}")
            import traceback
            traceback.print_exc()
            sys.exit(1)

if __name__ == "__main__":
    fix_migration()
