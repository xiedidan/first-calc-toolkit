"""add model version imports

Revision ID: 20251105_imports
Revises: 20251104_charge_items
Create Date: 2025-11-05

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '20251105_imports'
down_revision = '20251104_charge_items_hospital'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 创建 model_version_imports 表
    op.create_table(
        'model_version_imports',
        sa.Column('id', sa.Integer(), nullable=False, comment='主键'),
        sa.Column('target_version_id', sa.Integer(), nullable=False, comment='目标版本ID（导入后创建的新版本）'),
        sa.Column('source_version_id', sa.Integer(), nullable=False, comment='源版本ID'),
        sa.Column('source_hospital_id', sa.Integer(), nullable=False, comment='源医疗机构ID'),
        sa.Column('import_type', sa.String(length=50), nullable=False, comment='导入类型（structure_only/with_workflows）'),
        sa.Column('imported_by', sa.Integer(), nullable=False, comment='导入用户ID'),
        sa.Column('import_time', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=False, comment='导入时间'),
        sa.Column('statistics', postgresql.JSONB(astext_type=sa.Text()), nullable=True, comment='导入统计信息（JSON格式）'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # 创建索引
    op.create_index(op.f('ix_model_version_imports_id'), 'model_version_imports', ['id'], unique=False)
    op.create_index(op.f('ix_model_version_imports_target_version_id'), 'model_version_imports', ['target_version_id'], unique=False)
    op.create_index(op.f('ix_model_version_imports_source_version_id'), 'model_version_imports', ['source_version_id'], unique=False)
    
    # 创建外键约束
    op.create_foreign_key(
        'fk_model_version_imports_target_version_id',
        'model_version_imports', 'model_versions',
        ['target_version_id'], ['id'],
        ondelete='CASCADE'
    )
    op.create_foreign_key(
        'fk_model_version_imports_source_version_id',
        'model_version_imports', 'model_versions',
        ['source_version_id'], ['id'],
        ondelete='CASCADE'
    )
    op.create_foreign_key(
        'fk_model_version_imports_source_hospital_id',
        'model_version_imports', 'hospitals',
        ['source_hospital_id'], ['id'],
        ondelete='CASCADE'
    )
    op.create_foreign_key(
        'fk_model_version_imports_imported_by',
        'model_version_imports', 'users',
        ['imported_by'], ['id'],
        ondelete='CASCADE'
    )


def downgrade() -> None:
    # 删除外键约束
    op.drop_constraint('fk_model_version_imports_imported_by', 'model_version_imports', type_='foreignkey')
    op.drop_constraint('fk_model_version_imports_source_hospital_id', 'model_version_imports', type_='foreignkey')
    op.drop_constraint('fk_model_version_imports_source_version_id', 'model_version_imports', type_='foreignkey')
    op.drop_constraint('fk_model_version_imports_target_version_id', 'model_version_imports', type_='foreignkey')
    
    # 删除索引
    op.drop_index(op.f('ix_model_version_imports_source_version_id'), table_name='model_version_imports')
    op.drop_index(op.f('ix_model_version_imports_target_version_id'), table_name='model_version_imports')
    op.drop_index(op.f('ix_model_version_imports_id'), table_name='model_version_imports')
    
    # 删除表
    op.drop_table('model_version_imports')
