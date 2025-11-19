"""Add charge_item_id to dimension_item_mappings

Revision ID: 20251106_mappings
Revises: 20251105_fix_unique
Create Date: 2025-11-06 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20251106_mappings'
down_revision = '20251105_fix_unique'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """添加 charge_item_id 字段到 dimension_item_mappings 表"""
    
    # 1. 添加 charge_item_id 字段（可空）
    op.add_column('dimension_item_mappings', 
                  sa.Column('charge_item_id', sa.Integer(), nullable=True, comment='收费项目ID'))
    
    # 2. 创建索引
    op.create_index(op.f('ix_dimension_item_mappings_charge_item_id'), 
                    'dimension_item_mappings', ['charge_item_id'], unique=False)
    
    # 3. 添加外键约束
    op.create_foreign_key(
        'fk_dimension_item_mappings_charge_item_id',
        'dimension_item_mappings', 'charge_items',
        ['charge_item_id'], ['id'],
        ondelete='CASCADE'
    )
    
    # 4. 尝试关联现有数据（通过 hospital_id 和 item_code 匹配）
    op.execute("""
        UPDATE dimension_item_mappings dim
        SET charge_item_id = ci.id
        FROM charge_items ci
        WHERE dim.hospital_id = ci.hospital_id
        AND dim.item_code = ci.item_code
        AND dim.charge_item_id IS NULL
    """)


def downgrade() -> None:
    """移除 charge_item_id 字段"""
    
    # 1. 删除外键约束
    op.drop_constraint('fk_dimension_item_mappings_charge_item_id', 
                       'dimension_item_mappings', type_='foreignkey')
    
    # 2. 删除索引
    op.drop_index(op.f('ix_dimension_item_mappings_charge_item_id'), 
                  table_name='dimension_item_mappings')
    
    # 3. 删除字段
    op.drop_column('dimension_item_mappings', 'charge_item_id')
