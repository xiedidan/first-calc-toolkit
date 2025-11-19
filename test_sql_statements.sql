-- ============================================
-- 测试 SQL 语句集合
-- ============================================

-- 1. 创建测试表
CREATE TABLE IF NOT EXISTS test (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    age INT,
    email VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. 插入单条数据
INSERT INTO test (name, age, email) 
VALUES ('张三', 25, 'zhangsan@example.com');

-- 3. 插入多条数据
INSERT INTO test (name, age, email) VALUES 
    ('李四', 30, 'lisi@example.com'),
    ('王五', 28, 'wangwu@example.com'),
    ('赵六', 35, 'zhaoliu@example.com');

-- 4. 查询所有数据
SELECT * FROM test;

-- 5. 查询指定列
SELECT id, name, age FROM test;

-- 6. 条件查询
SELECT * FROM test WHERE age > 25;

-- 7. 排序查询
SELECT * FROM test ORDER BY age DESC;

-- 8. 限制返回数量
SELECT * FROM test LIMIT 5;

-- 9. 统计查询
SELECT COUNT(*) as total_count FROM test;

-- 10. 分组查询
SELECT age, COUNT(*) as count FROM test GROUP BY age;

-- 11. 更新数据
UPDATE test SET age = 26 WHERE name = '张三';

-- 12. 删除数据
DELETE FROM test WHERE name = '赵六';

-- 13. 查看表结构（PostgreSQL）
SELECT 
    column_name, 
    data_type, 
    character_maximum_length,
    is_nullable
FROM information_schema.columns 
WHERE table_name = 'test';

-- 14. 清空表数据（保留表结构）
TRUNCATE TABLE test;

-- 15. 删除表
DROP TABLE IF EXISTS test;
