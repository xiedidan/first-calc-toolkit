"""add ai classification tables

Revision ID: 20251126_ai_classification
Revises: 20251126_orientation
Create Date: 2025-11-26

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '20251126_ai_classification'
down_revision = '20251126_orientation_ids'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 创建枚举类型：任务状态
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE task_status AS ENUM ('pending', 'processing', 'completed', 'failed', 'paused');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)
    
    # 创建枚举类型：预案状态
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE plan_status AS ENUM ('draft', 'submitted');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)
    
    # 创建枚举类型：处理状态
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE processing_status AS ENUM ('pending', 'processing', 'completed', 'failed');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)
    
    # 创建枚举类型：进度状态
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE progress_status AS ENUM ('pending', 'processing', 'completed', 'failed');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)
    
    # 创建AI配置表
    op.create_table(
        'ai_configs',
        sa.Column('id', sa.Integer(), nullable=False, comment='主键'),
        sa.Column('hospital_id', sa.Integer(), nullable=False, comment='医疗机构ID'),
        sa.Column('api_endpoint', sa.String(length=500), nullable=False, comment='API访问端点'),
        sa.Column('api_key_encrypted', sa.Text(), nullable=False, comment='加密的API密钥'),
        sa.Column('prompt_template', sa.Text(), nullable=False, comment='提示词模板'),
        sa.Column('call_delay', sa.Float(), nullable=False, server_default='1.0', comment='调用延迟（秒）'),
        sa.Column('daily_limit', sa.Integer(), nullable=False, server_default='10000', comment='每日调用限额'),
        sa.Column('batch_size', sa.Integer(), nullable=False, server_default='100', comment='批次大小'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()'), comment='创建时间'),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()'), comment='更新时间'),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['hospital_id'], ['hospitals.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('hospital_id', name='uq_ai_config_hospital')
    )
    op.create_index('ix_ai_configs_id', 'ai_configs', ['id'], unique=False)
    op.create_index('ix_ai_configs_hospital_id', 'ai_configs', ['hospital_id'], unique=False)
    op.execute("COMMENT ON TABLE ai_configs IS 'AI接口配置表'")
    
    # 创建分类任务表
    op.create_table(
        'classification_tasks',
        sa.Column('id', sa.Integer(), nullable=False, comment='主键'),
        sa.Column('hospital_id', sa.Integer(), nullable=False, comment='医疗机构ID'),
        sa.Column('task_name', sa.String(length=100), nullable=False, comment='任务名称'),
        sa.Column('model_version_id', sa.Integer(), nullable=False, comment='模型版本ID'),
        sa.Column('charge_categories', postgresql.JSON(astext_type=sa.Text()), nullable=False, comment='收费类别列表'),
        sa.Column('status', postgresql.ENUM('pending', 'processing', 'completed', 'failed', 'paused', name='task_status', create_type=False), nullable=False, server_default='pending', comment='任务状态'),
        sa.Column('total_items', sa.Integer(), nullable=False, server_default='0', comment='总项目数'),
        sa.Column('processed_items', sa.Integer(), nullable=False, server_default='0', comment='已处理项目数'),
        sa.Column('failed_items', sa.Integer(), nullable=False, server_default='0', comment='失败项目数'),
        sa.Column('celery_task_id', sa.String(length=255), nullable=True, comment='Celery任务ID'),
        sa.Column('error_message', sa.Text(), nullable=True, comment='错误信息'),
        sa.Column('started_at', sa.DateTime(), nullable=True, comment='开始时间'),
        sa.Column('completed_at', sa.DateTime(), nullable=True, comment='完成时间'),
        sa.Column('created_by', sa.Integer(), nullable=False, comment='创建人ID'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()'), comment='创建时间'),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()'), comment='更新时间'),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['hospital_id'], ['hospitals.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['model_version_id'], ['model_versions.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'])
    )
    op.create_index('ix_classification_tasks_id', 'classification_tasks', ['id'], unique=False)
    op.create_index('ix_classification_tasks_hospital_id', 'classification_tasks', ['hospital_id'], unique=False)
    op.execute("COMMENT ON TABLE classification_tasks IS '分类任务表'")
    
    # 创建分类预案表
    op.create_table(
        'classification_plans',
        sa.Column('id', sa.Integer(), nullable=False, comment='主键'),
        sa.Column('hospital_id', sa.Integer(), nullable=False, comment='医疗机构ID'),
        sa.Column('task_id', sa.Integer(), nullable=False, comment='分类任务ID'),
        sa.Column('plan_name', sa.String(length=100), nullable=True, comment='预案名称'),
        sa.Column('status', postgresql.ENUM('draft', 'submitted', name='plan_status', create_type=False), nullable=False, server_default='draft', comment='预案状态'),
        sa.Column('submitted_at', sa.DateTime(), nullable=True, comment='提交时间'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()'), comment='创建时间'),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()'), comment='更新时间'),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['hospital_id'], ['hospitals.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['task_id'], ['classification_tasks.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('task_id', name='uq_classification_plan_task')
    )
    op.create_index('ix_classification_plans_id', 'classification_plans', ['id'], unique=False)
    op.create_index('ix_classification_plans_hospital_id', 'classification_plans', ['hospital_id'], unique=False)
    op.execute("COMMENT ON TABLE classification_plans IS '分类预案表'")
    
    # 创建预案项目表
    op.create_table(
        'plan_items',
        sa.Column('id', sa.Integer(), nullable=False, comment='主键'),
        sa.Column('hospital_id', sa.Integer(), nullable=False, comment='医疗机构ID'),
        sa.Column('plan_id', sa.Integer(), nullable=False, comment='预案ID'),
        sa.Column('charge_item_id', sa.Integer(), nullable=False, comment='收费项目ID'),
        sa.Column('charge_item_name', sa.String(length=200), nullable=False, comment='收费项目名称'),
        sa.Column('ai_suggested_dimension_id', sa.Integer(), nullable=True, comment='AI建议维度ID'),
        sa.Column('ai_confidence', sa.Numeric(precision=5, scale=4), nullable=True, comment='AI确信度（0-1）'),
        sa.Column('user_set_dimension_id', sa.Integer(), nullable=True, comment='用户设置维度ID'),
        sa.Column('is_adjusted', sa.Boolean(), nullable=False, server_default='false', comment='是否已调整'),
        sa.Column('processing_status', postgresql.ENUM('pending', 'processing', 'completed', 'failed', name='processing_status', create_type=False), nullable=False, server_default='pending', comment='处理状态'),
        sa.Column('error_message', sa.Text(), nullable=True, comment='错误信息'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()'), comment='创建时间'),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()'), comment='更新时间'),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['hospital_id'], ['hospitals.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['plan_id'], ['classification_plans.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['charge_item_id'], ['charge_items.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['ai_suggested_dimension_id'], ['model_nodes.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['user_set_dimension_id'], ['model_nodes.id'], ondelete='SET NULL'),
        sa.UniqueConstraint('plan_id', 'charge_item_id', name='uq_plan_item')
    )
    op.create_index('ix_plan_items_id', 'plan_items', ['id'], unique=False)
    op.create_index('ix_plan_items_hospital_id', 'plan_items', ['hospital_id'], unique=False)
    op.create_index('ix_plan_items_plan_id', 'plan_items', ['plan_id'], unique=False)
    op.execute("COMMENT ON TABLE plan_items IS '预案项目表'")
    
    # 创建任务进度表
    op.create_table(
        'task_progress',
        sa.Column('id', sa.Integer(), nullable=False, comment='主键'),
        sa.Column('task_id', sa.Integer(), nullable=False, comment='分类任务ID'),
        sa.Column('charge_item_id', sa.Integer(), nullable=False, comment='收费项目ID'),
        sa.Column('status', postgresql.ENUM('pending', 'processing', 'completed', 'failed', name='progress_status', create_type=False), nullable=False, server_default='pending', comment='处理状态'),
        sa.Column('error_message', sa.Text(), nullable=True, comment='错误信息'),
        sa.Column('processed_at', sa.DateTime(), nullable=True, comment='处理时间'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()'), comment='创建时间'),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['task_id'], ['classification_tasks.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['charge_item_id'], ['charge_items.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('task_id', 'charge_item_id', name='uq_task_progress')
    )
    op.create_index('ix_task_progress_id', 'task_progress', ['id'], unique=False)
    op.create_index('ix_task_progress_task_id', 'task_progress', ['task_id'], unique=False)
    op.execute("COMMENT ON TABLE task_progress IS '任务进度记录表'")
    
    # 创建API使用日志表
    op.create_table(
        'api_usage_logs',
        sa.Column('id', sa.Integer(), nullable=False, comment='主键'),
        sa.Column('hospital_id', sa.Integer(), nullable=False, comment='医疗机构ID'),
        sa.Column('task_id', sa.Integer(), nullable=False, comment='分类任务ID'),
        sa.Column('charge_item_id', sa.Integer(), nullable=False, comment='收费项目ID'),
        sa.Column('request_data', postgresql.JSON(astext_type=sa.Text()), nullable=True, comment='请求数据'),
        sa.Column('response_data', postgresql.JSON(astext_type=sa.Text()), nullable=True, comment='响应数据'),
        sa.Column('status_code', sa.Integer(), nullable=True, comment='HTTP状态码'),
        sa.Column('error_message', sa.Text(), nullable=True, comment='错误信息'),
        sa.Column('call_duration', sa.Float(), nullable=True, comment='调用耗时（秒）'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()'), comment='创建时间'),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['hospital_id'], ['hospitals.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['task_id'], ['classification_tasks.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['charge_item_id'], ['charge_items.id'], ondelete='CASCADE')
    )
    op.create_index('ix_api_usage_logs_id', 'api_usage_logs', ['id'], unique=False)
    op.create_index('ix_api_usage_logs_hospital_id', 'api_usage_logs', ['hospital_id'], unique=False)
    op.create_index('ix_api_usage_logs_task_id', 'api_usage_logs', ['task_id'], unique=False)
    op.create_index('ix_api_usage_logs_created_at', 'api_usage_logs', ['created_at'], unique=False)
    op.execute("COMMENT ON TABLE api_usage_logs IS 'API使用日志表'")


def downgrade() -> None:
    # 删除API使用日志表
    op.drop_index('ix_api_usage_logs_created_at', table_name='api_usage_logs')
    op.drop_index('ix_api_usage_logs_task_id', table_name='api_usage_logs')
    op.drop_index('ix_api_usage_logs_hospital_id', table_name='api_usage_logs')
    op.drop_index('ix_api_usage_logs_id', table_name='api_usage_logs')
    op.drop_table('api_usage_logs')
    
    # 删除任务进度表
    op.drop_index('ix_task_progress_task_id', table_name='task_progress')
    op.drop_index('ix_task_progress_id', table_name='task_progress')
    op.drop_table('task_progress')
    
    # 删除预案项目表
    op.drop_index('ix_plan_items_plan_id', table_name='plan_items')
    op.drop_index('ix_plan_items_hospital_id', table_name='plan_items')
    op.drop_index('ix_plan_items_id', table_name='plan_items')
    op.drop_table('plan_items')
    
    # 删除分类预案表
    op.drop_index('ix_classification_plans_hospital_id', table_name='classification_plans')
    op.drop_index('ix_classification_plans_id', table_name='classification_plans')
    op.drop_table('classification_plans')
    
    # 删除分类任务表
    op.drop_index('ix_classification_tasks_hospital_id', table_name='classification_tasks')
    op.drop_index('ix_classification_tasks_id', table_name='classification_tasks')
    op.drop_table('classification_tasks')
    
    # 删除AI配置表
    op.drop_index('ix_ai_configs_hospital_id', table_name='ai_configs')
    op.drop_index('ix_ai_configs_id', table_name='ai_configs')
    op.drop_table('ai_configs')
    
    # 删除枚举类型
    op.execute("DROP TYPE IF EXISTS progress_status")
    op.execute("DROP TYPE IF EXISTS processing_status")
    op.execute("DROP TYPE IF EXISTS plan_status")
    op.execute("DROP TYPE IF EXISTS task_status")
