# test_code 接口修复说明

## 问题 1：DataSourceService 实例化错误

### 问题描述
`/api/calculation-steps/test-code` 接口返回错误：
```json
{
  "success": false,
  "duration_ms": 3,
  "result": null,
  "error": "DataSourceService() takes no arguments"
}
```

### 问题原因
错误地实例化了 `DataSourceService` 类，但该类的所有方法都是 `@staticmethod`，不需要实例化。

### 修复方案
使用 `connection_manager` 来获取和管理数据库连接。

## 问题 2：自动添加 LIMIT 导致 SQL 语法错误

### 问题描述
执行 `CREATE TABLE test;` 时报错：
```
syntax error at or near "LIMIT"
LINE 1: create table test LIMIT 100
```

### 问题原因
代码无条件地给所有 SQL 语句添加 `LIMIT 100`，但 DDL/DML 语句（CREATE、INSERT、UPDATE、DELETE）不支持 LIMIT。

### 修复方案
移除自动添加 LIMIT 的逻辑，让用户自己控制查询结果数量。

## 修复内容

修改文件：`backend/app/api/calculation_steps.py`

### 1. 修复连接管理
- 移除错误的 `DataSourceService` 实例化
- 使用 `connection_manager` 获取连接池
- 使用 `with` 语句管理连接生命周期

### 2. 移除自动 LIMIT
- 移除自动添加 `LIMIT 100` 的逻辑
- 支持所有类型的 SQL 语句（SELECT、CREATE、INSERT、UPDATE、DELETE 等）

### 3. 区分查询和非查询语句
- 使用 `result.returns_rows` 判断是否有返回结果
- 对于 DDL/DML 语句，自动提交事务
- 根据语句类型返回不同的成功消息

### 4. 修复的函数
- `test_step_code()` - 测试已保存步骤的代码
- `test_code_without_save()` - 测试未保存的代码

## 测试方法

### 1. 测试 SELECT 查询
```bash
POST /api/calculation-steps/test-code
{
  "code_type": "sql",
  "code_content": "SELECT 1 as test_column",
  "data_source_id": 1
}
```

预期结果：
```json
{
  "success": true,
  "duration_ms": 50,
  "result": {
    "message": "SQL执行成功，返回 1 行数据",
    "columns": ["test_column"],
    "rows": [{"test_column": 1}],
    "row_count": 1
  }
}
```

### 2. 测试 CREATE TABLE
```bash
POST /api/calculation-steps/test-code
{
  "code_type": "sql",
  "code_content": "CREATE TABLE test (id INT, name VARCHAR(50))",
  "data_source_id": 1
}
```

预期结果：
```json
{
  "success": true,
  "duration_ms": 30,
  "result": {
    "message": "SQL执行成功",
    "columns": [],
    "rows": [],
    "row_count": 0
  }
}
```

### 3. 测试 INSERT
```bash
POST /api/calculation-steps/test-code
{
  "code_type": "sql",
  "code_content": "INSERT INTO test VALUES (1, 'Alice')",
  "data_source_id": 1
}
```

预期结果：
```json
{
  "success": true,
  "duration_ms": 25,
  "result": {
    "message": "SQL执行成功",
    "columns": [],
    "rows": [],
    "row_count": 0
  }
}
```
