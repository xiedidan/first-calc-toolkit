-- 修复收费项目迁移状态
-- 如果迁移失败，请在 PostgreSQL 中执行此脚本

BEGIN;

-- 1. 删除可能存在的外键约束
ALTER TABLE charge_items DROP CONSTRAINT IF EXISTS fk_charge_items_hospital_id;

-- 2. 删除可能存在的索引
DROP INDEX IF EXISTS ix_charge_items_hospital_id;

-- 3. 删除可能存在的复合唯一约束
ALTER TABLE charge_items DROP CONSTRAINT IF EXISTS uq_hospital_item_code;

-- 4. 删除 hospital_id 列（如果存在）
ALTER TABLE charge_items DROP COLUMN IF EXISTS hospital_id;

-- 5. 回滚 alembic 版本到上一个版本
UPDATE alembic_version SET version_num = '20251103_hospital';

COMMIT;

-- 完成！现在可以重新运行: alembic upgrade head
