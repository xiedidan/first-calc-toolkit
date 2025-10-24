"""
直接运行数据库迁移
"""
import sys
from alembic.config import Config
from alembic import command

def run_migration():
    """执行数据库迁移"""
    try:
        # 创建 Alembic 配置
        alembic_cfg = Config("alembic.ini")
        
        # 显示当前版本
        print("当前迁移状态:")
        command.current(alembic_cfg)
        print()
        
        # 执行迁移到最新版本
        print("执行迁移到最新版本...")
        command.upgrade(alembic_cfg, "head")
        print()
        
        # 显示迁移后的版本
        print("迁移后状态:")
        command.current(alembic_cfg)
        print()
        
        print("✓ 迁移成功完成！")
        return 0
        
    except Exception as e:
        print(f"✗ 迁移失败: {e}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    sys.exit(run_migration())
