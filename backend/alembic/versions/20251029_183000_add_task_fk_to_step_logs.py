"""add task foreign key to step logs

Revision ID: 20251029_183000
Revises: 20251029_182429
Create Date: 2025-10-29 18:30:00

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '20251029_183000'
down_revision = '20251029_182429'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 检查外键是否已存在
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    
    # 检查表是否存在
    tables = inspector.get_table_names()
    if 'calculation_step_logs' not in tables:
        # 如果表不存在，跳过
        return
    
    foreign_keys = [fk['name'] for fk in inspector.get_foreign_keys('calculation_step_logs')]
    
    # 添加外键约束（如果不存在）
    if 'fk_calculation_step_logs_task_id' not in foreign_keys:
        op.create_foreign_key(
            'fk_calculation_step_logs_task_id',
            'calculation_step_logs', 'calculation_tasks',
            ['task_id'], ['task_id'],
            ondelete='CASCADE'
        )


def downgrade() -> None:
    # 删除外键约束
    op.drop_constraint('fk_calculation_step_logs_task_id', 'calculation_step_logs', type_='foreignkey')
