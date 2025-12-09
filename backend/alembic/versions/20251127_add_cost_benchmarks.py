"""add cost benchmarks table

Revision ID: 20251127_add_cost_benchmarks
Revises: 20251127_add_orientation_values
Create Date: 2025-11-27

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '20251127_add_cost_benchmarks'
down_revision = '20251127_add_orientation_values'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 创建成本基准表
    op.create_table(
        'cost_benchmarks',
        sa.Column('id', sa.Integer(), nullable=False, comment='主键'),
        sa.Column('hospital_id', sa.Integer(), nullable=False, comment='所属医疗机构ID'),
        sa.Column('department_code', sa.String(length=50), nullable=False, comment='科室代码'),
        sa.Column('department_name', sa.String(length=100), nullable=False, comment='科室名称'),
        sa.Column('version_id', sa.Integer(), nullable=False, comment='模型版本ID'),
        sa.Column('version_name', sa.String(length=100), nullable=False, comment='模型版本名称'),
        sa.Column('dimension_code', sa.String(length=100), nullable=False, comment='维度代码'),
        sa.Column('dimension_name', sa.String(length=200), nullable=False, comment='维度名称'),
        sa.Column('benchmark_value', sa.Numeric(precision=15, scale=2), nullable=False, comment='基准值'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()'), comment='创建时间'),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()'), comment='更新时间'),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(
            ['hospital_id'], ['hospitals.id'],
            name='fk_cost_benchmarks_hospital_id',
            ondelete='CASCADE'
        ),
        sa.ForeignKeyConstraint(
            ['version_id'], ['model_versions.id'],
            name='fk_cost_benchmarks_version_id',
            ondelete='CASCADE'
        ),
        sa.UniqueConstraint(
            'hospital_id', 'department_code', 'version_id', 'dimension_code',
            name='uq_cost_benchmark_dept_version_dimension'
        ),
        comment='成本基准表'
    )
    
    # 创建索引
    op.create_index(op.f('ix_cost_benchmarks_id'), 'cost_benchmarks', ['id'], unique=False)
    op.create_index(op.f('ix_cost_benchmarks_hospital_id'), 'cost_benchmarks', ['hospital_id'], unique=False)
    op.create_index(op.f('ix_cost_benchmarks_department_code'), 'cost_benchmarks', ['department_code'], unique=False)
    op.create_index(op.f('ix_cost_benchmarks_version_id'), 'cost_benchmarks', ['version_id'], unique=False)
    op.create_index(op.f('ix_cost_benchmarks_dimension_code'), 'cost_benchmarks', ['dimension_code'], unique=False)


def downgrade() -> None:
    # 删除索引
    op.drop_index(op.f('ix_cost_benchmarks_dimension_code'), table_name='cost_benchmarks')
    op.drop_index(op.f('ix_cost_benchmarks_version_id'), table_name='cost_benchmarks')
    op.drop_index(op.f('ix_cost_benchmarks_department_code'), table_name='cost_benchmarks')
    op.drop_index(op.f('ix_cost_benchmarks_hospital_id'), table_name='cost_benchmarks')
    op.drop_index(op.f('ix_cost_benchmarks_id'), table_name='cost_benchmarks')
    
    # 删除表
    op.drop_table('cost_benchmarks')
