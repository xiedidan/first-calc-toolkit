"""add revenue tables

Revision ID: 20251128_revenue
Revises: 
Create Date: 2025-11-28 22:30:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20251128_revenue'
down_revision = None  # 需要根据实际情况设置
branch_labels = None
depends_on = None


def upgrade():
    # 创建科室收入表
    op.create_table(
        'department_revenues',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('hospital_id', sa.Integer(), nullable=False),
        sa.Column('year_month', sa.String(7), nullable=False, comment='年月，格式：YYYY-MM'),
        sa.Column('department_code', sa.String(50), nullable=False, comment='科室代码'),
        sa.Column('department_name', sa.String(100), nullable=False, comment='科室名称'),
        sa.Column('revenue', sa.Numeric(20, 2), nullable=False, comment='收入金额'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id'),
        comment='科室收入表'
    )
    
    # 创建唯一索引
    op.create_index(
        'uq_dept_revenue_hospital_month_dept',
        'department_revenues',
        ['hospital_id', 'year_month', 'department_code'],
        unique=True
    )
    
    # 创建科室收入基准表
    op.create_table(
        'revenue_benchmarks',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('hospital_id', sa.Integer(), nullable=False),
        sa.Column('department_code', sa.String(50), nullable=False, comment='科室代码'),
        sa.Column('department_name', sa.String(100), nullable=False, comment='科室名称'),
        sa.Column('version_id', sa.Integer(), nullable=False, comment='模型版本ID'),
        sa.Column('version_name', sa.String(200), nullable=False, comment='模型版本名称'),
        sa.Column('benchmark_revenue', sa.Numeric(20, 2), nullable=False, comment='基准收入'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['version_id'], ['model_versions.id'], ondelete='CASCADE'),
        comment='科室收入基准表'
    )
    
    # 创建唯一索引
    op.create_index(
        'uq_revenue_benchmark_hospital_dept_version',
        'revenue_benchmarks',
        ['hospital_id', 'department_code', 'version_id'],
        unique=True
    )


def downgrade():
    op.drop_index('uq_revenue_benchmark_hospital_dept_version', table_name='revenue_benchmarks')
    op.drop_table('revenue_benchmarks')
    op.drop_index('uq_dept_revenue_hospital_month_dept', table_name='department_revenues')
    op.drop_table('department_revenues')
