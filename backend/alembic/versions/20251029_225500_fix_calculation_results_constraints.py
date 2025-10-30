"""fix calculation results constraints

Revision ID: 20251029_225500
Revises: 3900f968ffe3
Create Date: 2025-10-29 22:55:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20251029_225500'
down_revision = '3900f968ffe3'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. 移除 calculation_results 表的外键约束
    # 注意：外键约束名称可能因数据库而异，这里使用常见的命名模式
    op.drop_constraint('calculation_results_department_id_fkey', 'calculation_results', type_='foreignkey')
    op.drop_constraint('calculation_results_node_id_fkey', 'calculation_results', type_='foreignkey')
    op.drop_constraint('calculation_results_task_id_fkey', 'calculation_results', type_='foreignkey')
    
    # 2. 移除 calculation_summaries 表的外键约束
    op.drop_constraint('calculation_summaries_department_id_fkey', 'calculation_summaries', type_='foreignkey')
    op.drop_constraint('calculation_summaries_task_id_fkey', 'calculation_summaries', type_='foreignkey')
    
    # 3. 为 calculation_summaries 添加唯一约束以支持 ON CONFLICT
    op.create_unique_constraint(
        'uq_calculation_summaries_task_dept',
        'calculation_summaries',
        ['task_id', 'department_id']
    )
    
    # 4. 添加索引以提高查询性能
    op.create_index('ix_calculation_results_task_id', 'calculation_results', ['task_id'])
    op.create_index('ix_calculation_results_department_id', 'calculation_results', ['department_id'])
    op.create_index('ix_calculation_summaries_task_id', 'calculation_summaries', ['task_id'])
    op.create_index('ix_calculation_summaries_department_id', 'calculation_summaries', ['department_id'])


def downgrade() -> None:
    # 1. 移除索引
    op.drop_index('ix_calculation_summaries_department_id', 'calculation_summaries')
    op.drop_index('ix_calculation_summaries_task_id', 'calculation_summaries')
    op.drop_index('ix_calculation_results_department_id', 'calculation_results')
    op.drop_index('ix_calculation_results_task_id', 'calculation_results')
    
    # 2. 移除唯一约束
    op.drop_constraint('uq_calculation_summaries_task_dept', 'calculation_summaries', type_='unique')
    
    # 3. 恢复 calculation_summaries 的外键约束
    op.create_foreign_key(
        'calculation_summaries_task_id_fkey',
        'calculation_summaries', 'calculation_tasks',
        ['task_id'], ['task_id']
    )
    op.create_foreign_key(
        'calculation_summaries_department_id_fkey',
        'calculation_summaries', 'departments',
        ['department_id'], ['id']
    )
    
    # 4. 恢复 calculation_results 的外键约束
    op.create_foreign_key(
        'calculation_results_task_id_fkey',
        'calculation_results', 'calculation_tasks',
        ['task_id'], ['task_id']
    )
    op.create_foreign_key(
        'calculation_results_node_id_fkey',
        'calculation_results', 'model_nodes',
        ['node_id'], ['id']
    )
    op.create_foreign_key(
        'calculation_results_department_id_fkey',
        'calculation_results', 'departments',
        ['department_id'], ['id']
    )
