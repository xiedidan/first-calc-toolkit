"""Add model_versions and model_nodes tables

Revision ID: g1h2i3j4k5l6
Revises: f0384ea4c792
Create Date: 2025-10-22 14:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'g1h2i3j4k5l6'
down_revision = 'a1b2c3d4e5f6'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 创建 model_versions 表
    op.create_table('model_versions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('version', sa.String(length=50), nullable=False, comment='版本号'),
        sa.Column('name', sa.String(length=100), nullable=False, comment='版本名称'),
        sa.Column('description', sa.Text(), nullable=True, comment='版本描述'),
        sa.Column('is_active', sa.Boolean(), nullable=False, comment='是否激活'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_model_versions_id'), 'model_versions', ['id'], unique=False)
    op.create_index(op.f('ix_model_versions_version'), 'model_versions', ['version'], unique=True)
    
    # 创建 model_nodes 表
    op.create_table('model_nodes',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('version_id', sa.Integer(), nullable=False, comment='模型版本ID'),
        sa.Column('parent_id', sa.Integer(), nullable=True, comment='父节点ID'),
        sa.Column('name', sa.String(length=100), nullable=False, comment='节点名称'),
        sa.Column('code', sa.String(length=50), nullable=False, comment='节点编码'),
        sa.Column('node_type', sa.String(length=20), nullable=False, comment='节点类型(sequence/dimension)'),
        sa.Column('calc_type', sa.String(length=20), nullable=True, comment='计算类型(statistical/calculational)'),
        sa.Column('weight', sa.Numeric(precision=10, scale=4), nullable=True, comment='权重/单价'),
        sa.Column('business_guide', sa.Text(), nullable=True, comment='业务导向'),
        sa.Column('script', sa.Text(), nullable=True, comment='SQL/Python脚本'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['version_id'], ['model_versions.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['parent_id'], ['model_nodes.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_model_nodes_id'), 'model_nodes', ['id'], unique=False)
    op.create_index(op.f('ix_model_nodes_version_id'), 'model_nodes', ['version_id'], unique=False)
    op.create_index(op.f('ix_model_nodes_parent_id'), 'model_nodes', ['parent_id'], unique=False)


def downgrade() -> None:
    # 删除 model_nodes 表
    op.drop_index(op.f('ix_model_nodes_parent_id'), table_name='model_nodes')
    op.drop_index(op.f('ix_model_nodes_version_id'), table_name='model_nodes')
    op.drop_index(op.f('ix_model_nodes_id'), table_name='model_nodes')
    op.drop_table('model_nodes')
    
    # 删除 model_versions 表
    op.drop_index(op.f('ix_model_versions_version'), table_name='model_versions')
    op.drop_index(op.f('ix_model_versions_id'), table_name='model_versions')
    op.drop_table('model_versions')
