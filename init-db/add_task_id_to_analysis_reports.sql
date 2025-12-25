-- Add task_id column to analysis_reports table
ALTER TABLE analysis_reports ADD COLUMN IF NOT EXISTS task_id VARCHAR(100);
CREATE INDEX IF NOT EXISTS ix_analysis_reports_task_id ON analysis_reports(task_id);
