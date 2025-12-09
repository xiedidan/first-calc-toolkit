"""add orientation values table

Revision ID: 20251127_add_orientation_values
Revises: 20251126_add_orientation_rule_ids_to_model_nodes
Create Date: 2025-11-27

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '20251127_add_orientation_values'
down_revision = '20251127_system_prompt'
branch_labels = None
depends_on = None


def upgrade():
    # 创建 orientation_values 表
    op.create_table(
        'orientation_values',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('hospital_id', sa.Integer(), nullable=False, comment='医疗机构ID'),
        sa.Column('year_month', sa.String(length=7), nullable=False, comment='年月(格式: YYYY-MM)'),
        sa.Column('department_code', sa.String(length=50), nullable=False, comment='科室代码'),
        sa.Column('department_name', sa.String(length=100), nullable=False, comment='科室名称'),
        sa.Column('orientation_rule_id', sa.Integer(), nullable=False, comment='导向规则ID'),
        sa.Column('actual_value', sa.Numeric(precision=15, scale=4), nullable=False, comment='导向实际取值'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    
    # 创建索引
    op.create_index('ix_orientation_values_hospital_id', 'orientation_values', ['hospital_id'])
    op.create_index('ix_orientation_values_orientation_rule_id', 'orientation_values', ['orientation_rule_id'])
    op.create_index('ix_orientation_values_year_month', 'orientation_values', ['year_month'])
    op.create_index('ix_orientation_values_department_code', 'orientation_values', ['department_code'])
    
    # 创建唯一约束：同一医院、同一年月、同一科室、同一导向规则只能有一条记录
    op.create_unique_constraint(
        'uq_orientation_values_hospital_yearmonth_dept_rule',
        'orientation_values',
        ['hospital_id', 'year_month', 'department_code', 'orientation_rule_id']
    )
    
    # 添加外键约束
    op.execute("""
        DO $$ BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM pg_constraint 
                WHERE conname = 'fk_orientation_values_hospital_id'
            ) THEN
                ALTER TABLE orientation_values 
                ADD CONSTRAINT fk_orientation_values_hospital_id 
                FOREIGN KEY (hospital_id) REFERENCES hospitals(id) ON DELETE CASCADE;
            END IF;
        END $$;
    """)
    
    op.execute("""
        DO $$ BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM pg_constraint 
                WHERE conname = 'fk_orientation_values_orientation_rule_id'
            ) THEN
                ALTER TABLE orientation_values 
                ADD CONSTRAINT fk_orientation_values_orientation_rule_id 
                FOREIGN KEY (orientation_rule_id) REFERENCES orientation_rules(id) ON DELETE CASCADE;
            END IF;
        END $$;
    """)


def downgrade():
    # 删除外键约束
    op.execute("""
        DO $$ BEGIN
            IF EXISTS (
                SELECT 1 FROM pg_constraint 
                WHERE conname = 'fk_orientation_values_orientation_rule_id'
            ) THEN
                ALTER TABLE orientation_values 
                DROP CONSTRAINT fk_orientation_values_orientation_rule_id;
            END IF;
        END $$;
    """)
    
    op.execute("""
        DO $$ BEGIN
            IF EXISTS (
                SELECT 1 FROM pg_constraint 
                WHERE conname = 'fk_orientation_values_hospital_id'
            ) THEN
                ALTER TABLE orientation_values 
                DROP CONSTRAINT fk_orientation_values_hospital_id;
            END IF;
        END $$;
    """)
    
    # 删除表
    op.drop_table('orientation_values')
