"""add calculation task tables

Revision ID: 20251029_182429
Revises: add_datasource_steps
Create Date: 2025-10-29 18:24:29

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '20251029_182429'
down_revision = 'add_datasource_steps'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 创建计算任务表
    op.create_table(
        'calculation_tasks',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('task_id', sa.String(length=100), nullable=False, comment='任务ID'),
        sa.Column('model_version_id', sa.Integer(), nullable=False, comment='模型版本ID'),
        sa.Column('workflow_id', sa.Integer(), nullable=True, comment='计算流程ID'),
        sa.Column('period', sa.String(length=20), nullable=False, comment='计算周期(YYYY-MM)'),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='pending', comment='任务状态'),
        sa.Column('progress', sa.DECIMAL(precision=5, scale=2), server_default='0', comment='进度百分比'),
        sa.Column('description', sa.Text(), nullable=True, comment='任务描述'),
        sa.Column('error_message', sa.Text(), nullable=True, comment='错误信息'),
        sa.Column('created_at', sa.DateTime(), nullable=True, comment='创建时间'),
        sa.Column('started_at', sa.DateTime(), nullable=True, comment='开始时间'),
        sa.Column('completed_at', sa.DateTime(), nullable=True, comment='完成时间'),
        sa.Column('created_by', sa.Integer(), nullable=True, comment='创建人ID'),
        sa.ForeignKeyConstraint(['model_version_id'], ['model_versions.id'], ),
        sa.ForeignKeyConstraint(['workflow_id'], ['calculation_workflows.id'], ),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_calculation_tasks_id'), 'calculation_tasks', ['id'], unique=False)
    op.create_index(op.f('ix_calculation_tasks_task_id'), 'calculation_tasks', ['task_id'], unique=True)

    # 创建计算结果明细表
    op.create_table(
        'calculation_results',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('task_id', sa.String(length=100), nullable=False, comment='任务ID'),
        sa.Column('department_id', sa.Integer(), nullable=False, comment='科室ID'),
        sa.Column('node_id', sa.Integer(), nullable=False, comment='节点ID'),
        sa.Column('node_name', sa.String(length=255), nullable=False, comment='节点名称'),
        sa.Column('node_code', sa.String(length=100), nullable=True, comment='节点编码'),
        sa.Column('node_type', sa.String(length=50), nullable=True, comment='节点类型'),
        sa.Column('parent_id', sa.Integer(), nullable=True, comment='父节点ID'),
        sa.Column('workload', sa.DECIMAL(precision=20, scale=4), nullable=True, comment='工作量'),
        sa.Column('weight', sa.DECIMAL(precision=10, scale=4), nullable=True, comment='权重/单价'),
        sa.Column('value', sa.DECIMAL(precision=20, scale=4), nullable=True, comment='价值'),
        sa.Column('ratio', sa.DECIMAL(precision=10, scale=4), nullable=True, comment='占比'),
        sa.Column('created_at', sa.DateTime(), nullable=True, comment='创建时间'),
        sa.ForeignKeyConstraint(['task_id'], ['calculation_tasks.task_id'], ),
        sa.ForeignKeyConstraint(['department_id'], ['departments.id'], ),
        sa.ForeignKeyConstraint(['node_id'], ['model_nodes.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_calculation_results_id'), 'calculation_results', ['id'], unique=False)

    # 创建计算结果汇总表
    op.create_table(
        'calculation_summaries',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('task_id', sa.String(length=100), nullable=False, comment='任务ID'),
        sa.Column('department_id', sa.Integer(), nullable=False, comment='科室ID'),
        sa.Column('doctor_value', sa.DECIMAL(precision=20, scale=4), server_default='0', comment='医生价值'),
        sa.Column('doctor_ratio', sa.DECIMAL(precision=10, scale=4), server_default='0', comment='医生占比'),
        sa.Column('nurse_value', sa.DECIMAL(precision=20, scale=4), server_default='0', comment='护理价值'),
        sa.Column('nurse_ratio', sa.DECIMAL(precision=10, scale=4), server_default='0', comment='护理占比'),
        sa.Column('tech_value', sa.DECIMAL(precision=20, scale=4), server_default='0', comment='医技价值'),
        sa.Column('tech_ratio', sa.DECIMAL(precision=10, scale=4), server_default='0', comment='医技占比'),
        sa.Column('total_value', sa.DECIMAL(precision=20, scale=4), server_default='0', comment='科室总价值'),
        sa.Column('created_at', sa.DateTime(), nullable=True, comment='创建时间'),
        sa.ForeignKeyConstraint(['task_id'], ['calculation_tasks.task_id'], ),
        sa.ForeignKeyConstraint(['department_id'], ['departments.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_calculation_summaries_id'), 'calculation_summaries', ['id'], unique=False)


def downgrade() -> None:
    # 删除表
    op.drop_index(op.f('ix_calculation_summaries_id'), table_name='calculation_summaries')
    op.drop_table('calculation_summaries')
    
    op.drop_index(op.f('ix_calculation_results_id'), table_name='calculation_results')
    op.drop_table('calculation_results')
    
    op.drop_index(op.f('ix_calculation_tasks_task_id'), table_name='calculation_tasks')
    op.drop_index(op.f('ix_calculation_tasks_id'), table_name='calculation_tasks')
    op.drop_table('calculation_tasks')
