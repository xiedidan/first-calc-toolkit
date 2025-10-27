"""change dimension_id to dimension_code

Revision ID: change_dim_to_code
Revises: g1h2i3j4k5l6
Create Date: 2025-10-24

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'change_dim_to_code'
down_revision = 'k5l6m7n8o9p0'
branch_labels = None
depends_on = None


def upgrade():
    """
    将 dimension_item_mappings 表的 dimension_id 改为 dimension_code
    """
    # 1. 添加新列 dimension_code
    op.add_column('dimension_item_mappings', 
                  sa.Column('dimension_code', sa.String(100), nullable=True, comment='维度节点编码'))
    
    # 2. 迁移数据：从 model_nodes 表获取 code 并填充到 dimension_code
    # PostgreSQL语法
    op.execute("""
        UPDATE dimension_item_mappings
        SET dimension_code = mn.code
        FROM model_nodes mn
        WHERE dimension_item_mappings.dimension_id = mn.id
    """)
    
    # 3. 将 dimension_code 设置为 NOT NULL
    op.alter_column('dimension_item_mappings', 'dimension_code',
                    existing_type=sa.String(100),
                    nullable=False)
    
    # 4. 添加索引
    op.create_index('ix_dimension_item_mappings_dimension_code', 
                    'dimension_item_mappings', ['dimension_code'])
    
    # 5. 删除旧列的索引
    op.drop_index('ix_dimension_item_mappings_dimension_id', 
                  table_name='dimension_item_mappings')
    
    # 6. 删除旧列 dimension_id
    op.drop_column('dimension_item_mappings', 'dimension_id')


def downgrade():
    """
    回滚：将 dimension_code 改回 dimension_id
    """
    # 1. 添加回 dimension_id 列
    op.add_column('dimension_item_mappings',
                  sa.Column('dimension_id', sa.Integer(), nullable=True, comment='维度节点ID'))
    
    # 2. 迁移数据：从 model_nodes 表获取 id 并填充到 dimension_id
    # PostgreSQL语法
    op.execute("""
        UPDATE dimension_item_mappings
        SET dimension_id = mn.id
        FROM model_nodes mn
        WHERE dimension_item_mappings.dimension_code = mn.code
    """)
    
    # 3. 将 dimension_id 设置为 NOT NULL
    op.alter_column('dimension_item_mappings', 'dimension_id',
                    existing_type=sa.Integer(),
                    nullable=False)
    
    # 4. 添加索引
    op.create_index('ix_dimension_item_mappings_dimension_id',
                    'dimension_item_mappings', ['dimension_id'])
    
    # 5. 删除 dimension_code 的索引
    op.drop_index('ix_dimension_item_mappings_dimension_code',
                  table_name='dimension_item_mappings')
    
    # 6. 删除 dimension_code 列
    op.drop_column('dimension_item_mappings', 'dimension_code')
