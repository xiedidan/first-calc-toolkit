"""add task_id to analysis_reports

Revision ID: 20251210_task_id
Revises: 20251209_ai_prompts
Create Date: 2025-12-10

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20251210_task_id'
down_revision = '20251209_ai_prompt_cat'
branch_labels = None
depends_on = None


def upgrade():
    # 添加 task_id 字段到 analysis_reports 表
    op.add_column(
        'analysis_reports',
        sa.Column('task_id', sa.String(100), nullable=True, comment='关联的计算任务ID')
    )
    
    # 添加索引
    op.create_index(
        'ix_analysis_reports_task_id',
        'analysis_reports',
        ['task_id']
    )
    
    # 添加字段注释
    op.execute("""
        COMMENT ON COLUMN analysis_reports.task_id IS '关联的计算任务ID，用于获取计算结果数据'
    """)


def downgrade():
    op.drop_index('ix_analysis_reports_task_id', table_name='analysis_reports')
    op.drop_column('analysis_reports', 'task_id')
