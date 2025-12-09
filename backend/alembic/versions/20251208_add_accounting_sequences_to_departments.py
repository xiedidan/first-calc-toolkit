"""add accounting sequences to departments

Revision ID: m7n8o9p0q1r2
Revises: 20251205_analysis_reports
Create Date: 2024-12-08

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '20251208_accounting_seq'
down_revision = '20251205_analysis_reports'
branch_labels = None
depends_on = None


def upgrade():
    # 添加核算序列字段，使用ARRAY类型支持多选
    op.add_column('departments', 
        sa.Column('accounting_sequences', 
                  postgresql.ARRAY(sa.String(20)), 
                  nullable=True, 
                  comment='核算序列（可多选：医生、护理、医技）'))
    
    # 创建索引以提高查询性能
    op.create_index('ix_departments_accounting_sequences', 
                    'departments', 
                    ['accounting_sequences'], 
                    postgresql_using='gin')


def downgrade():
    op.drop_index('ix_departments_accounting_sequences', table_name='departments')
    op.drop_column('departments', 'accounting_sequences')
