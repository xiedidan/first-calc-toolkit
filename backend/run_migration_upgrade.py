"""运行数据库迁移升级"""
from alembic.config import Config
from alembic import command

# 创建Alembic配置
alembic_cfg = Config("alembic.ini")

# 运行升级到最新版本
command.upgrade(alembic_cfg, "head")

print("数据库迁移完成！")
