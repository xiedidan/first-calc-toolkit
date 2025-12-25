"""add cost reports table

Revision ID: 20251211_add_cost_reports
Revises: 20251209_add_ai_prompt_categories
Create Date: 2025-12-11

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20251211_add_cost_reports'
down_revision = '20251210_task_id'
branch_labels = None
depends_on = None


def upgrade():
    # 创建成本报表表
    op.create_table(
        'cost_reports',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('hospital_id', sa.Integer(), nullable=False, comment='医疗机构ID'),
        sa.Column('period', sa.String(7), nullable=False, comment='年月，格式：YYYY-MM'),
        sa.Column('department_code', sa.String(50), nullable=False, comment='科室代码'),
        sa.Column('department_name', sa.String(100), nullable=False, comment='科室名称'),
        sa.Column('personnel_cost', sa.Numeric(18, 4), nullable=False, server_default='0', comment='人员经费'),
        sa.Column('material_cost', sa.Numeric(18, 4), nullable=False, server_default='0', comment='不收费卫生材料费'),
        sa.Column('medicine_cost', sa.Numeric(18, 4), nullable=False, server_default='0', comment='不收费药品费'),
        sa.Column('depreciation_cost', sa.Numeric(18, 4), nullable=False, server_default='0', comment='折旧风险费'),
        sa.Column('other_cost', sa.Numeric(18, 4), nullable=False, server_default='0', comment='其他费用'),
        sa.Column('created_at', sa.DateTime(), nullable=True, comment='创建时间'),
        sa.Column('updated_at', sa.DateTime(), nullable=True, comment='更新时间'),
        sa.ForeignKeyConstraint(['hospital_id'], ['hospitals.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('hospital_id', 'period', 'department_code', name='uq_cost_report_hospital_period_dept'),
        comment='成本报表'
    )
    op.create_index(op.f('ix_cost_reports_hospital_id'), 'cost_reports', ['hospital_id'], unique=False)
    op.create_index(op.f('ix_cost_reports_period'), 'cost_reports', ['period'], unique=False)
    op.create_index(op.f('ix_cost_reports_department_code'), 'cost_reports', ['department_code'], unique=False)


def downgrade():
    op.drop_index(op.f('ix_cost_reports_department_code'), table_name='cost_reports')
    op.drop_index(op.f('ix_cost_reports_period'), table_name='cost_reports')
    op.drop_index(op.f('ix_cost_reports_hospital_id'), table_name='cost_reports')
    op.drop_table('cost_reports')
