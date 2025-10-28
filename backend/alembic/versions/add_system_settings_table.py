"""add system_settings table

Revision ID: add_system_settings
Revises: l6m7n8o9p0q1
Create Date: 2025-10-28

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import func


# revision identifiers, used by Alembic.
revision = 'add_system_settings'
down_revision = 'l6m7n8o9p0q1'
branch_labels = None
depends_on = None


def upgrade():
    """升级数据库"""
    # 创建系统设置表
    op.create_table(
        'system_settings',
        sa.Column('id', sa.Integer(), nullable=False, comment='主键'),
        sa.Column('key', sa.String(length=100), nullable=False, comment='设置键'),
        sa.Column('value', sa.Text(), nullable=True, comment='设置值'),
        sa.Column('description', sa.Text(), nullable=True, comment='设置描述'),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=func.now(), nullable=False, comment='创建时间'),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=func.now(), nullable=False, comment='更新时间'),
        sa.PrimaryKeyConstraint('id'),
        comment='系统设置表'
    )
    
    # 创建索引
    op.create_index('ix_system_settings_id', 'system_settings', ['id'])
    op.create_index('ix_system_settings_key', 'system_settings', ['key'], unique=True)
    
    # 插入默认设置
    op.execute("""
        INSERT INTO system_settings (key, value, description, created_at, updated_at)
        VALUES 
            ('system_name', '医院科室业务价值评估工具', '系统名称', NOW(), NOW()),
            ('system_version', '1.0.0', '系统版本', NOW(), NOW())
    """)


def downgrade():
    """降级数据库"""
    # 删除索引
    op.drop_index('ix_system_settings_key', table_name='system_settings')
    op.drop_index('ix_system_settings_id', table_name='system_settings')
    
    # 删除表
    op.drop_table('system_settings')
