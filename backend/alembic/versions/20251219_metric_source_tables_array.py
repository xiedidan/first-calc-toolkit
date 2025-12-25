"""metric source_tables array

Revision ID: 20251219_source_tables
Revises: 20251217_intelligent_query
Create Date: 2024-12-19

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '20251219_source_tables'
down_revision = '20251217_intelligent_query'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. 添加新的 source_tables 列（JSONB 类型）
    op.add_column('metrics', sa.Column('source_tables', postgresql.JSONB(), nullable=True, comment='源表列表'))
    
    # 2. 迁移旧数据：将 source_table 字符串转换为数组
    op.execute("""
        UPDATE metrics 
        SET source_tables = CASE 
            WHEN source_table IS NOT NULL AND source_table != '' 
            THEN jsonb_build_array(source_table)
            ELSE NULL 
        END
    """)
    
    # 3. 删除旧的 source_table 列
    op.drop_column('metrics', 'source_table')


def downgrade() -> None:
    # 1. 添加旧的 source_table 列
    op.add_column('metrics', sa.Column('source_table', sa.String(200), nullable=True, comment='源表'))
    
    # 2. 迁移数据：取数组的第一个元素
    op.execute("""
        UPDATE metrics 
        SET source_table = source_tables->>0
        WHERE source_tables IS NOT NULL AND jsonb_array_length(source_tables) > 0
    """)
    
    # 3. 删除新的 source_tables 列
    op.drop_column('metrics', 'source_tables')
