"""
用户角色权限系统升级

- Role表增加role_type枚举字段和menu_permissions JSON字段
- User表增加department_id字段

Revision ID: 20251203_role_perm
Revises: 20251202_refval
Create Date: 2025-12-03
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '20251203_role_perm'
down_revision = '20251128_add_original_weight'
branch_labels = None
depends_on = None


def upgrade():
    # 创建角色类型枚举
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE role_type AS ENUM ('department_user', 'hospital_user', 'admin', 'maintainer');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)
    
    # Role表增加字段
    op.add_column('roles', sa.Column('role_type', sa.Enum('department_user', 'hospital_user', 'admin', 'maintainer', name='role_type'), nullable=True, comment='角色类型'))
    op.add_column('roles', sa.Column('menu_permissions', postgresql.JSON(astext_type=sa.Text()), nullable=True, comment='菜单权限列表'))
    
    # User表增加department_id字段
    op.add_column('users', sa.Column('department_id', sa.Integer(), nullable=True, comment='所属科室ID'))
    op.create_foreign_key('fk_users_department_id', 'users', 'departments', ['department_id'], ['id'], ondelete='SET NULL')
    op.create_index('ix_users_department_id', 'users', ['department_id'])
    
    # 更新现有角色的role_type
    op.execute("""
        UPDATE roles SET role_type = 'admin' WHERE code = 'admin';
        UPDATE roles SET role_type = 'hospital_user' WHERE code = 'user';
        UPDATE roles SET role_type = 'maintainer' WHERE code = 'maintainer';
        -- 其他未匹配的角色默认设为hospital_user
        UPDATE roles SET role_type = 'hospital_user' WHERE role_type IS NULL;
    """)
    
    # 设置role_type为非空
    op.alter_column('roles', 'role_type', nullable=False)
    
    # 添加字段注释
    op.execute("COMMENT ON COLUMN roles.role_type IS '角色类型：department_user-科室用户, hospital_user-全院用户, admin-管理员, maintainer-维护者'")
    op.execute("COMMENT ON COLUMN roles.menu_permissions IS '菜单权限列表，JSON数组格式'")
    op.execute("COMMENT ON COLUMN users.department_id IS '所属科室ID，科室用户必填'")
    
    # 创建维护者角色（如果不存在）
    op.execute("""
        INSERT INTO roles (name, code, role_type, description, created_at, updated_at)
        SELECT '系统维护者', 'maintainer', 'maintainer', '系统最高权限，可管理所有用户和AI接口', NOW(), NOW()
        WHERE NOT EXISTS (SELECT 1 FROM roles WHERE code = 'maintainer');
    """)


def downgrade():
    # 删除维护者角色
    op.execute("DELETE FROM roles WHERE code = 'maintainer'")
    
    # 删除User表的department_id字段
    op.drop_index('ix_users_department_id', table_name='users')
    op.drop_constraint('fk_users_department_id', 'users', type_='foreignkey')
    op.drop_column('users', 'department_id')
    
    # 删除Role表的新字段
    op.drop_column('roles', 'menu_permissions')
    op.drop_column('roles', 'role_type')
    
    # 删除枚举类型
    op.execute("DROP TYPE IF EXISTS role_type")
