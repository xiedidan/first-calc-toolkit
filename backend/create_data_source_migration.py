"""
创建数据源迁移脚本
"""
import os
import sys

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from alembic.config import Config
from alembic import command

def create_migration():
    """创建迁移"""
    try:
        # 创建Alembic配置
        alembic_cfg = Config("alembic.ini")
        
        # 生成迁移脚本
        print("正在生成数据源迁移脚本...")
        command.revision(
            alembic_cfg,
            message="add data sources table and update calculation steps",
            autogenerate=True
        )
        
        print("迁移脚本生成成功！")
        
    except Exception as e:
        print(f"错误: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    create_migration()
