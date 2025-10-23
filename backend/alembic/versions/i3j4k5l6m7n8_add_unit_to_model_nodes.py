"""Add unit to model_nodes

Revision ID: i3j4k5l6m7n8
Revises: h2i3j4k5l6m7
Create Date: 2025-10-22 19:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'i3j4k5l6m7n8'
down_revision = 'h2i3j4k5l6m7'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 添加 unit 字段
    op.add_column('model_nodes', sa.Column('unit', sa.String(length=20), nullable=True, server_default='%', comment='单位'))


def downgrade() -> None:
    # 删除 unit 字段
    op.drop_column('model_nodes', 'unit')
