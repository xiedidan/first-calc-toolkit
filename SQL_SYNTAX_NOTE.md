# SQL 语法说明

## CREATE TABLE 语法错误

### 错误信息
```
(psycopg2.errors.SyntaxError) syntax error at or near ";" 
LINE 1: create table test;
```

### 问题原因

`CREATE TABLE test;` 是不完整的 SQL 语句。在 PostgreSQL（以及大多数数据库）中，CREATE TABLE 必须至少定义一个列。

### 正确的语法

#### 最简单的表（一个列）
```sql
CREATE TABLE test (
    id INT
);
```

或者一行写法：
```sql
CREATE TABLE test (id INT);
```

#### 带多个列
```sql
CREATE TABLE test (
    id INT PRIMARY KEY,
    name VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### 带约束
```sql
CREATE TABLE test (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    email VARCHAR(100) UNIQUE,
    age INT CHECK (age >= 0)
);
```

### 其他常见的 DDL 语句示例

#### 1. 删除表
```sql
DROP TABLE IF EXISTS test;
```

#### 2. 修改表结构
```sql
-- 添加列
ALTER TABLE test ADD COLUMN description TEXT;

-- 删除列
ALTER TABLE test DROP COLUMN description;

-- 修改列类型
ALTER TABLE test ALTER COLUMN name TYPE VARCHAR(100);
```

#### 3. 创建索引
```sql
CREATE INDEX idx_test_name ON test(name);
```

#### 4. 插入数据
```sql
INSERT INTO test (id, name) VALUES (1, 'Alice');
```

#### 5. 更新数据
```sql
UPDATE test SET name = 'Bob' WHERE id = 1;
```

#### 6. 删除数据
```sql
DELETE FROM test WHERE id = 1;
```

#### 7. 查询数据
```sql
SELECT * FROM test;
SELECT id, name FROM test WHERE id > 0 LIMIT 10;
```

### 测试建议

在测试 SQL 代码时，建议使用完整的、语法正确的 SQL 语句：

1. **测试创建表**
```sql
CREATE TABLE test_table (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

2. **测试插入数据**
```sql
INSERT INTO test_table (name) VALUES ('Test User');
```

3. **测试查询**
```sql
SELECT * FROM test_table;
```

4. **测试清理**
```sql
DROP TABLE IF EXISTS test_table;
```

### 注意事项

1. **事务管理**：DDL 语句（CREATE、DROP、ALTER）在 PostgreSQL 中会自动提交
2. **权限检查**：确保数据库用户有相应的权限
3. **表名冲突**：创建表前检查表是否已存在，或使用 `CREATE TABLE IF NOT EXISTS`
4. **数据类型**：不同数据库的数据类型可能有差异

### PostgreSQL 特定语法

```sql
-- 创建表（如果不存在）
CREATE TABLE IF NOT EXISTS test (id INT);

-- 创建临时表
CREATE TEMP TABLE test (id INT);

-- 创建表并从查询结果填充
CREATE TABLE test AS SELECT * FROM other_table;
```
