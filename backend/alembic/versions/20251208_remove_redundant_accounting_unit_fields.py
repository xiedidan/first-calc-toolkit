"""remove redundant accounting unit fields from calculation_results

Revision ID: 20251208_remove_accounting_unit
Revises: 20251208_add_accounting_sequences_to_departments
Create Date: 2025-12-08

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20251208_remove_accounting_unit'
down_revision = '20251208_accounting_seq'
branch_labels = None
depends_on = None


def upgrade():
    # 删除索引（如果存在）
    conn = op.get_bind()
    index_exists = conn.execute(sa.text("""
        SELECT EXISTS (
            SELECT 1 FROM pg_indexes 
            WHERE indexname = 'ix_calculation_results_accounting_unit'
        )
    """)).scalar()
    
    if index_exists:
        op.drop_index('ix_calculation_results_accounting_unit', table_name='calculation_results')
    
    # 删除冗余字段（如果存在）
    inspector = sa.inspect(conn)
    columns = [col['name'] for col in inspector.get_columns('calculation_results')]
    
    if 'accounting_unit_code' in columns:
        op.drop_column('calculation_results', 'accounting_unit_code')
    if 'accounting_unit_name' in columns:
        op.drop_column('calculation_results', 'accounting_unit_name')


def downgrade():
    # 恢复字段
    op.add_column('calculation_results', sa.Column('accounting_unit_name', sa.VARCHAR(length=100), nullable=True))
    op.add_column('calculation_results', sa.Column('accounting_unit_code', sa.VARCHAR(length=50), nullable=True))
    
    # 恢复索引
    op.create_index('ix_calculation_results_accounting_unit', 'calculation_results', ['accounting_unit_code'], unique=False)
