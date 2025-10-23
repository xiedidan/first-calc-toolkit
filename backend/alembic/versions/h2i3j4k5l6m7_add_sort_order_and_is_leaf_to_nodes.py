"""Add sort_order and is_leaf to model_nodes

Revision ID: h2i3j4k5l6m7
Revises: g1h2i3j4k5l6
Create Date: 2025-10-22 18:30:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'h2i3j4k5l6m7'
down_revision = 'g1h2i3j4k5l6'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 添加 sort_order 字段
    op.add_column('model_nodes', sa.Column('sort_order', sa.Numeric(precision=10, scale=2), nullable=False, server_default='0', comment='排序序号'))
    
    # 添加 is_leaf 字段
    op.add_column('model_nodes', sa.Column('is_leaf', sa.Boolean(), nullable=False, server_default='false', comment='是否为末级维度'))
    
    # 创建索引
    op.create_index(op.f('ix_model_nodes_sort_order'), 'model_nodes', ['sort_order'], unique=False)


def downgrade() -> None:
    # 删除索引
    op.drop_index(op.f('ix_model_nodes_sort_order'), table_name='model_nodes')
    
    # 删除字段
    op.drop_column('model_nodes', 'is_leaf')
    op.drop_column('model_nodes', 'sort_order')
