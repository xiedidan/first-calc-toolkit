"""add data sources table

Revision ID: l6m7n8o9p0q1
Revises: calc_workflow_001
Create Date: 2025-10-28

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'l6m7n8o9p0q1'
down_revision = 'calc_workflow_001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 创建数据源表
    op.create_table(
        'data_sources',
        sa.Column('id', sa.Integer(), nullable=False, comment='主键'),
        sa.Column('name', sa.String(length=100), nullable=False, comment='数据源名称'),
        sa.Column('db_type', sa.String(length=20), nullable=False, comment='数据库类型'),
        sa.Column('host', sa.String(length=255), nullable=False, comment='主机地址'),
        sa.Column('port', sa.Integer(), nullable=False, comment='端口号'),
        sa.Column('database_name', sa.String(length=100), nullable=False, comment='数据库名称'),
        sa.Column('username', sa.String(length=100), nullable=False, comment='用户名'),
        sa.Column('password', sa.Text(), nullable=False, comment='密码（加密存储）'),
        sa.Column('schema_name', sa.String(length=100), nullable=True, comment='Schema名称'),
        sa.Column('connection_params', postgresql.JSON(astext_type=sa.Text()), nullable=True, comment='额外连接参数'),
        sa.Column('is_default', sa.Boolean(), nullable=False, server_default='false', comment='是否默认数据源'),
        sa.Column('is_enabled', sa.Boolean(), nullable=False, server_default='true', comment='是否启用'),
        sa.Column('description', sa.Text(), nullable=True, comment='描述'),
        sa.Column('pool_size_min', sa.Integer(), nullable=False, server_default='2', comment='连接池最小连接数'),
        sa.Column('pool_size_max', sa.Integer(), nullable=False, server_default='10', comment='连接池最大连接数'),
        sa.Column('pool_timeout', sa.Integer(), nullable=False, server_default='30', comment='连接超时时间(秒)'),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=False, comment='创建时间'),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=False, comment='更新时间'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
    op.create_index(op.f('ix_data_sources_id'), 'data_sources', ['id'], unique=False)
    
    # 在 calculation_steps 表中添加 data_source_id 字段
    op.add_column('calculation_steps', sa.Column('data_source_id', sa.Integer(), nullable=True, comment='数据源ID'))
    op.create_foreign_key(
        'fk_calculation_steps_data_source_id',
        'calculation_steps', 'data_sources',
        ['data_source_id'], ['id'],
        ondelete='SET NULL'
    )


def downgrade() -> None:
    # 删除 calculation_steps 表中的外键和字段
    op.drop_constraint('fk_calculation_steps_data_source_id', 'calculation_steps', type_='foreignkey')
    op.drop_column('calculation_steps', 'data_source_id')
    
    # 删除数据源表
    op.drop_index(op.f('ix_data_sources_id'), table_name='data_sources')
    op.drop_table('data_sources')
