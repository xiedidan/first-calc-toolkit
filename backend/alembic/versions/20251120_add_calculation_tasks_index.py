"""add calculation tasks index

Revision ID: m7n8o9p0q1r2
Revises: l6m7n8o9p0q1
Create Date: 2025-11-20

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'm7n8o9p0q1r2'
down_revision = '20251119_data_issues'  # 修复：接在最新的迁移后面
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 检查索引是否已存在，如果不存在则创建
    # 使用 DO 块实现幂等性
    op.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM pg_indexes 
                WHERE indexname = 'idx_calculation_tasks_period_status'
            ) THEN
                CREATE INDEX idx_calculation_tasks_period_status 
                ON calculation_tasks(period, status, model_version_id);
            END IF;
        END $$;
    """)


def downgrade() -> None:
    # 删除索引（如果存在）
    op.execute("""
        DROP INDEX IF EXISTS idx_calculation_tasks_period_status;
    """)
