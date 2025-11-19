"""add indexes to charge items

Revision ID: a1b2c3d4e5f6
Revises: f0384ea4c792
Create Date: 2025-10-22 17:30:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a1b2c3d4e5f6'
down_revision = 'f0384ea4c792'
branch_labels = None
depends_on = None


def upgrade():
    # 添加索引以优化查询性能
    # item_name 索引 - 用于搜索
    op.create_index(
        'ix_charge_items_item_name',
        'charge_items',
        ['item_name'],
        unique=False
    )
    
    # item_category 索引 - 用于分类筛选
    op.create_index(
        'ix_charge_items_item_category',
        'charge_items',
        ['item_category'],
        unique=False
    )


def downgrade():
    # 删除索引
    op.drop_index('ix_charge_items_item_category', table_name='charge_items')
    op.drop_index('ix_charge_items_item_name', table_name='charge_items')
