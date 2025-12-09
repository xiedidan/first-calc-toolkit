"""add AI prompt categories for report generation

Revision ID: 20251209_ai_prompt_cat
Revises: 20251208_remove_accounting_unit
Create Date: 2024-12-09

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '20251209_ai_prompt_cat'
down_revision = '20251208_remove_accounting_unit'
branch_labels = None
depends_on = None


def upgrade():
    # 创建 ai_prompt_configs 表，支持多个提示词分类
    op.execute("""
        CREATE TABLE IF NOT EXISTS ai_prompt_configs (
            id SERIAL PRIMARY KEY,
            hospital_id INTEGER NOT NULL REFERENCES hospitals(id) ON DELETE CASCADE,
            category VARCHAR(50) NOT NULL,
            system_prompt TEXT,
            user_prompt TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT NOW() NOT NULL,
            updated_at TIMESTAMP DEFAULT NOW() NOT NULL
        );
    """)
    
    # 添加唯一约束：每个医疗机构每个分类只有一个配置
    op.execute("""
        DO $$ BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM pg_constraint WHERE conname = 'uq_ai_prompt_config_hospital_category'
            ) THEN
                ALTER TABLE ai_prompt_configs 
                ADD CONSTRAINT uq_ai_prompt_config_hospital_category 
                UNIQUE (hospital_id, category);
            END IF;
        END $$;
    """)
    
    # 创建索引
    op.execute("""
        CREATE INDEX IF NOT EXISTS ix_ai_prompt_configs_hospital_id ON ai_prompt_configs(hospital_id);
    """)
    op.execute("""
        CREATE INDEX IF NOT EXISTS ix_ai_prompt_configs_category ON ai_prompt_configs(category);
    """)
    
    # 添加字段注释
    op.execute("""
        COMMENT ON TABLE ai_prompt_configs IS 'AI提示词配置表（按分类）';
    """)
    op.execute("""
        COMMENT ON COLUMN ai_prompt_configs.hospital_id IS '所属医疗机构ID';
    """)
    op.execute("""
        COMMENT ON COLUMN ai_prompt_configs.category IS '提示词分类：classification（智能分类分级）、report_issues（业务价值报表-当前存在问题）、report_plans（业务价值报表-未来发展计划）';
    """)
    op.execute("""
        COMMENT ON COLUMN ai_prompt_configs.system_prompt IS '系统提示词';
    """)
    op.execute("""
        COMMENT ON COLUMN ai_prompt_configs.user_prompt IS '用户提示词模板';
    """)
    
    # 迁移现有 ai_configs 表中的提示词到新表
    op.execute("""
        INSERT INTO ai_prompt_configs (hospital_id, category, system_prompt, user_prompt, created_at, updated_at)
        SELECT hospital_id, 'classification', system_prompt, prompt_template, created_at, updated_at
        FROM ai_configs
        WHERE prompt_template IS NOT NULL
        ON CONFLICT (hospital_id, category) DO NOTHING;
    """)


def downgrade():
    op.execute("DROP TABLE IF EXISTS ai_prompt_configs CASCADE;")
