"""add intelligent query system tables

Revision ID: 20251217_intelligent_query
Revises: 20251212_discipline_rules
Create Date: 2025-12-17

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '20251217_intelligent_query'
down_revision = '20251212_discipline_rules'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. 创建AI接口表
    op.create_table(
        'ai_interfaces',
        sa.Column('id', sa.Integer(), nullable=False, comment='主键'),
        sa.Column('hospital_id', sa.Integer(), nullable=False, comment='医疗机构ID'),
        sa.Column('name', sa.String(length=100), nullable=False, comment='接口名称'),
        sa.Column('api_endpoint', sa.String(length=500), nullable=False, comment='API端点'),
        sa.Column('model_name', sa.String(length=100), nullable=False, comment='模型名称'),
        sa.Column('api_key_encrypted', sa.Text(), nullable=False, comment='加密的API密钥'),
        sa.Column('call_delay', sa.Float(), nullable=False, server_default='1.0', comment='调用延迟（秒）'),
        sa.Column('daily_limit', sa.Integer(), nullable=False, server_default='10000', comment='每日调用限额'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true', comment='是否启用'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['hospital_id'], ['hospitals.id'], ondelete='CASCADE'),
        comment='AI接口配置表'
    )
    op.create_index('ix_ai_interfaces_hospital_id', 'ai_interfaces', ['hospital_id'])


    # 2. 创建AI提示词模块表
    op.create_table(
        'ai_prompt_modules',
        sa.Column('id', sa.Integer(), nullable=False, comment='主键'),
        sa.Column('hospital_id', sa.Integer(), nullable=False, comment='医疗机构ID'),
        sa.Column('module_code', sa.String(length=100), nullable=False, comment='模块代码'),
        sa.Column('module_name', sa.String(length=200), nullable=False, comment='模块名称'),
        sa.Column('description', sa.Text(), nullable=True, comment='模块描述'),
        sa.Column('ai_interface_id', sa.Integer(), nullable=True, comment='AI接口ID'),
        sa.Column('temperature', sa.Float(), nullable=False, server_default='0.7', comment='模型温度'),
        sa.Column('placeholders', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default='[]', comment='支持的占位符'),
        sa.Column('system_prompt', sa.Text(), nullable=True, comment='系统提示词'),
        sa.Column('user_prompt', sa.Text(), nullable=False, comment='用户提示词'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['hospital_id'], ['hospitals.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['ai_interface_id'], ['ai_interfaces.id'], ondelete='SET NULL'),
        sa.UniqueConstraint('hospital_id', 'module_code', name='uq_ai_prompt_module_hospital_code'),
        comment='AI提示词模块表'
    )
    op.create_index('ix_ai_prompt_modules_hospital_id', 'ai_prompt_modules', ['hospital_id'])
    op.create_index('ix_ai_prompt_modules_ai_interface_id', 'ai_prompt_modules', ['ai_interface_id'])

    # 3. 创建对话分组表
    op.create_table(
        'conversation_groups',
        sa.Column('id', sa.Integer(), nullable=False, comment='主键'),
        sa.Column('hospital_id', sa.Integer(), nullable=False, comment='医疗机构ID'),
        sa.Column('name', sa.String(length=100), nullable=False, comment='分组名称'),
        sa.Column('sort_order', sa.Integer(), nullable=False, server_default='0', comment='排序顺序'),
        sa.Column('is_collapsed', sa.Boolean(), nullable=False, server_default='false', comment='是否收起'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['hospital_id'], ['hospitals.id'], ondelete='CASCADE'),
        comment='对话分组表'
    )
    op.create_index('ix_conversation_groups_hospital_id', 'conversation_groups', ['hospital_id'])

    # 4. 创建对话表
    op.create_table(
        'conversations',
        sa.Column('id', sa.Integer(), nullable=False, comment='主键'),
        sa.Column('hospital_id', sa.Integer(), nullable=False, comment='医疗机构ID'),
        sa.Column('group_id', sa.Integer(), nullable=True, comment='分组ID'),
        sa.Column('title', sa.String(length=200), nullable=False, comment='对话标题'),
        sa.Column('description', sa.String(length=500), nullable=True, comment='对话描述'),
        sa.Column('conversation_type', sa.String(length=50), nullable=False, server_default='caliber', comment='对话类型'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['hospital_id'], ['hospitals.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['group_id'], ['conversation_groups.id'], ondelete='SET NULL'),
        comment='对话表'
    )
    op.create_index('ix_conversations_hospital_id', 'conversations', ['hospital_id'])
    op.create_index('ix_conversations_group_id', 'conversations', ['group_id'])


    # 5. 创建对话消息表
    op.create_table(
        'conversation_messages',
        sa.Column('id', sa.Integer(), nullable=False, comment='主键'),
        sa.Column('conversation_id', sa.Integer(), nullable=False, comment='对话ID'),
        sa.Column('role', sa.String(length=20), nullable=False, comment='角色(user/assistant)'),
        sa.Column('content', sa.Text(), nullable=False, comment='消息内容'),
        sa.Column('content_type', sa.String(length=50), nullable=False, server_default='text', comment='内容类型'),
        sa.Column('message_metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=True, comment='元数据(图表配置等)'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['conversation_id'], ['conversations.id'], ondelete='CASCADE'),
        comment='对话消息表'
    )
    op.create_index('ix_conversation_messages_conversation_id', 'conversation_messages', ['conversation_id'])

    # 6. 创建指标项目表
    op.create_table(
        'metric_projects',
        sa.Column('id', sa.Integer(), nullable=False, comment='主键'),
        sa.Column('hospital_id', sa.Integer(), nullable=False, comment='医疗机构ID'),
        sa.Column('name', sa.String(length=100), nullable=False, comment='项目名称'),
        sa.Column('description', sa.String(length=500), nullable=True, comment='项目描述'),
        sa.Column('sort_order', sa.Integer(), nullable=False, server_default='0', comment='排序顺序'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['hospital_id'], ['hospitals.id'], ondelete='CASCADE'),
        comment='指标项目表'
    )
    op.create_index('ix_metric_projects_hospital_id', 'metric_projects', ['hospital_id'])

    # 7. 创建指标主题表
    op.create_table(
        'metric_topics',
        sa.Column('id', sa.Integer(), nullable=False, comment='主键'),
        sa.Column('project_id', sa.Integer(), nullable=False, comment='项目ID'),
        sa.Column('name', sa.String(length=100), nullable=False, comment='主题名称'),
        sa.Column('description', sa.String(length=500), nullable=True, comment='主题描述'),
        sa.Column('sort_order', sa.Integer(), nullable=False, server_default='0', comment='排序顺序'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['project_id'], ['metric_projects.id'], ondelete='CASCADE'),
        comment='指标主题表'
    )
    op.create_index('ix_metric_topics_project_id', 'metric_topics', ['project_id'])


    # 8. 创建指标表
    op.create_table(
        'metrics',
        sa.Column('id', sa.Integer(), nullable=False, comment='主键'),
        sa.Column('topic_id', sa.Integer(), nullable=False, comment='主题ID'),
        sa.Column('name_cn', sa.String(length=200), nullable=False, comment='中文名称'),
        sa.Column('name_en', sa.String(length=200), nullable=True, comment='英文名称'),
        sa.Column('metric_type', sa.String(length=50), nullable=False, server_default='atomic', comment='指标类型'),
        sa.Column('metric_level', sa.String(length=100), nullable=True, comment='指标层级'),
        sa.Column('business_caliber', sa.Text(), nullable=True, comment='业务口径'),
        sa.Column('technical_caliber', sa.Text(), nullable=True, comment='技术口径'),
        sa.Column('source_table', sa.String(length=200), nullable=True, comment='源表'),
        sa.Column('dimension_tables', postgresql.JSONB(astext_type=sa.Text()), nullable=True, comment='关联维表'),
        sa.Column('dimensions', postgresql.JSONB(astext_type=sa.Text()), nullable=True, comment='指标维度'),
        sa.Column('data_source_id', sa.Integer(), nullable=True, comment='数据源ID'),
        sa.Column('sort_order', sa.Integer(), nullable=False, server_default='0', comment='排序顺序'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['topic_id'], ['metric_topics.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['data_source_id'], ['data_sources.id'], ondelete='SET NULL'),
        comment='指标表'
    )
    op.create_index('ix_metrics_topic_id', 'metrics', ['topic_id'])
    op.create_index('ix_metrics_data_source_id', 'metrics', ['data_source_id'])

    # 9. 创建指标关联表
    op.create_table(
        'metric_relations',
        sa.Column('id', sa.Integer(), nullable=False, comment='主键'),
        sa.Column('source_metric_id', sa.Integer(), nullable=False, comment='源指标ID'),
        sa.Column('target_metric_id', sa.Integer(), nullable=False, comment='目标指标ID'),
        sa.Column('relation_type', sa.String(length=50), nullable=False, server_default='component', comment='关联类型'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['source_metric_id'], ['metrics.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['target_metric_id'], ['metrics.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('source_metric_id', 'target_metric_id', name='uq_metric_relation_source_target'),
        comment='指标关联表'
    )
    op.create_index('ix_metric_relations_source_metric_id', 'metric_relations', ['source_metric_id'])
    op.create_index('ix_metric_relations_target_metric_id', 'metric_relations', ['target_metric_id'])


def downgrade() -> None:
    # 按创建的逆序删除表
    op.drop_index('ix_metric_relations_target_metric_id', table_name='metric_relations')
    op.drop_index('ix_metric_relations_source_metric_id', table_name='metric_relations')
    op.drop_table('metric_relations')
    
    op.drop_index('ix_metrics_data_source_id', table_name='metrics')
    op.drop_index('ix_metrics_topic_id', table_name='metrics')
    op.drop_table('metrics')
    
    op.drop_index('ix_metric_topics_project_id', table_name='metric_topics')
    op.drop_table('metric_topics')
    
    op.drop_index('ix_metric_projects_hospital_id', table_name='metric_projects')
    op.drop_table('metric_projects')
    
    op.drop_index('ix_conversation_messages_conversation_id', table_name='conversation_messages')
    op.drop_table('conversation_messages')
    
    op.drop_index('ix_conversations_group_id', table_name='conversations')
    op.drop_index('ix_conversations_hospital_id', table_name='conversations')
    op.drop_table('conversations')
    
    op.drop_index('ix_conversation_groups_hospital_id', table_name='conversation_groups')
    op.drop_table('conversation_groups')
    
    op.drop_index('ix_ai_prompt_modules_ai_interface_id', table_name='ai_prompt_modules')
    op.drop_index('ix_ai_prompt_modules_hospital_id', table_name='ai_prompt_modules')
    op.drop_table('ai_prompt_modules')
    
    op.drop_index('ix_ai_interfaces_hospital_id', table_name='ai_interfaces')
    op.drop_table('ai_interfaces')
