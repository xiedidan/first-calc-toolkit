"""add orientation adjustment details table

Revision ID: 20251128_add_orientation_adjustment_details
Revises: 20251128_add_cost_values
Create Date: 2025-11-28

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '20251128_orientation_details'
down_revision = '20251128_add_cost_values'
branch_labels = None
depends_on = None


def upgrade():
    # 创建业务导向调整明细表
    op.create_table(
        'orientation_adjustment_details',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('task_id', sa.String(50), nullable=False, comment='计算任务ID'),
        sa.Column('hospital_id', sa.Integer(), nullable=False, comment='医疗机构ID'),
        sa.Column('year_month', sa.String(7), nullable=False, comment='计算年月(格式: YYYY-MM)'),
        
        # 科室信息
        sa.Column('department_id', sa.Integer(), nullable=False, comment='科室ID'),
        sa.Column('department_code', sa.String(50), nullable=False, comment='科室代码'),
        sa.Column('department_name', sa.String(100), nullable=False, comment='科室名称'),
        
        # 维度信息
        sa.Column('node_id', sa.Integer(), nullable=False, comment='模型节点ID'),
        sa.Column('node_code', sa.String(50), nullable=False, comment='维度代码'),
        sa.Column('node_name', sa.String(200), nullable=False, comment='维度名称'),
        
        # 导向规则信息
        sa.Column('orientation_rule_id', sa.Integer(), nullable=False, comment='导向规则ID'),
        sa.Column('orientation_rule_name', sa.String(100), nullable=False, comment='导向规则名称'),
        sa.Column('orientation_type', sa.String(20), nullable=False, comment='导向类型: benchmark_ladder/fixed_benchmark'),
        
        # 计算过程 - 输入值
        sa.Column('actual_value', sa.Numeric(15, 4), nullable=True, comment='导向实际值'),
        sa.Column('benchmark_value', sa.Numeric(15, 4), nullable=True, comment='导向基准值'),
        
        # 计算过程 - 中间结果
        sa.Column('orientation_ratio', sa.Numeric(10, 6), nullable=True, comment='导向比例 = 实际值/基准值'),
        
        # 计算过程 - 阶梯匹配（仅基准阶梯型）
        sa.Column('ladder_id', sa.Integer(), nullable=True, comment='匹配的阶梯ID'),
        sa.Column('ladder_lower_limit', sa.Numeric(10, 6), nullable=True, comment='阶梯下限'),
        sa.Column('ladder_upper_limit', sa.Numeric(10, 6), nullable=True, comment='阶梯上限'),
        sa.Column('adjustment_intensity', sa.Numeric(10, 6), nullable=True, comment='调整力度/管控力度'),
        
        # 计算过程 - 权重调整
        sa.Column('original_weight', sa.Numeric(15, 4), nullable=False, comment='原始权重（全院业务价值）'),
        sa.Column('adjusted_weight', sa.Numeric(15, 4), nullable=True, comment='调整后权重 = 原始权重 × 调整力度'),
        
        # 调整状态
        sa.Column('is_adjusted', sa.Boolean(), nullable=False, default=False, comment='是否实际调整'),
        sa.Column('adjustment_reason', sa.String(200), nullable=True, comment='未调整原因'),
        
        # 时间戳
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        
        sa.PrimaryKeyConstraint('id')
    )
    
    # 创建索引
    op.create_index('ix_orientation_adjustment_details_task_id', 'orientation_adjustment_details', ['task_id'])
    op.create_index('ix_orientation_adjustment_details_hospital_id', 'orientation_adjustment_details', ['hospital_id'])
    op.create_index('ix_orientation_adjustment_details_year_month', 'orientation_adjustment_details', ['year_month'])
    op.create_index('ix_orientation_adjustment_details_department_id', 'orientation_adjustment_details', ['department_id'])
    op.create_index('ix_orientation_adjustment_details_node_id', 'orientation_adjustment_details', ['node_id'])
    op.create_index('ix_orientation_adjustment_details_orientation_rule_id', 'orientation_adjustment_details', ['orientation_rule_id'])
    
    # 创建复合索引（常用查询组合）
    op.create_index(
        'ix_orientation_adjustment_details_task_dept_node',
        'orientation_adjustment_details',
        ['task_id', 'department_id', 'node_id']
    )
    
    # 添加外键约束
    op.execute("""
        DO $$ BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM pg_constraint WHERE conname = 'fk_orientation_adjustment_details_hospital_id'
            ) THEN
                ALTER TABLE orientation_adjustment_details 
                ADD CONSTRAINT fk_orientation_adjustment_details_hospital_id 
                FOREIGN KEY (hospital_id) REFERENCES hospitals(id) ON DELETE CASCADE;
            END IF;
        END $$;
    """)
    
    op.execute("""
        DO $$ BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM pg_constraint WHERE conname = 'fk_orientation_adjustment_details_department_id'
            ) THEN
                ALTER TABLE orientation_adjustment_details 
                ADD CONSTRAINT fk_orientation_adjustment_details_department_id 
                FOREIGN KEY (department_id) REFERENCES departments(id) ON DELETE CASCADE;
            END IF;
        END $$;
    """)
    
    op.execute("""
        DO $$ BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM pg_constraint WHERE conname = 'fk_orientation_adjustment_details_node_id'
            ) THEN
                ALTER TABLE orientation_adjustment_details 
                ADD CONSTRAINT fk_orientation_adjustment_details_node_id 
                FOREIGN KEY (node_id) REFERENCES model_nodes(id) ON DELETE CASCADE;
            END IF;
        END $$;
    """)
    
    op.execute("""
        DO $$ BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM pg_constraint WHERE conname = 'fk_orientation_adjustment_details_orientation_rule_id'
            ) THEN
                ALTER TABLE orientation_adjustment_details 
                ADD CONSTRAINT fk_orientation_adjustment_details_orientation_rule_id 
                FOREIGN KEY (orientation_rule_id) REFERENCES orientation_rules(id) ON DELETE CASCADE;
            END IF;
        END $$;
    """)


def downgrade():
    op.drop_table('orientation_adjustment_details')
