"""Add rule to model_nodes

Revision ID: k5l6m7n8o9p0
Revises: j4k5l6m7n8o9
Create Date: 2025-10-23 20:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'k5l6m7n8o9p0'
down_revision = 'j4k5l6m7n8o9'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 添加 rule 字段
    op.add_column('model_nodes', sa.Column('rule', sa.Text(), nullable=True, comment='规则说明'))


def downgrade() -> None:
    # 删除 rule 字段
    op.drop_column('model_nodes', 'rule')
