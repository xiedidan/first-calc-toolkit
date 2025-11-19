"""add data templates table

Revision ID: 20251106_data_templates
Revises: 20251105_fix_unique_constraint
Create Date: 2025-11-06

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '20251106_data_templates'
down_revision = '20251106_mappings'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 创建 data_templates 表
    op.create_table(
        'data_templates',
        sa.Column('id', sa.Integer(), nullable=False, comment='主键'),
        sa.Column('hospital_id', sa.Integer(), nullable=False, comment='所属医疗机构ID'),
        sa.Column('table_name', sa.String(length=100), nullable=False, comment='表名'),
        sa.Column('table_name_cn', sa.String(length=200), nullable=False, comment='中文名'),
        sa.Column('description', sa.Text(), nullable=True, comment='表说明'),
        sa.Column('is_core', sa.Boolean(), nullable=False, server_default='false', comment='是否核心表'),
        sa.Column('sort_order', sa.Numeric(precision=10, scale=2), nullable=False, comment='排序序号'),
        sa.Column('definition_file_path', sa.Text(), nullable=True, comment='表定义文档存储路径'),
        sa.Column('definition_file_name', sa.String(length=255), nullable=True, comment='表定义文档原始文件名'),
        sa.Column('sql_file_path', sa.Text(), nullable=True, comment='SQL建表代码存储路径'),
        sa.Column('sql_file_name', sa.String(length=255), nullable=True, comment='SQL建表代码原始文件名'),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=False, comment='创建时间'),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=False, comment='更新时间'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('hospital_id', 'table_name', name='uq_hospital_table_name')
    )
    
    # 创建索引
    op.create_index(op.f('ix_data_templates_id'), 'data_templates', ['id'], unique=False)
    op.create_index(op.f('ix_data_templates_hospital_id'), 'data_templates', ['hospital_id'], unique=False)
    op.create_index(op.f('ix_data_templates_table_name'), 'data_templates', ['table_name'], unique=False)
    op.create_index(op.f('ix_data_templates_is_core'), 'data_templates', ['is_core'], unique=False)
    op.create_index('ix_data_templates_hospital_sort', 'data_templates', ['hospital_id', 'sort_order'], unique=False)
    
    # 创建外键约束
    op.create_foreign_key(
        'fk_data_templates_hospital_id',
        'data_templates', 'hospitals',
        ['hospital_id'], ['id'],
        ondelete='CASCADE'
    )


def downgrade() -> None:
    # 删除外键约束
    op.drop_constraint('fk_data_templates_hospital_id', 'data_templates', type_='foreignkey')
    
    # 删除索引
    op.drop_index('ix_data_templates_hospital_sort', table_name='data_templates')
    op.drop_index(op.f('ix_data_templates_is_core'), table_name='data_templates')
    op.drop_index(op.f('ix_data_templates_table_name'), table_name='data_templates')
    op.drop_index(op.f('ix_data_templates_hospital_id'), table_name='data_templates')
    op.drop_index(op.f('ix_data_templates_id'), table_name='data_templates')
    
    # 删除表
    op.drop_table('data_templates')
