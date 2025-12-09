-- ============================================================================
-- 数据库迁移脚本: 为收费明细表添加业务类别字段
-- ============================================================================
-- 功能: 在外部数据源的 charge_details 表中添加 business_type 字段
-- 
-- 使用方法:
--   psql -h <host> -U <user> -d <database> -f add_business_type_to_charge_details.sql
--
-- 注意事项:
--   1. 此脚本是幂等的，可以重复执行
--   2. 如果字段已存在，会跳过添加操作
--   3. 建议先在测试环境执行，确认无误后再在生产环境执行
-- ============================================================================

-- 检查表是否存在
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.tables 
        WHERE table_name = 'charge_details'
    ) THEN
        RAISE NOTICE '表 charge_details 不存在，跳过迁移';
        RETURN;
    END IF;
    
    RAISE NOTICE '表 charge_details 存在，开始检查字段...';
END $$;

-- 添加 business_type 字段（如果不存在）
DO $$ 
BEGIN
    -- 检查字段是否已存在
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'charge_details' 
        AND column_name = 'business_type'
    ) THEN
        -- 添加字段
        ALTER TABLE charge_details 
        ADD COLUMN business_type VARCHAR(20);
        
        RAISE NOTICE '✅ 已添加字段 business_type';
        
        -- 添加索引以提高查询性能
        CREATE INDEX idx_charge_details_business_type 
        ON charge_details(business_type);
        
        RAISE NOTICE '✅ 已创建索引 idx_charge_details_business_type';
        
        -- 添加注释
        COMMENT ON COLUMN charge_details.business_type IS '业务类别：门诊、住院';
        
        RAISE NOTICE '✅ 已添加字段注释';
    ELSE
        RAISE NOTICE '⚠️  字段 business_type 已存在，跳过添加';
    END IF;
END $$;

-- 验证字段是否添加成功
DO $$ 
DECLARE
    col_exists BOOLEAN;
    idx_exists BOOLEAN;
BEGIN
    -- 检查字段
    SELECT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'charge_details' 
        AND column_name = 'business_type'
    ) INTO col_exists;
    
    -- 检查索引
    SELECT EXISTS (
        SELECT 1 FROM pg_indexes 
        WHERE tablename = 'charge_details' 
        AND indexname = 'idx_charge_details_business_type'
    ) INTO idx_exists;
    
    IF col_exists THEN
        RAISE NOTICE '✅ 验证成功: 字段 business_type 存在';
    ELSE
        RAISE EXCEPTION '❌ 验证失败: 字段 business_type 不存在';
    END IF;
    
    IF idx_exists THEN
        RAISE NOTICE '✅ 验证成功: 索引 idx_charge_details_business_type 存在';
    ELSE
        RAISE NOTICE '⚠️  警告: 索引 idx_charge_details_business_type 不存在';
    END IF;
END $$;

-- 显示表结构
\d charge_details

-- 统计现有数据的业务类别分布
DO $$ 
DECLARE
    total_count INTEGER;
    null_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO total_count FROM charge_details;
    SELECT COUNT(*) INTO null_count FROM charge_details WHERE business_type IS NULL;
    
    RAISE NOTICE '';
    RAISE NOTICE '数据统计:';
    RAISE NOTICE '  总记录数: %', total_count;
    RAISE NOTICE '  业务类别为空的记录数: %', null_count;
    
    IF null_count > 0 AND total_count > 0 THEN
        RAISE NOTICE '  ⚠️  提示: 有 % 条记录的业务类别为空 (%.2f%%)', 
            null_count, (null_count::FLOAT / total_count * 100);
        RAISE NOTICE '  建议: 根据实际业务规则更新这些记录的业务类别';
    END IF;
END $$;

-- ============================================================================
-- 迁移完成
-- ============================================================================
-- 后续步骤:
--   1. 如果有历史数据，需要根据业务规则更新 business_type 字段
--   2. 可以使用以下SQL更新历史数据（示例）:
--      UPDATE charge_details 
--      SET business_type = '门诊' 
--      WHERE business_type IS NULL 
--      AND <门诊业务的判断条件>;
--
--      UPDATE charge_details 
--      SET business_type = '住院' 
--      WHERE business_type IS NULL 
--      AND <住院业务的判断条件>;
--
--   3. 新插入的数据应该包含 business_type 字段
-- ============================================================================
