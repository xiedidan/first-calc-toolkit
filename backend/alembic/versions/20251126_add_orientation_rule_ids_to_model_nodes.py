"""add orientation_rule_ids to model_nodes

Revision ID: 20251126_orientation_ids
Revises: 20251126_add_orientation_management
Create Date: 2025-11-26

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '20251126_orientation_ids'
down_revision = '20251126_orientation'
branch_labels = None
depends_on = None


def upgrade():
    # 添加新的数组字段
    op.add_column('model_nodes', sa.Column('orientation_rule_ids', postgresql.ARRAY(sa.Integer()), nullable=True, comment='关联导向规则ID列表'))
    
    # 迁移现有数据：将 orientation_rule_id 转换为 orientation_rule_ids 数组
    op.execute("""
        UPDATE model_nodes 
        SET orientation_rule_ids = ARRAY[orientation_rule_id]::integer[]
        WHERE orientation_rule_id IS NOT NULL
    """)
    
    # 可选：删除旧字段（如果确定不再需要）
    # op.drop_constraint('model_nodes_orientation_rule_id_fkey', 'model_nodes', type_='foreignkey')
    # op.drop_column('model_nodes', 'orientation_rule_id')


def downgrade():
    # 回滚：将数组的第一个元素恢复到单个ID字段
    op.execute("""
        UPDATE model_nodes 
        SET orientation_rule_id = orientation_rule_ids[1]
        WHERE orientation_rule_ids IS NOT NULL AND array_length(orientation_rule_ids, 1) > 0
    """)
    
    op.drop_column('model_nodes', 'orientation_rule_ids')
