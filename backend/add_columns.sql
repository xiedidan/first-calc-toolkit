-- 手动添加 calculation_steps 表的列

-- 检查并添加 python_env 列
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'calculation_steps' AND column_name = 'python_env'
    ) THEN
        ALTER TABLE calculation_steps ADD COLUMN python_env VARCHAR(200);
        RAISE NOTICE 'python_env 列已添加';
    ELSE
        RAISE NOTICE 'python_env 列已存在';
    END IF;
END $$;

-- 检查并添加 data_source_id 列
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'calculation_steps' AND column_name = 'data_source_id'
    ) THEN
        ALTER TABLE calculation_steps ADD COLUMN data_source_id INTEGER;
        RAISE NOTICE 'data_source_id 列已添加';
    ELSE
        RAISE NOTICE 'data_source_id 列已存在';
    END IF;
END $$;

-- 检查并添加外键约束
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints 
        WHERE constraint_name = 'fk_calculation_steps_data_source_id'
    ) THEN
        ALTER TABLE calculation_steps 
        ADD CONSTRAINT fk_calculation_steps_data_source_id 
        FOREIGN KEY (data_source_id) REFERENCES data_sources(id) ON DELETE SET NULL;
        RAISE NOTICE '外键约束已添加';
    ELSE
        RAISE NOTICE '外键约束已存在';
    END IF;
END $$;

-- 检查并添加索引
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_indexes 
        WHERE indexname = 'ix_calculation_steps_data_source_id'
    ) THEN
        CREATE INDEX ix_calculation_steps_data_source_id ON calculation_steps(data_source_id);
        RAISE NOTICE '索引已添加';
    ELSE
        RAISE NOTICE '索引已存在';
    END IF;
END $$;

-- 查看最终的表结构
SELECT column_name, data_type, is_nullable 
FROM information_schema.columns 
WHERE table_name = 'calculation_steps'
ORDER BY ordinal_position;
