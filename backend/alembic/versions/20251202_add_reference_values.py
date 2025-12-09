"""add reference values table

Revision ID: 20251202_refval
Revises: 
Create Date: 2025-12-02 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20251202_refval'
down_revision = None  # 独立迁移
branch_labels = None
depends_on = None


def upgrade():
    # 创建参考价值表
    op.create_table(
        'reference_values',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('hospital_id', sa.Integer(), nullable=False, comment='医疗机构ID'),
        sa.Column('period', sa.String(7), nullable=False, comment='年月，格式：YYYY-MM'),
        sa.Column('department_code', sa.String(50), nullable=False, comment='科室代码'),
        sa.Column('department_name', sa.String(100), nullable=False, comment='科室名称'),
        sa.Column('reference_value', sa.Numeric(18, 4), nullable=False, comment='参考总价值'),
        sa.Column('doctor_reference_value', sa.Numeric(18, 4), nullable=True, comment='医生参考价值'),
        sa.Column('nurse_reference_value', sa.Numeric(18, 4), nullable=True, comment='护理参考价值'),
        sa.Column('tech_reference_value', sa.Numeric(18, 4), nullable=True, comment='医技参考价值'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['hospital_id'], ['hospitals.id'], ondelete='CASCADE'),
        comment='参考价值表'
    )
    
    # 创建索引
    op.create_index('ix_reference_values_hospital_id', 'reference_values', ['hospital_id'])
    op.create_index('ix_reference_values_period', 'reference_values', ['period'])
    op.create_index('ix_reference_values_department_code', 'reference_values', ['department_code'])
    
    # 创建唯一约束
    op.create_index(
        'uq_reference_value_hospital_period_dept',
        'reference_values',
        ['hospital_id', 'period', 'department_code'],
        unique=True
    )


def downgrade():
    op.drop_index('uq_reference_value_hospital_period_dept', table_name='reference_values')
    op.drop_index('ix_reference_values_department_code', table_name='reference_values')
    op.drop_index('ix_reference_values_period', table_name='reference_values')
    op.drop_index('ix_reference_values_hospital_id', table_name='reference_values')
    op.drop_table('reference_values')
