"""add data issues table

Revision ID: 20251119_data_issues
Revises: 20251106_add_default_roles
Create Date: 2025-11-19

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '20251119_data_issues'
down_revision = '20251106_add_default_roles'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 创建处理阶段枚举类型（如果不存在）
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE processingstage AS ENUM ('not_started', 'in_progress', 'resolved', 'confirmed');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)
    
    # 使用原始SQL创建表以避免SQLAlchemy自动创建枚举类型
    op.execute("""
        CREATE TABLE IF NOT EXISTS data_issues (
            id SERIAL PRIMARY KEY,
            title VARCHAR(200) NOT NULL,
            description TEXT NOT NULL,
            reporter VARCHAR(100) NOT NULL,
            reporter_user_id INTEGER,
            assignee VARCHAR(100),
            assignee_user_id INTEGER,
            processing_stage processingstage NOT NULL DEFAULT 'not_started',
            resolution TEXT,
            hospital_id INTEGER NOT NULL,
            created_at TIMESTAMP NOT NULL DEFAULT now(),
            resolved_at TIMESTAMP,
            updated_at TIMESTAMP NOT NULL DEFAULT now()
        );
    """)
    
    # 添加注释
    op.execute("""
        COMMENT ON COLUMN data_issues.id IS '问题ID';
        COMMENT ON COLUMN data_issues.title IS '问题标题';
        COMMENT ON COLUMN data_issues.description IS '问题描述';
        COMMENT ON COLUMN data_issues.reporter IS '记录人姓名';
        COMMENT ON COLUMN data_issues.reporter_user_id IS '记录人用户ID';
        COMMENT ON COLUMN data_issues.assignee IS '负责人姓名';
        COMMENT ON COLUMN data_issues.assignee_user_id IS '负责人用户ID';
        COMMENT ON COLUMN data_issues.processing_stage IS '处理阶段';
        COMMENT ON COLUMN data_issues.resolution IS '解决方案';
        COMMENT ON COLUMN data_issues.hospital_id IS '所属医疗机构ID';
        COMMENT ON COLUMN data_issues.created_at IS '记录时间';
        COMMENT ON COLUMN data_issues.resolved_at IS '解决时间';
        COMMENT ON COLUMN data_issues.updated_at IS '更新时间';
    """)
    
    # 创建索引
    op.execute("CREATE INDEX IF NOT EXISTS ix_data_issues_id ON data_issues (id);")
    op.execute("CREATE INDEX IF NOT EXISTS ix_data_issues_hospital_id ON data_issues (hospital_id);")
    op.execute("CREATE INDEX IF NOT EXISTS ix_data_issues_processing_stage ON data_issues (processing_stage);")
    op.execute("CREATE INDEX IF NOT EXISTS ix_data_issues_reporter_user_id ON data_issues (reporter_user_id);")
    op.execute("CREATE INDEX IF NOT EXISTS ix_data_issues_assignee_user_id ON data_issues (assignee_user_id);")
    op.execute("CREATE INDEX IF NOT EXISTS ix_data_issues_created_at ON data_issues (created_at);")
    
    # 创建外键约束（使用DO块检查是否存在）
    op.execute("""
        DO $$ BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM pg_constraint WHERE conname = 'fk_data_issues_hospital_id'
            ) THEN
                ALTER TABLE data_issues 
                ADD CONSTRAINT fk_data_issues_hospital_id 
                FOREIGN KEY (hospital_id) REFERENCES hospitals(id) ON DELETE CASCADE;
            END IF;
        END $$;
    """)
    op.execute("""
        DO $$ BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM pg_constraint WHERE conname = 'fk_data_issues_reporter_user_id'
            ) THEN
                ALTER TABLE data_issues 
                ADD CONSTRAINT fk_data_issues_reporter_user_id 
                FOREIGN KEY (reporter_user_id) REFERENCES users(id) ON DELETE SET NULL;
            END IF;
        END $$;
    """)
    op.execute("""
        DO $$ BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM pg_constraint WHERE conname = 'fk_data_issues_assignee_user_id'
            ) THEN
                ALTER TABLE data_issues 
                ADD CONSTRAINT fk_data_issues_assignee_user_id 
                FOREIGN KEY (assignee_user_id) REFERENCES users(id) ON DELETE SET NULL;
            END IF;
        END $$;
    """)


def downgrade() -> None:
    # 删除外键约束
    op.execute("ALTER TABLE data_issues DROP CONSTRAINT IF EXISTS fk_data_issues_assignee_user_id;")
    op.execute("ALTER TABLE data_issues DROP CONSTRAINT IF EXISTS fk_data_issues_reporter_user_id;")
    op.execute("ALTER TABLE data_issues DROP CONSTRAINT IF EXISTS fk_data_issues_hospital_id;")
    
    # 删除索引
    op.execute("DROP INDEX IF EXISTS ix_data_issues_created_at;")
    op.execute("DROP INDEX IF EXISTS ix_data_issues_assignee_user_id;")
    op.execute("DROP INDEX IF EXISTS ix_data_issues_reporter_user_id;")
    op.execute("DROP INDEX IF EXISTS ix_data_issues_processing_stage;")
    op.execute("DROP INDEX IF EXISTS ix_data_issues_hospital_id;")
    op.execute("DROP INDEX IF EXISTS ix_data_issues_id;")
    
    # 删除表
    op.execute("DROP TABLE IF EXISTS data_issues;")
    
    # 删除枚举类型
    op.execute("DROP TYPE IF EXISTS processingstage;")
