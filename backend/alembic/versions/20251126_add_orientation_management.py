"""add orientation management tables

Revision ID: 20251126_orientation
Revises: l6m7n8o9p0q1
Create Date: 2025-11-26

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '20251126_orientation'
down_revision = 'm7n8o9p0q1r2'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 创建枚举类型：导向类别
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE orientation_category AS ENUM ('benchmark_ladder', 'direct_ladder', 'other');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)
    
    # 创建枚举类型：基准类别
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE benchmark_type AS ENUM ('average', 'median', 'max', 'min', 'other');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)
    
    # 创建导向规则表
    op.create_table(
        'orientation_rules',
        sa.Column('id', sa.Integer(), nullable=False, comment='主键'),
        sa.Column('hospital_id', sa.Integer(), nullable=False, comment='医疗机构ID'),
        sa.Column('name', sa.String(length=100), nullable=False, comment='导向名称'),
        sa.Column('category', postgresql.ENUM('benchmark_ladder', 'direct_ladder', 'other', name='orientation_category', create_type=False), nullable=False, comment='导向类别'),
        sa.Column('description', sa.String(length=1024), nullable=True, comment='导向规则描述'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False, comment='创建时间'),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False, comment='更新时间'),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['hospital_id'], ['hospitals.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('hospital_id', 'name', name='uq_orientation_rule_name')
    )
    op.create_index('ix_orientation_rules_id', 'orientation_rules', ['id'], unique=False)
    op.create_index('ix_orientation_rules_hospital_id', 'orientation_rules', ['hospital_id'], unique=False)
    
    # 添加表注释
    op.execute("COMMENT ON TABLE orientation_rules IS '导向规则表'")

    # 创建导向基准表
    op.create_table(
        'orientation_benchmarks',
        sa.Column('id', sa.Integer(), nullable=False, comment='主键'),
        sa.Column('hospital_id', sa.Integer(), nullable=False, comment='医疗机构ID'),
        sa.Column('rule_id', sa.Integer(), nullable=False, comment='导向规则ID'),
        sa.Column('department_code', sa.String(length=50), nullable=False, comment='科室代码'),
        sa.Column('department_name', sa.String(length=100), nullable=False, comment='科室名称'),
        sa.Column('benchmark_type', postgresql.ENUM('average', 'median', 'max', 'min', 'other', name='benchmark_type', create_type=False), nullable=False, comment='基准类别'),
        sa.Column('control_intensity', sa.Numeric(precision=10, scale=4), nullable=False, comment='管控力度'),
        sa.Column('stat_start_date', sa.DateTime(), nullable=False, comment='统计开始时间'),
        sa.Column('stat_end_date', sa.DateTime(), nullable=False, comment='统计结束时间'),
        sa.Column('benchmark_value', sa.Numeric(precision=10, scale=4), nullable=False, comment='基准值'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False, comment='创建时间'),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False, comment='更新时间'),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['hospital_id'], ['hospitals.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['rule_id'], ['orientation_rules.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('hospital_id', 'rule_id', 'department_code', name='uq_benchmark_dept')
    )
    op.create_index('ix_orientation_benchmarks_id', 'orientation_benchmarks', ['id'], unique=False)
    op.create_index('ix_orientation_benchmarks_hospital_id', 'orientation_benchmarks', ['hospital_id'], unique=False)
    op.create_index('ix_orientation_benchmarks_rule_id', 'orientation_benchmarks', ['rule_id'], unique=False)
    
    # 添加表注释
    op.execute("COMMENT ON TABLE orientation_benchmarks IS '导向基准表'")
    
    # 创建导向阶梯表
    op.create_table(
        'orientation_ladders',
        sa.Column('id', sa.Integer(), nullable=False, comment='主键'),
        sa.Column('hospital_id', sa.Integer(), nullable=False, comment='医疗机构ID'),
        sa.Column('rule_id', sa.Integer(), nullable=False, comment='导向规则ID'),
        sa.Column('ladder_order', sa.Integer(), nullable=False, comment='阶梯次序'),
        sa.Column('upper_limit', sa.Numeric(precision=10, scale=4), nullable=True, comment='阶梯上限（NULL表示正无穷）'),
        sa.Column('lower_limit', sa.Numeric(precision=10, scale=4), nullable=True, comment='阶梯下限（NULL表示负无穷）'),
        sa.Column('adjustment_intensity', sa.Numeric(precision=10, scale=4), nullable=False, comment='调整力度'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False, comment='创建时间'),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False, comment='更新时间'),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['hospital_id'], ['hospitals.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['rule_id'], ['orientation_rules.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('hospital_id', 'rule_id', 'ladder_order', name='uq_ladder_order')
    )
    op.create_index('ix_orientation_ladders_id', 'orientation_ladders', ['id'], unique=False)
    op.create_index('ix_orientation_ladders_hospital_id', 'orientation_ladders', ['hospital_id'], unique=False)
    op.create_index('ix_orientation_ladders_rule_id', 'orientation_ladders', ['rule_id'], unique=False)
    
    # 添加表注释
    op.execute("COMMENT ON TABLE orientation_ladders IS '导向阶梯表'")
    
    # 为 model_nodes 表添加 orientation_rule_id 外键字段
    op.add_column('model_nodes', sa.Column('orientation_rule_id', sa.Integer(), nullable=True, comment='关联导向规则ID'))
    
    # 添加外键约束（使用 DO 块检查是否已存在）
    op.execute("""
        DO $$ BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'fk_model_nodes_orientation_rule_id') THEN
                ALTER TABLE model_nodes ADD CONSTRAINT fk_model_nodes_orientation_rule_id 
                    FOREIGN KEY (orientation_rule_id) REFERENCES orientation_rules(id) ON DELETE SET NULL;
            END IF;
        END $$;
    """)
    
    # 添加字段注释
    op.execute("COMMENT ON COLUMN model_nodes.orientation_rule_id IS '关联导向规则ID'")


def downgrade() -> None:
    # 删除 model_nodes 表中的外键和字段
    op.execute("""
        DO $$ BEGIN
            IF EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'fk_model_nodes_orientation_rule_id') THEN
                ALTER TABLE model_nodes DROP CONSTRAINT fk_model_nodes_orientation_rule_id;
            END IF;
        END $$;
    """)
    op.drop_column('model_nodes', 'orientation_rule_id')
    
    # 删除导向阶梯表
    op.drop_index('ix_orientation_ladders_rule_id', table_name='orientation_ladders')
    op.drop_index('ix_orientation_ladders_hospital_id', table_name='orientation_ladders')
    op.drop_index('ix_orientation_ladders_id', table_name='orientation_ladders')
    op.drop_table('orientation_ladders')
    
    # 删除导向基准表
    op.drop_index('ix_orientation_benchmarks_rule_id', table_name='orientation_benchmarks')
    op.drop_index('ix_orientation_benchmarks_hospital_id', table_name='orientation_benchmarks')
    op.drop_index('ix_orientation_benchmarks_id', table_name='orientation_benchmarks')
    op.drop_table('orientation_benchmarks')
    
    # 删除导向规则表
    op.drop_index('ix_orientation_rules_hospital_id', table_name='orientation_rules')
    op.drop_index('ix_orientation_rules_id', table_name='orientation_rules')
    op.drop_table('orientation_rules')
    
    # 删除枚举类型
    op.execute("DROP TYPE IF EXISTS benchmark_type")
    op.execute("DROP TYPE IF EXISTS orientation_category")
