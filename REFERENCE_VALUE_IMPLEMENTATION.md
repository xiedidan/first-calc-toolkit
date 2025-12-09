# 参考价值管理功能实现

## 功能概述

在科室业务价值汇总表中添加"参考总价值"和"实际参考比"列，用于对比科室实际业务价值与参考价值。

## 实现内容

### 1. 后端

#### 数据模型
- `backend/app/models/reference_value.py` - 参考价值模型
  - 字段：id, hospital_id, period, department_code, department_name, reference_value, doctor_reference_value, nurse_reference_value, tech_reference_value

#### Schema
- `backend/app/schemas/reference_value.py` - 请求/响应模型
  - 基础CRUD Schema
  - Excel智能导入相关Schema

#### API路由
- `backend/app/api/reference_values.py` - RESTful API
  - `GET /reference-values` - 获取列表
  - `GET /reference-values/by-period/{period}` - 获取指定月份数据（用于报表对比）
  - `GET /reference-values/periods` - 获取已有月份列表
  - `POST /reference-values` - 创建
  - `PUT /reference-values/{id}` - 更新
  - `DELETE /reference-values/{id}` - 删除
  - `DELETE /reference-values/period/{period}/clear-all` - 清空指定月份
  - `DELETE /reference-values/clear-all` - 清空所有
  - Excel导入相关接口（parse, extract-values, preview, execute）

#### 服务
- `backend/app/services/reference_value_import_service.py` - Excel智能导入服务
  - 支持按科室代码精确匹配
  - 支持按科室名称模糊匹配（带智能建议）

### 2. 前端

#### API
- `frontend/src/api/reference-values.ts` - API调用函数

#### 页面
- `frontend/src/views/ReferenceValues.vue` - 参考价值管理页面
  - 数据列表展示
  - 手动添加/编辑
  - Excel智能导入（三步向导）

#### 路由
- 添加 `/reference-values` 路由

#### 菜单
- 在"基础数据管理"下添加"参考价值管理"菜单项

#### 报表对比
- 修改 `frontend/src/views/Results.vue`
  - 添加"参考总价值"列
  - 添加"实际参考比"列（科室总价值/参考总价值）
  - 未录入参考价值时显示"-"

### 3. 数据库迁移

- `backend/alembic/versions/20251202_add_reference_values.py` - Alembic迁移
- `create_reference_values_table.sql` - 直接SQL脚本（备选）

## 使用说明

### Excel导入流程

1. **第一步：上传文件**
   - 选择Excel文件
   - 设置标题行位置（跳过前N行）
   - 选择匹配方式：
     - 按科室代码精确匹配：Excel中需有科室代码列
     - 按科室名称模糊匹配：系统自动匹配相似科室名称
   - 配置字段映射

2. **第二步：科室匹配**（仅名称匹配时）
   - 系统显示Excel中的唯一科室名称
   - 为每个名称选择对应的系统科室
   - 系统提供相似度建议

3. **第三步：预览确认**
   - 显示导入预览
   - 标记新增/覆盖/错误记录
   - 确认后执行导入

### 报表对比

- 在"业务价值报表"页面查看汇总表
- "参考总价值"列显示该科室当月的参考价值
- "实际参考比"列显示 科室总价值/参考总价值 的百分比
- 未录入参考价值时显示"-"

## 部署步骤

1. 执行数据库迁移：
   ```bash
   cd backend
   alembic upgrade head
   ```
   或直接执行SQL：
   ```bash
   psql -h <host> -U <user> -d <database> -f create_reference_values_table.sql
   ```

2. 重启后端服务

3. 重新构建前端（如需要）
