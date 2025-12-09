"""
合并多个迁移分支

Revision ID: 20251203_merge
Revises: 20251128_revenue, 20251202_refval, 20251203_role_perm
Create Date: 2025-12-03
"""
from alembic import op

revision = '20251203_merge'
down_revision = ('20251128_revenue', '20251202_refval', '20251203_role_perm')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
