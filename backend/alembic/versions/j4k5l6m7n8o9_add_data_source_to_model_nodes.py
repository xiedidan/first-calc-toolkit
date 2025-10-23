"""Add data_source to model_nodes

Revision ID: j4k5l6m7n8o9
Revises: i3j4k5l6m7n8
Create Date: 2025-10-23 10:30:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'j4k5l6m7n8o9'
down_revision = 'i3j4k5l6m7n8'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 添加 data_source 字段
    op.add_column('model_nodes', sa.Column('data_source', sa.String(length=50), nullable=True, server_default='HIS', comment='数据来源'))


def downgrade() -> None:
    # 删除 data_source 字段
    op.drop_column('model_nodes', 'data_source')
