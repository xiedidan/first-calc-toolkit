"""migrate ai_configs and ai_prompt_configs to new tables

Revision ID: 20251222_ai_migrate
Revises: 20251219_source_tables
Create Date: 2024-12-22

将旧的 ai_configs 表数据迁移到新的 ai_interfaces 表
将旧的 ai_prompt_configs 表数据迁移到新的 ai_prompt_modules 表
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20251222_ai_migrate'
down_revision = '20251219_source_tables'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. 将 ai_configs 表中的数据迁移到 ai_interfaces 表
    # 按 api_endpoint + model_name 组合判断是否已存在，保留不同的配置
    op.execute("""
        INSERT INTO ai_interfaces (
            hospital_id, 
            name, 
            api_endpoint, 
            model_name, 
            api_key_encrypted, 
            call_delay, 
            daily_limit, 
            is_active, 
            created_at, 
            updated_at
        )
        SELECT 
            c.hospital_id,
            COALESCE(c.model_name, 'deepseek-chat') || '（迁移）' as name,
            c.api_endpoint,
            COALESCE(c.model_name, 'deepseek-chat') as model_name,
            c.api_key_encrypted,
            c.call_delay,
            c.daily_limit,
            true as is_active,
            c.created_at,
            c.updated_at
        FROM ai_configs c
        WHERE NOT EXISTS (
            SELECT 1 FROM ai_interfaces i 
            WHERE i.hospital_id = c.hospital_id 
            AND i.api_endpoint = c.api_endpoint 
            AND i.model_name = COALESCE(c.model_name, 'deepseek-chat')
        );
    """)
    
    # 2. 为迁移过来的接口自动关联到提示词模块
    # 找到每个医院的第一个AI接口，关联到所有未配置接口的模块
    op.execute("""
        UPDATE ai_prompt_modules m
        SET ai_interface_id = (
            SELECT id FROM ai_interfaces i 
            WHERE i.hospital_id = m.hospital_id 
            ORDER BY i.created_at ASC 
            LIMIT 1
        )
        WHERE m.ai_interface_id IS NULL
        AND EXISTS (
            SELECT 1 FROM ai_interfaces i 
            WHERE i.hospital_id = m.hospital_id
        );
    """)
    
    # 3. 将 ai_prompt_configs 表中的自定义提示词迁移到 ai_prompt_modules 表
    # 分类到模块代码的映射：
    # - classification -> classification
    # - report_issues -> report_issues  
    # - report_plans -> report_plans
    
    # 迁移 classification 分类的提示词
    op.execute("""
        UPDATE ai_prompt_modules m
        SET 
            system_prompt = COALESCE(p.system_prompt, m.system_prompt),
            user_prompt = COALESCE(p.user_prompt, m.user_prompt),
            updated_at = COALESCE(p.updated_at, m.updated_at)
        FROM ai_prompt_configs p
        WHERE m.hospital_id = p.hospital_id
        AND m.module_code = 'classification'
        AND p.category = 'classification'
        AND (p.system_prompt IS NOT NULL OR p.user_prompt IS NOT NULL);
    """)
    
    # 迁移 report_issues 分类的提示词
    op.execute("""
        UPDATE ai_prompt_modules m
        SET 
            system_prompt = COALESCE(p.system_prompt, m.system_prompt),
            user_prompt = COALESCE(p.user_prompt, m.user_prompt),
            updated_at = COALESCE(p.updated_at, m.updated_at)
        FROM ai_prompt_configs p
        WHERE m.hospital_id = p.hospital_id
        AND m.module_code = 'report_issues'
        AND p.category = 'report_issues'
        AND (p.system_prompt IS NOT NULL OR p.user_prompt IS NOT NULL);
    """)
    
    # 迁移 report_plans 分类的提示词
    op.execute("""
        UPDATE ai_prompt_modules m
        SET 
            system_prompt = COALESCE(p.system_prompt, m.system_prompt),
            user_prompt = COALESCE(p.user_prompt, m.user_prompt),
            updated_at = COALESCE(p.updated_at, m.updated_at)
        FROM ai_prompt_configs p
        WHERE m.hospital_id = p.hospital_id
        AND m.module_code = 'report_plans'
        AND p.category = 'report_plans'
        AND (p.system_prompt IS NOT NULL OR p.user_prompt IS NOT NULL);
    """)


def downgrade() -> None:
    # 回滚：删除从 ai_configs 迁移过来的记录（名称为"默认AI接口"的）
    op.execute("""
        DELETE FROM ai_interfaces 
        WHERE name = '默认AI接口';
    """)
    # 注意：提示词的回滚比较复杂，因为无法区分哪些是迁移的、哪些是新创建的
    # 建议在回滚前手动备份 ai_prompt_modules 表
