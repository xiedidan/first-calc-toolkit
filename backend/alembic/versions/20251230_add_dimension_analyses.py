"""add dimension_analyses table

Revision ID: 20251230_dim_analyses
Revises: 20251230_calc_details
Create Date: 2025-12-30

维度分析表：存储用户对维度的分析文字
- 当期分析：与医院、科室、月份、维度挂钩
- 长期分析：与医院、科室、维度挂钩（period 为 NULL）
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20251230_dim_analyses'
down_revision = '20251230_calc_details'
branch_labels = None
depends_on = None


def upgrade():
    # 创建 dimension_analyses 表
    op.execute("""
        CREATE TABLE IF NOT EXISTS dimension_analyses (
            id SERIAL PRIMARY KEY,
            hospital_id INTEGER NOT NULL,
            department_id INTEGER NOT NULL,
            node_id INTEGER NOT NULL,
            period VARCHAR(7),
            content TEXT NOT NULL,
            created_by INTEGER,
            updated_by INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            
            CONSTRAINT fk_dim_analysis_hospital FOREIGN KEY (hospital_id) REFERENCES hospitals(id) ON DELETE CASCADE,
            CONSTRAINT fk_dim_analysis_department FOREIGN KEY (department_id) REFERENCES departments(id) ON DELETE CASCADE,
            CONSTRAINT fk_dim_analysis_node FOREIGN KEY (node_id) REFERENCES model_nodes(id) ON DELETE CASCADE,
            CONSTRAINT fk_dim_analysis_creator FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL,
            CONSTRAINT fk_dim_analysis_updater FOREIGN KEY (updated_by) REFERENCES users(id) ON DELETE SET NULL
        )
    """)
    
    # 添加表注释
    op.execute("COMMENT ON TABLE dimension_analyses IS '维度分析表 - 存储用户对维度的分析文字'")
    op.execute("COMMENT ON COLUMN dimension_analyses.hospital_id IS '医疗机构ID'")
    op.execute("COMMENT ON COLUMN dimension_analyses.department_id IS '科室ID'")
    op.execute("COMMENT ON COLUMN dimension_analyses.node_id IS '维度节点ID'")
    op.execute("COMMENT ON COLUMN dimension_analyses.period IS '统计月份(YYYY-MM)，NULL表示长期分析'")
    op.execute("COMMENT ON COLUMN dimension_analyses.content IS '分析内容'")
    op.execute("COMMENT ON COLUMN dimension_analyses.created_by IS '创建人ID'")
    op.execute("COMMENT ON COLUMN dimension_analyses.updated_by IS '更新人ID'")
    op.execute("COMMENT ON COLUMN dimension_analyses.created_at IS '创建时间'")
    op.execute("COMMENT ON COLUMN dimension_analyses.updated_at IS '更新时间'")
    
    # 创建索引
    op.execute("CREATE INDEX IF NOT EXISTS idx_dim_analysis_hospital ON dimension_analyses(hospital_id)")
    op.execute("CREATE INDEX IF NOT EXISTS idx_dim_analysis_department ON dimension_analyses(department_id)")
    op.execute("CREATE INDEX IF NOT EXISTS idx_dim_analysis_node ON dimension_analyses(node_id)")
    op.execute("CREATE INDEX IF NOT EXISTS idx_dim_analysis_period ON dimension_analyses(period)")
    op.execute("CREATE INDEX IF NOT EXISTS idx_dim_analysis_lookup ON dimension_analyses(hospital_id, department_id, node_id, period)")
    
    # 创建唯一约束（使用 COALESCE 处理 NULL 值）
    op.execute("""
        CREATE UNIQUE INDEX IF NOT EXISTS uq_dim_analysis_key 
        ON dimension_analyses(hospital_id, department_id, node_id, COALESCE(period, ''))
    """)


def downgrade():
    op.execute("DROP TABLE IF EXISTS dimension_analyses CASCADE")
