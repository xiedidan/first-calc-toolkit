"""add hospital management

Revision ID: 20251103_hospital
Revises: 20251029_225500
Create Date: 2025-11-03

"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime

# revision identifiers, used by Alembic.
revision = '20251103_hospital'
down_revision = '20251029_225500'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. 创建医疗机构表
    op.create_table(
        'hospitals',
        sa.Column('id', sa.Integer(), nullable=False, comment='主键'),
        sa.Column('code', sa.String(length=50), nullable=False, comment='医疗机构编码'),
        sa.Column('name', sa.String(length=200), nullable=False, comment='医疗机构名称'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true', comment='是否启用'),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=False, comment='创建时间'),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=False, comment='更新时间'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('code')
    )
    op.create_index(op.f('ix_hospitals_id'), 'hospitals', ['id'], unique=False)
    op.create_index(op.f('ix_hospitals_code'), 'hospitals', ['code'], unique=True)
    
    # 2. 插入默认医疗机构"宁波市眼科医院"
    op.execute("""
        INSERT INTO hospitals (code, name, is_active, created_at, updated_at)
        VALUES ('nbeye', '宁波市眼科医院', true, now(), now())
    """)
    
    # 3. 在 users 表添加 hospital_id 字段
    op.add_column('users', sa.Column('hospital_id', sa.Integer(), nullable=True, comment='所属医疗机构ID，NULL表示超级用户'))
    op.create_index(op.f('ix_users_hospital_id'), 'users', ['hospital_id'], unique=False)
    op.create_foreign_key(
        'fk_users_hospital_id',
        'users', 'hospitals',
        ['hospital_id'], ['id'],
        ondelete='SET NULL'
    )
    
    # 4. 在 departments 表添加 hospital_id 字段
    # 先添加字段为可空
    op.add_column('departments', sa.Column('hospital_id', sa.Integer(), nullable=True, comment='所属医疗机构ID'))
    
    # 更新现有数据关联到默认医疗机构
    op.execute("""
        UPDATE departments
        SET hospital_id = (SELECT id FROM hospitals WHERE code = 'nbeye')
        WHERE hospital_id IS NULL
    """)
    
    # 将字段改为非空
    op.alter_column('departments', 'hospital_id', nullable=False)
    op.create_index(op.f('ix_departments_hospital_id'), 'departments', ['hospital_id'], unique=False)
    op.create_foreign_key(
        'fk_departments_hospital_id',
        'departments', 'hospitals',
        ['hospital_id'], ['id'],
        ondelete='CASCADE'
    )
    
    # 修改 his_code 的唯一约束，改为与 hospital_id 组合唯一
    # 先检查约束是否存在，如果存在则删除
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    constraints = inspector.get_unique_constraints('departments')
    
    # 查找 his_code 相关的唯一约束
    his_code_constraint = None
    for constraint in constraints:
        if 'his_code' in constraint['column_names']:
            his_code_constraint = constraint['name']
            break
    
    if his_code_constraint:
        op.drop_constraint(his_code_constraint, 'departments', type_='unique')
    
    op.create_unique_constraint('uq_departments_hospital_his_code', 'departments', ['hospital_id', 'his_code'])
    
    # 5. 在 model_versions 表添加 hospital_id 字段
    # 先添加字段为可空
    op.add_column('model_versions', sa.Column('hospital_id', sa.Integer(), nullable=True, comment='所属医疗机构ID'))
    
    # 更新现有数据关联到默认医疗机构
    op.execute("""
        UPDATE model_versions
        SET hospital_id = (SELECT id FROM hospitals WHERE code = 'nbeye')
        WHERE hospital_id IS NULL
    """)
    
    # 将字段改为非空
    op.alter_column('model_versions', 'hospital_id', nullable=False)
    op.create_index(op.f('ix_model_versions_hospital_id'), 'model_versions', ['hospital_id'], unique=False)
    op.create_foreign_key(
        'fk_model_versions_hospital_id',
        'model_versions', 'hospitals',
        ['hospital_id'], ['id'],
        ondelete='CASCADE'
    )
    
    # 修改 version 的唯一约束，改为与 hospital_id 组合唯一
    # 先检查约束是否存在，如果存在则删除
    constraints = inspector.get_unique_constraints('model_versions')
    
    # 查找 version 相关的唯一约束
    version_constraint = None
    for constraint in constraints:
        if 'version' in constraint['column_names']:
            version_constraint = constraint['name']
            break
    
    if version_constraint:
        op.drop_constraint(version_constraint, 'model_versions', type_='unique')
    
    op.create_unique_constraint('uq_model_versions_hospital_version', 'model_versions', ['hospital_id', 'version'])
    
    # 6. 在 dimension_item_mappings 表添加 hospital_id 字段
    # 先添加字段为可空
    op.add_column('dimension_item_mappings', sa.Column('hospital_id', sa.Integer(), nullable=True, comment='所属医疗机构ID'))
    
    # 更新现有数据关联到默认医疗机构
    op.execute("""
        UPDATE dimension_item_mappings
        SET hospital_id = (SELECT id FROM hospitals WHERE code = 'nbeye')
        WHERE hospital_id IS NULL
    """)
    
    # 将字段改为非空
    op.alter_column('dimension_item_mappings', 'hospital_id', nullable=False)
    op.create_index(op.f('ix_dimension_item_mappings_hospital_id'), 'dimension_item_mappings', ['hospital_id'], unique=False)
    op.create_foreign_key(
        'fk_dimension_item_mappings_hospital_id',
        'dimension_item_mappings', 'hospitals',
        ['hospital_id'], ['id'],
        ondelete='CASCADE'
    )


def downgrade() -> None:
    # 6. 恢复 dimension_item_mappings 表
    op.drop_constraint('fk_dimension_item_mappings_hospital_id', 'dimension_item_mappings', type_='foreignkey')
    op.drop_index(op.f('ix_dimension_item_mappings_hospital_id'), table_name='dimension_item_mappings')
    op.drop_column('dimension_item_mappings', 'hospital_id')
    
    # 5. 恢复 model_versions 表
    op.drop_constraint('uq_model_versions_hospital_version', 'model_versions', type_='unique')
    # 恢复 version 的唯一约束（如果原来存在的话）
    # op.create_unique_constraint('model_versions_version_key', 'model_versions', ['version'])
    op.drop_constraint('fk_model_versions_hospital_id', 'model_versions', type_='foreignkey')
    op.drop_index(op.f('ix_model_versions_hospital_id'), table_name='model_versions')
    op.drop_column('model_versions', 'hospital_id')
    
    # 4. 恢复 departments 表
    op.drop_constraint('uq_departments_hospital_his_code', 'departments', type_='unique')
    # 恢复 his_code 的唯一约束（如果原来存在的话）
    # op.create_unique_constraint('departments_his_code_key', 'departments', ['his_code'])
    op.drop_constraint('fk_departments_hospital_id', 'departments', type_='foreignkey')
    op.drop_index(op.f('ix_departments_hospital_id'), table_name='departments')
    op.drop_column('departments', 'hospital_id')
    
    # 3. 恢复 users 表
    op.drop_constraint('fk_users_hospital_id', 'users', type_='foreignkey')
    op.drop_index(op.f('ix_users_hospital_id'), table_name='users')
    op.drop_column('users', 'hospital_id')
    
    # 1. 删除医疗机构表
    op.drop_index(op.f('ix_hospitals_code'), table_name='hospitals')
    op.drop_index(op.f('ix_hospitals_id'), table_name='hospitals')
    op.drop_table('hospitals')
