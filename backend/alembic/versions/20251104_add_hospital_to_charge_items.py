"""add hospital to charge items

Revision ID: 20251104_charge_items_hospital
Revises: 20251103_hospital
Create Date: 2025-11-04 16:20:42

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20251104_charge_items_hospital'
down_revision = '20251103_hospital'
branch_labels = None
depends_on = None


def upgrade():
    """添加医疗机构关联到收费项目"""
    
    conn = op.get_bind()
    
    # 1. 添加 hospital_id 列（允许为空，用于迁移）
    op.add_column('charge_items', sa.Column('hospital_id', sa.Integer(), nullable=True))
    
    # 2. 获取默认医疗机构ID（如果存在）
    result = conn.execute(sa.text("SELECT id FROM hospitals ORDER BY id LIMIT 1"))
    row = result.fetchone()
    
    if row:
        default_hospital_id = row[0]
        # 3. 将现有数据关联到默认医疗机构
        conn.execute(
            sa.text("UPDATE charge_items SET hospital_id = :hospital_id WHERE hospital_id IS NULL"),
            {"hospital_id": default_hospital_id}
        )
    
    # 4. 设置 hospital_id 为非空
    op.alter_column('charge_items', 'hospital_id', nullable=False)
    
    # 5. 删除旧的唯一约束（如果存在）
    # 先检查约束是否存在
    constraint_check = conn.execute(sa.text("""
        SELECT constraint_name 
        FROM information_schema.table_constraints 
        WHERE table_name = 'charge_items' 
        AND constraint_type = 'UNIQUE'
        AND constraint_name LIKE '%item_code%'
    """))
    
    for constraint in constraint_check:
        constraint_name = constraint[0]
        try:
            op.drop_constraint(constraint_name, 'charge_items', type_='unique')
        except Exception as e:
            print(f"Warning: Could not drop constraint {constraint_name}: {e}")
    
    # 6. 创建新的复合唯一约束
    op.create_unique_constraint('uq_hospital_item_code', 'charge_items', ['hospital_id', 'item_code'])
    
    # 7. 创建外键约束
    op.create_foreign_key(
        'fk_charge_items_hospital_id',
        'charge_items', 'hospitals',
        ['hospital_id'], ['id'],
        ondelete='CASCADE'
    )
    
    # 8. 创建索引
    op.create_index('ix_charge_items_hospital_id', 'charge_items', ['hospital_id'], unique=False)


def downgrade():
    """回滚医疗机构关联"""
    
    # 1. 删除索引
    op.drop_index('ix_charge_items_hospital_id', 'charge_items')
    
    # 2. 删除外键约束
    op.drop_constraint('fk_charge_items_hospital_id', 'charge_items', type_='foreignkey')
    
    # 3. 删除复合唯一约束
    op.drop_constraint('uq_hospital_item_code', 'charge_items', type_='unique')
    
    # 4. 恢复旧的唯一约束
    op.create_unique_constraint('charge_items_item_code_key', 'charge_items', ['item_code'])
    
    # 5. 删除 hospital_id 列
    op.drop_column('charge_items', 'hospital_id')
