"""add system_prompt to ai_configs

Revision ID: 20251127_system_prompt
Revises: 20251127_model_name
Create Date: 2025-11-27

"""
from alembic import op
import sqlalchemy as sa

revision = '20251127_system_prompt'
down_revision = '20251127_model_name'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
        DO $$ BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM information_schema.columns 
                WHERE table_name = 'ai_configs' AND column_name = 'system_prompt'
            ) THEN
                ALTER TABLE ai_configs ADD COLUMN system_prompt TEXT;
                COMMENT ON COLUMN ai_configs.system_prompt IS '系统提示词';
            END IF;
        END $$;
    """)


def downgrade() -> None:
    op.drop_column('ai_configs', 'system_prompt')
