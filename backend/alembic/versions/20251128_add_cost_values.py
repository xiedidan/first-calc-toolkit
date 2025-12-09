"""add cost values table

Revision ID: 20251128_add_cost_values
Revises: 20251127_add_orientation_values
Create Date: 2025-11-28

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '20251128_add_cost_values'
down_revision = '20251127_add_cost_benchmarks'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'cost_values',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('hospital_id', sa.Integer(), nullable=False),
        sa.Column('year_month', sa.String(7), nullable=False, comment='年月，格式：YYYY-MM'),
        sa.Column('dept_code', sa.String(50), nullable=False, comment='科室代码'),
        sa.Column('dept_name', sa.String(200), nullable=False, comment='科室名称'),
        sa.Column('dimension_code', sa.String(50), nullable=False, comment='维度代码'),
        sa.Column('dimension_name', sa.String(200), nullable=False, comment='维度名称'),
        sa.Column('cost_value', sa.Numeric(15, 2), nullable=False, comment='成本值'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.PrimaryKeyConstraint('id')
    )
    
    # 创建索引
    op.create_index('ix_cost_values_hospital_id', 'cost_values', ['hospital_id'])
    op.create_index('ix_cost_values_year_month', 'cost_values', ['year_month'])
    op.create_index('ix_cost_values_dept_code', 'cost_values', ['dept_code'])
    op.create_index('ix_cost_values_dimension_code', 'cost_values', ['dimension_code'])
    
    # 创建复合唯一约束（多租户隔离）
    op.create_unique_constraint(
        'uq_cost_values_hospital_period_dept_dim',
        'cost_values',
        ['hospital_id', 'year_month', 'dept_code', 'dimension_code']
    )
    
    # 添加外键约束
    op.execute("""
        DO $$ BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM pg_constraint WHERE conname = 'fk_cost_values_hospital_id'
            ) THEN
                ALTER TABLE cost_values 
                ADD CONSTRAINT fk_cost_values_hospital_id 
                FOREIGN KEY (hospital_id) REFERENCES hospitals(id) ON DELETE CASCADE;
            END IF;
        END $$;
    """)


def downgrade():
    op.drop_table('cost_values')
