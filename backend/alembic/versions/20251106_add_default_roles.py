"""Add default roles (admin and user)

Revision ID: 20251106_add_default_roles
Revises: 20251106_add_data_templates_table
Create Date: 2025-11-06 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime


# revision identifiers, used by Alembic.
revision = '20251106_add_default_roles'
down_revision = '20251106_data_templates'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 插入默认角色
    roles_table = sa.table('roles',
        sa.column('name', sa.String),
        sa.column('code', sa.String),
        sa.column('description', sa.Text),
        sa.column('created_at', sa.DateTime),
        sa.column('updated_at', sa.DateTime)
    )
    
    now = datetime.utcnow()
    
    # 检查是否已存在角色，如果不存在则插入
    conn = op.get_bind()
    
    # 检查admin角色
    result = conn.execute(sa.text("SELECT COUNT(*) FROM roles WHERE code = 'admin'"))
    if result.scalar() == 0:
        op.bulk_insert(roles_table, [
            {
                'name': '管理员',
                'code': 'admin',
                'description': '系统管理员，可访问所有医疗机构和功能',
                'created_at': now,
                'updated_at': now
            }
        ])
    
    # 检查user角色
    result = conn.execute(sa.text("SELECT COUNT(*) FROM roles WHERE code = 'user'"))
    if result.scalar() == 0:
        op.bulk_insert(roles_table, [
            {
                'name': '普通用户',
                'code': 'user',
                'description': '普通用户，只能访问所属医疗机构的数据',
                'created_at': now,
                'updated_at': now
            }
        ])


def downgrade() -> None:
    # 删除默认角色
    op.execute("DELETE FROM roles WHERE code IN ('admin', 'user')")
