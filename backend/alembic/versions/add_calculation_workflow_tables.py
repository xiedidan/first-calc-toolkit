"""add calculation workflow tables

Revision ID: calc_workflow_001
Revises: change_dim_to_code
Create Date: 2025-10-27 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'calc_workflow_001'
down_revision = 'change_dim_to_code'
branch_labels = None
depends_on = None


def upgrade():
    # 创建计算流程表
    op.create_table(
        'calculation_workflows',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('version_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['version_id'], ['model_versions.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_calculation_workflows_version_id', 'calculation_workflows', ['version_id'])
    op.create_index('ix_calculation_workflows_is_active', 'calculation_workflows', ['is_active'])

    # 创建计算步骤表
    op.create_table(
        'calculation_steps',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('workflow_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('code_type', sa.String(length=20), nullable=False),
        sa.Column('code_content', sa.Text(), nullable=False),
        sa.Column('sort_order', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('is_enabled', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.CheckConstraint("code_type IN ('python', 'sql')", name='check_code_type'),
        sa.ForeignKeyConstraint(['workflow_id'], ['calculation_workflows.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_calculation_steps_workflow_id', 'calculation_steps', ['workflow_id'])
    op.create_index('ix_calculation_steps_sort_order', 'calculation_steps', ['sort_order'])

    # 创建计算步骤执行日志表
    op.create_table(
        'calculation_step_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('task_id', sa.String(length=100), nullable=False),
        sa.Column('step_id', sa.Integer(), nullable=False),
        sa.Column('department_id', sa.Integer(), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('start_time', sa.DateTime(), nullable=False),
        sa.Column('end_time', sa.DateTime(), nullable=True),
        sa.Column('duration_ms', sa.Integer(), nullable=True),
        sa.Column('result_data', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.CheckConstraint("status IN ('success', 'failed')", name='check_status'),
        sa.ForeignKeyConstraint(['step_id'], ['calculation_steps.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_calculation_step_logs_task_id', 'calculation_step_logs', ['task_id'])
    op.create_index('ix_calculation_step_logs_step_id', 'calculation_step_logs', ['step_id'])


def downgrade():
    # 删除表（按照依赖关系的逆序）
    op.drop_index('ix_calculation_step_logs_step_id', table_name='calculation_step_logs')
    op.drop_index('ix_calculation_step_logs_task_id', table_name='calculation_step_logs')
    op.drop_table('calculation_step_logs')
    
    op.drop_index('ix_calculation_steps_sort_order', table_name='calculation_steps')
    op.drop_index('ix_calculation_steps_workflow_id', table_name='calculation_steps')
    op.drop_table('calculation_steps')
    
    op.drop_index('ix_calculation_workflows_is_active', table_name='calculation_workflows')
    op.drop_index('ix_calculation_workflows_version_id', table_name='calculation_workflows')
    op.drop_table('calculation_workflows')
