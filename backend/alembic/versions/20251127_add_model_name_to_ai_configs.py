"""add model_name to ai_configs

Revision ID: 20251127_model_name
Revises: 20251126_ai_classification
Create Date: 2025-11-27

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '20251127_model_name'
down_revision = '20251126_ai_classification'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 添加 model_name 字段到 ai_configs 表
    op.execute("""
        DO $$ BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM information_schema.columns 
                WHERE table_name = 'ai_configs' AND column_name = 'model_name'
            ) THEN
                ALTER TABLE ai_configs ADD COLUMN model_name VARCHAR(100) NOT NULL DEFAULT 'deepseek-chat';
                COMMENT ON COLUMN ai_configs.model_name IS '模型名称';
            END IF;
        END $$;
    """)


def downgrade() -> None:
    op.drop_column('ai_configs', 'model_name')
