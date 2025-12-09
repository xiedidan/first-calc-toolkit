"""add analysis_reports table

Revision ID: 20251205_analysis_reports
Revises: 22398d9e8699
Create Date: 2024-12-05

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '20251205_analysis_reports'
down_revision = '22398d9e8699'
branch_labels = None
depends_on = None


def upgrade():
    # 创建 analysis_reports 表
    op.execute("""
        CREATE TABLE IF NOT EXISTS analysis_reports (
            id SERIAL PRIMARY KEY,
            hospital_id INTEGER NOT NULL REFERENCES hospitals(id) ON DELETE CASCADE,
            department_id INTEGER NOT NULL REFERENCES departments(id) ON DELETE CASCADE,
            period VARCHAR(20) NOT NULL,
            current_issues TEXT,
            future_plans TEXT,
            created_at TIMESTAMP DEFAULT NOW() NOT NULL,
            updated_at TIMESTAMP DEFAULT NOW() NOT NULL,
            created_by INTEGER REFERENCES users(id) ON DELETE SET NULL
        );
    """)
    
    # 添加唯一约束
    op.execute("""
        DO $$ BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM pg_constraint WHERE conname = 'uq_analysis_report_hospital_dept_period'
            ) THEN
                ALTER TABLE analysis_reports 
                ADD CONSTRAINT uq_analysis_report_hospital_dept_period 
                UNIQUE (hospital_id, department_id, period);
            END IF;
        END $$;
    """)
    
    # 创建索引
    op.execute("""
        CREATE INDEX IF NOT EXISTS ix_analysis_reports_id ON analysis_reports(id);
    """)
    op.execute("""
        CREATE INDEX IF NOT EXISTS ix_analysis_reports_hospital_id ON analysis_reports(hospital_id);
    """)
    op.execute("""
        CREATE INDEX IF NOT EXISTS ix_analysis_reports_department_id ON analysis_reports(department_id);
    """)
    op.execute("""
        CREATE INDEX IF NOT EXISTS ix_analysis_reports_period ON analysis_reports(period);
    """)
    op.execute("""
        CREATE INDEX IF NOT EXISTS ix_analysis_reports_hospital_period ON analysis_reports(hospital_id, period);
    """)
    
    # 添加字段注释
    op.execute("""
        COMMENT ON TABLE analysis_reports IS '科室运营分析报告表';
    """)
    op.execute("""
        COMMENT ON COLUMN analysis_reports.hospital_id IS '所属医疗机构ID';
    """)
    op.execute("""
        COMMENT ON COLUMN analysis_reports.department_id IS '科室ID';
    """)
    op.execute("""
        COMMENT ON COLUMN analysis_reports.period IS '年月 (YYYY-MM格式)';
    """)
    op.execute("""
        COMMENT ON COLUMN analysis_reports.current_issues IS '当前存在问题 (Markdown格式，最大2000字符)';
    """)
    op.execute("""
        COMMENT ON COLUMN analysis_reports.future_plans IS '未来发展计划 (Markdown格式，最大2000字符)';
    """)
    op.execute("""
        COMMENT ON COLUMN analysis_reports.created_by IS '创建人ID';
    """)


def downgrade():
    op.execute("DROP TABLE IF EXISTS analysis_reports CASCADE;")
