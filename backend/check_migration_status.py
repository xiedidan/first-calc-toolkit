"""
检查数据库迁移状态
"""
import sys
from alembic.config import Config
from alembic import command

def check_migration_status():
    """检查迁移状态"""
    try:
        # 创建Alembic配置
        alembic_cfg = Config("alembic.ini")
        
        # 显示当前版本
        print("=== 当前数据库版本 ===")
        command.current(alembic_cfg, verbose=True)
        
        # 显示迁移历史
        print("\n=== 迁移历史 ===")
        command.history(alembic_cfg, verbose=True)
        
        # 显示待执行的迁移
        print("\n=== 待执行的迁移 ===")
        command.show(alembic_cfg, "head")
        
    except Exception as e:
        print(f"错误: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    check_migration_status()
