"""add discipline rules table

Revision ID: 20251212_discipline_rules
Revises: l6m7n8o9p0q1
Create Date: 2025-12-12

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '20251212_discipline_rules'
down_revision = '20251211_add_cost_reports'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 创建学科规则表
    op.create_table(
        'discipline_rules',
        sa.Column('id', sa.Integer(), nullable=False, comment='主键'),
        sa.Column('hospital_id', sa.Integer(), nullable=False, comment='所属医疗机构ID'),
        sa.Column('version_id', sa.Integer(), nullable=False, comment='模型版本ID'),
        sa.Column('department_code', sa.String(length=50), nullable=False, comment='科室代码'),
        sa.Column('department_name', sa.String(length=100), nullable=False, comment='科室名称'),
        sa.Column('dimension_code', sa.String(length=100), nullable=False, comment='维度代码'),
        sa.Column('dimension_name', sa.String(length=200), nullable=False, comment='维度名称'),
        sa.Column('rule_description', sa.String(length=500), nullable=True, comment='规则描述'),
        sa.Column('rule_coefficient', sa.Numeric(precision=10, scale=4), nullable=False, default=1.0, comment='规则系数'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['hospital_id'], ['hospitals.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['version_id'], ['model_versions.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('hospital_id', 'version_id', 'department_code', 'dimension_code', 
                          name='uq_discipline_rule_version_dept_dim'),
        comment='学科规则表'
    )
    
    # 创建索引
    op.create_index('ix_discipline_rules_hospital_id', 'discipline_rules', ['hospital_id'])
    op.create_index('ix_discipline_rules_version_id', 'discipline_rules', ['version_id'])
    op.create_index('ix_discipline_rules_department_code', 'discipline_rules', ['department_code'])
    op.create_index('ix_discipline_rules_dimension_code', 'discipline_rules', ['dimension_code'])


def downgrade() -> None:
    op.drop_index('ix_discipline_rules_dimension_code', table_name='discipline_rules')
    op.drop_index('ix_discipline_rules_department_code', table_name='discipline_rules')
    op.drop_index('ix_discipline_rules_version_id', table_name='discipline_rules')
    op.drop_index('ix_discipline_rules_hospital_id', table_name='discipline_rules')
    op.drop_table('discipline_rules')
