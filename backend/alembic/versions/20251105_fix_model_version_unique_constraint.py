"""Fix model_version unique constraint to be per hospital

Revision ID: 20251105_fix_unique
Revises: 20251105_imports
Create Date: 2025-11-05 15:30:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20251105_fix_unique'
down_revision = '20251105_imports'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 使用原始SQL来检查和处理约束
    from sqlalchemy import text
    conn = op.get_bind()
    
    # 检查旧的唯一索引是否存在
    result = conn.execute(text("""
        SELECT indexname FROM pg_indexes 
        WHERE tablename = 'model_versions' 
        AND indexname = 'ix_model_versions_version'
    """))
    index_exists = result.fetchone() is not None
    
    if index_exists:
        # 检查索引是否是唯一的
        result = conn.execute(text("""
            SELECT i.indisunique
            FROM pg_class c
            JOIN pg_index i ON i.indexrelid = c.oid
            WHERE c.relname = 'ix_model_versions_version'
        """))
        row = result.fetchone()
        is_unique = row[0] if row else False
        
        if is_unique:
            # 删除旧的唯一索引
            op.drop_index('ix_model_versions_version', table_name='model_versions')
            # 创建新的非唯一索引
            op.create_index('ix_model_versions_version', 'model_versions', ['version'], unique=False)
    
    # 检查复合唯一约束是否已存在
    result = conn.execute(text("""
        SELECT conname FROM pg_constraint 
        WHERE conname = 'uq_model_versions_hospital_version'
        AND conrelid = 'model_versions'::regclass
    """))
    constraint_exists = result.fetchone() is not None
    
    if not constraint_exists:
        # 创建复合唯一约束（hospital_id + version）
        op.create_unique_constraint(
            'uq_model_versions_hospital_version',
            'model_versions',
            ['hospital_id', 'version']
        )


def downgrade() -> None:
    # 删除复合唯一约束
    op.drop_constraint('uq_model_versions_hospital_version', 'model_versions', type_='unique')
    
    # 删除非唯一索引
    op.drop_index('ix_model_versions_version', table_name='model_versions')
    
    # 恢复旧的唯一索引
    op.create_index('ix_model_versions_version', 'model_versions', ['version'], unique=True)
