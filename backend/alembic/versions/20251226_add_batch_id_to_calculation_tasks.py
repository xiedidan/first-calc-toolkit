"""add batch_id to calculation_tasks

Revision ID: 20251226_batch_id
Revises: 20251222_migrate_ai_configs_to_interfaces
Create Date: 2025-12-26

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20251226_batch_id'
down_revision = '20251222_ai_migrate'
branch_labels = None
depends_on = None


def upgrade():
    # 添加 batch_id 字段到 calculation_tasks 表
    op.add_column('calculation_tasks', sa.Column('batch_id', sa.String(100), nullable=True, comment='批次ID，同一次创建的多个任务共享同一批次ID'))
    
    # 创建索引以加速按批次查询
    op.create_index('ix_calculation_tasks_batch_id', 'calculation_tasks', ['batch_id'])


def downgrade():
    op.drop_index('ix_calculation_tasks_batch_id', table_name='calculation_tasks')
    op.drop_column('calculation_tasks', 'batch_id')
