"""add data_source_id and python_env to calculation_steps

Revision ID: add_datasource_steps
Revises: l6m7n8o9p0q1
Create Date: 2025-10-28 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'add_datasource_steps'
down_revision = 'add_system_settings'
branch_labels = None
depends_on = None


def upgrade():
    # 检查列是否已存在，如果不存在才添加
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    columns = [col['name'] for col in inspector.get_columns('calculation_steps')]
    
    # 添加 data_source_id 字段（用于 SQL 步骤）
    if 'data_source_id' not in columns:
        op.add_column('calculation_steps', 
            sa.Column('data_source_id', sa.Integer(), nullable=True, comment='数据源ID（SQL步骤使用）')
        )
    
    # 添加 python_env 字段（用于 Python 步骤）
    if 'python_env' not in columns:
        op.add_column('calculation_steps',
            sa.Column('python_env', sa.String(length=200), nullable=True, comment='Python虚拟环境路径（Python步骤使用）')
        )
    
    # 检查外键是否已存在
    foreign_keys = [fk['name'] for fk in inspector.get_foreign_keys('calculation_steps')]
    if 'fk_calculation_steps_data_source_id' not in foreign_keys:
        # 添加外键约束
        op.create_foreign_key(
            'fk_calculation_steps_data_source_id',
            'calculation_steps', 'data_sources',
            ['data_source_id'], ['id'],
            ondelete='SET NULL'
        )
    
    # 检查索引是否已存在
    indexes = [idx['name'] for idx in inspector.get_indexes('calculation_steps')]
    if 'ix_calculation_steps_data_source_id' not in indexes:
        # 创建索引
        op.create_index('ix_calculation_steps_data_source_id', 'calculation_steps', ['data_source_id'])


def downgrade():
    # 删除索引
    op.drop_index('ix_calculation_steps_data_source_id', table_name='calculation_steps')
    
    # 删除外键约束
    op.drop_constraint('fk_calculation_steps_data_source_id', 'calculation_steps', type_='foreignkey')
    
    # 删除字段
    op.drop_column('calculation_steps', 'python_env')
    op.drop_column('calculation_steps', 'data_source_id')
