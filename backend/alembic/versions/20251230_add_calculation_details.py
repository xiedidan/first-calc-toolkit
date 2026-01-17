"""add calculation_details table

Revision ID: 20251230_calc_details
Revises: 20251226_batch_id
Create Date: 2025-12-30

核算明细表：存储按(hospital_id, task_id, department_id, node_id, item_code)聚合的收费明细
用于支持维度下钻功能，将统计逻辑从API层移到计算流程中
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20251230_calc_details'
down_revision = '20251226_batch_id'
branch_labels = None
depends_on = None


def upgrade():
    # 创建 calculation_details 表
    op.execute("""
        CREATE TABLE IF NOT EXISTS calculation_details (
            id SERIAL PRIMARY KEY,
            hospital_id INTEGER NOT NULL,
            task_id VARCHAR(100) NOT NULL,
            department_id INTEGER NOT NULL,
            department_code VARCHAR(50) NOT NULL,
            
            -- 维度信息
            node_id INTEGER NOT NULL,
            node_code VARCHAR(100) NOT NULL,
            node_name VARCHAR(255) NOT NULL,
            parent_id INTEGER,
            
            -- 收费项目信息
            item_code VARCHAR(100) NOT NULL,
            item_name VARCHAR(200),
            item_category VARCHAR(100),
            
            -- 业务属性
            business_type VARCHAR(20),
            
            -- 数值
            amount DECIMAL(20, 4) NOT NULL DEFAULT 0,
            quantity DECIMAL(20, 4) NOT NULL DEFAULT 0,
            
            -- 时间
            period VARCHAR(7) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # 添加列注释
    op.execute("COMMENT ON TABLE calculation_details IS '核算明细表 - 按维度和项目聚合的收费明细'")
    op.execute("COMMENT ON COLUMN calculation_details.hospital_id IS '医疗机构ID'")
    op.execute("COMMENT ON COLUMN calculation_details.task_id IS '计算任务ID'")
    op.execute("COMMENT ON COLUMN calculation_details.department_id IS '科室ID'")
    op.execute("COMMENT ON COLUMN calculation_details.department_code IS '科室代码'")
    op.execute("COMMENT ON COLUMN calculation_details.node_id IS '维度节点ID'")
    op.execute("COMMENT ON COLUMN calculation_details.node_code IS '维度编码'")
    op.execute("COMMENT ON COLUMN calculation_details.node_name IS '维度名称'")
    op.execute("COMMENT ON COLUMN calculation_details.parent_id IS '父节点ID'")
    op.execute("COMMENT ON COLUMN calculation_details.item_code IS '收费项目编码'")
    op.execute("COMMENT ON COLUMN calculation_details.item_name IS '收费项目名称'")
    op.execute("COMMENT ON COLUMN calculation_details.item_category IS '项目类别'")
    op.execute("COMMENT ON COLUMN calculation_details.business_type IS '业务类型（门诊/住院）'")
    op.execute("COMMENT ON COLUMN calculation_details.amount IS '金额'")
    op.execute("COMMENT ON COLUMN calculation_details.quantity IS '数量'")
    op.execute("COMMENT ON COLUMN calculation_details.period IS '统计月份(YYYY-MM)'")
    
    # 创建索引
    op.execute("CREATE INDEX IF NOT EXISTS idx_calc_details_hospital ON calculation_details(hospital_id)")
    op.execute("CREATE INDEX IF NOT EXISTS idx_calc_details_task ON calculation_details(task_id)")
    op.execute("CREATE INDEX IF NOT EXISTS idx_calc_details_dept ON calculation_details(department_id)")
    op.execute("CREATE INDEX IF NOT EXISTS idx_calc_details_node ON calculation_details(node_id)")
    op.execute("CREATE INDEX IF NOT EXISTS idx_calc_details_item ON calculation_details(item_code)")
    op.execute("CREATE INDEX IF NOT EXISTS idx_calc_details_task_dept_node ON calculation_details(task_id, department_id, node_id)")
    op.execute("CREATE INDEX IF NOT EXISTS idx_calc_details_hospital_task ON calculation_details(hospital_id, task_id)")
    
    # 创建唯一约束（防止重复数据）
    op.execute("""
        CREATE UNIQUE INDEX IF NOT EXISTS uq_calc_details_key 
        ON calculation_details(hospital_id, task_id, department_id, node_id, item_code, COALESCE(business_type, ''))
    """)


def downgrade():
    op.execute("DROP TABLE IF EXISTS calculation_details CASCADE")
