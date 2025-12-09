"""add original_weight to calculation_results

Revision ID: 20251128_add_original_weight
Revises: 20251128_add_orientation_adjustment_details
Create Date: 2025-11-28

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '20251128_add_original_weight'
down_revision = '20251128_orientation_details'
branch_labels = None
depends_on = None


def upgrade():
    # 添加 original_weight 字段
    op.add_column('calculation_results', 
        sa.Column('original_weight', sa.DECIMAL(precision=10, scale=4), nullable=True, comment='原始权重（未调整）')
    )


def downgrade():
    op.drop_column('calculation_results', 'original_weight')
