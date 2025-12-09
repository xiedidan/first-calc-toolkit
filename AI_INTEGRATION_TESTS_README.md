# AI分类集成测试文档

## 概述

本文档描述了AI医技智能分类分级模块的集成测试和端到端测试。这些测试验证了完整的分类流程，从AI接口配置到最终的维度目录提交。

## 测试文件

### 1. test_ai_interface_integration.py - AI接口集成测试

**目的**: 测试与DeepSeek AI接口的集成

**测试内容**:
- ✅ AI请求格式验证
  - 提示词模板占位符替换
  - 维度列表JSON构建
  - 请求参数完整性
  
- ✅ AI响应解析
  - 标准JSON格式解析
  - 包含额外字段的响应处理
  - confidence字段类型转换
  - 缺少字段的默认值处理
  - 非JSON格式错误处理
  - 缺少必需字段的错误处理
  
- ✅ AI错误处理
  - 连接错误重试机制
  - 限流错误处理
  - API错误处理

**验证需求**: 3.2-3.3, 9.1-9.5, 11.1-11.2

**运行方式**:
```bash
python test_ai_interface_integration.py
```

**注意事项**:
- 默认使用mock数据，不需要真实API密钥
- 如需测试真实API，设置环境变量: `DEEPSEEK_API_KEY=your-api-key`

### 2. test_e2e_classification_flow.py - 端到端分类流程测试

**目的**: 测试完整的AI分类流程

**测试流程**:
1. ✅ 配置AI接口
   - 创建AI配置
   - 验证密钥加密
   
2. ✅ 创建分类任务
   - 选择收费类别
   - 选择模型版本
   - 启动异步处理
   
3. ✅ 等待任务完成
   - 模拟AI接口调用
   - 验证进度更新
   - 验证任务状态
   
4. ✅ 查看预案
   - 验证预案生成
   - 查看预案项目
   - 验证AI建议和确信度
   
5. ✅ 调整部分项目
   - 修改项目维度
   - 验证调整标记
   
6. ✅ 保存预案
   - 设置预案名称
   - 验证保存状态
   
7. ✅ 提交预览
   - 分析新增/覆盖项目
   - 验证统计准确性
   
8. ✅ 提交预案
   - 批量提交到维度目录
   - 验证提交状态
   
9. ✅ 验证维度目录
   - 验证所有项目已添加
   - 验证调整的项目使用用户设置维度
   - 验证未调整的项目使用AI建议维度

**验证需求**: 1.1-12.5（所有需求）

**运行方式**:
```bash
python test_e2e_classification_flow.py
```

**测试数据**:
- 1个医疗机构
- 1个用户
- 1个模型版本
- 5个末级维度
- 10个医技收费项目

### 3. test_breakpoint_resume.py - 断点续传场景测试

**目的**: 测试任务中断后的断点续传功能

**测试流程**:
1. ✅ 创建任务
   - 创建包含20个项目的任务
   
2. ✅ 模拟中断
   - 处理前10个项目后抛出异常
   - 模拟Celery worker中断
   
3. ✅ 验证进度保存
   - 验证已处理10个项目
   - 验证任务状态为processing或failed
   - 验证预案项目状态（10个completed，10个pending）
   
4. ✅ 继续处理
   - 调用continue_task方法
   - 从中断位置继续处理
   
5. ✅ 验证不重复处理
   - 验证AI只调用了剩余10次
   - 验证所有项目最终都已完成
   - 验证没有重复处理

**验证需求**: 3.7, 4.3-4.5

**运行方式**:
```bash
python test_breakpoint_resume.py
```

**测试数据**:
- 1个医疗机构
- 1个用户
- 1个模型版本
- 3个末级维度
- 20个医技收费项目

## 运行所有测试

使用测试运行器一次性运行所有集成测试:

```bash
python run_integration_tests.py
```

## 测试架构

### Mock策略

所有测试都使用mock来模拟外部依赖:

1. **AI接口Mock**:
   - 使用`@patch('app.tasks.classification_tasks.call_ai_classification')`
   - 模拟AI返回随机维度和确信度
   - 可控制成功/失败场景

2. **时间Mock**:
   - 使用`@patch('app.tasks.classification_tasks.time.sleep')`
   - 跳过实际延迟，加速测试

3. **OpenAI客户端Mock**:
   - 使用`@patch('app.utils.ai_interface.OpenAI')`
   - 模拟不同的响应格式和错误场景

### 数据隔离

每个测试都:
1. 在`setup_test_data()`中创建独立的测试数据
2. 使用唯一的标识符（如"测试医院E2E"）
3. 在`cleanup_test_data()`中清理所有测试数据
4. 使用`try-finally`确保清理总是执行

### 断言策略

测试使用详细的断言来验证:
- 数据完整性（所有必需字段都存在）
- 业务逻辑（状态转换正确）
- 数据一致性（计数匹配、关系正确）
- 错误处理（异常被正确捕获和记录）

## 测试覆盖

### 功能覆盖

- ✅ AI接口配置管理
- ✅ API密钥加密/解密
- ✅ 分类任务创建
- ✅ 异步AI分类处理
- ✅ 进度跟踪和更新
- ✅ 断点续传
- ✅ 预案生成和查看
- ✅ 预案项目调整
- ✅ 预案保存
- ✅ 提交预览分析
- ✅ 批量提交到维度目录
- ✅ 多租户数据隔离

### 需求覆盖

| 需求编号 | 需求描述 | 测试文件 |
|---------|---------|---------|
| 1.1-1.8 | AI接口配置管理 | test_e2e_classification_flow.py |
| 2.1-2.7 | 医技项目选择和任务创建 | test_e2e_classification_flow.py |
| 3.1-3.7 | AI异步分类处理 | test_e2e_classification_flow.py, test_ai_interface_integration.py |
| 4.1-4.6 | 断点续传和进度管理 | test_breakpoint_resume.py |
| 5.1-5.8 | 分类预案查看和调整 | test_e2e_classification_flow.py |
| 6.1-6.7 | 分类预案命名和保存 | test_e2e_classification_flow.py |
| 7.1-7.7 | 分类预案提交前预览 | test_e2e_classification_flow.py |
| 8.1-8.7 | 分类预案正式提交 | test_e2e_classification_flow.py |
| 9.1-9.6 | AI提示词模板和参数 | test_ai_interface_integration.py |
| 10.1-10.5 | 多租户数据隔离 | test_e2e_classification_flow.py |
| 11.1-11.5 | 错误处理和日志 | test_ai_interface_integration.py |
| 12.1-12.5 | 性能和限流 | test_ai_interface_integration.py |

## 故障排查

### 常见问题

1. **数据库连接失败**
   - 确保PostgreSQL服务正在运行
   - 检查`.env`文件中的数据库配置
   - 验证数据库用户权限

2. **测试数据未清理**
   - 检查`cleanup_test_data()`是否被调用
   - 手动清理: 删除名称包含"测试"的记录
   - 重置数据库序列

3. **Mock未生效**
   - 检查patch路径是否正确
   - 确保mock在函数调用之前设置
   - 验证mock的side_effect或return_value

4. **断言失败**
   - 检查测试数据是否正确创建
   - 验证业务逻辑是否按预期执行
   - 查看详细的错误堆栈

### 调试技巧

1. **启用详细日志**:
   ```python
   import logging
   logging.basicConfig(level=logging.DEBUG)
   ```

2. **打印中间状态**:
   ```python
   print(f"任务状态: {task.status}")
   print(f"已处理: {task.processed_items}/{task.total_items}")
   ```

3. **使用断点**:
   ```python
   import pdb; pdb.set_trace()
   ```

4. **检查数据库状态**:
   ```sql
   SELECT * FROM classification_tasks WHERE task_name LIKE '%测试%';
   SELECT * FROM classification_plans WHERE plan_name LIKE '%测试%';
   ```

## 持续集成

### CI/CD集成

这些测试可以集成到CI/CD流程中:

```yaml
# .github/workflows/test.yml
name: Integration Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:16
        env:
          POSTGRES_PASSWORD: postgres
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    
    steps:
      - uses: actions/checkout@v2
      
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.12'
      
      - name: Install dependencies
        run: |
          pip install -r backend/requirements.txt
      
      - name: Run integration tests
        run: |
          python run_integration_tests.py
```

### 测试报告

生成测试报告:

```bash
python run_integration_tests.py > test_report.txt 2>&1
```

## 维护指南

### 添加新测试

1. 创建新的测试文件: `test_new_feature.py`
2. 实现`setup_test_data()`和`cleanup_test_data()`
3. 编写测试函数，使用详细的断言
4. 添加到`run_integration_tests.py`

### 更新现有测试

1. 修改测试数据以反映新的业务规则
2. 更新断言以验证新的行为
3. 确保向后兼容性
4. 运行所有测试验证没有破坏现有功能

### 测试最佳实践

1. **独立性**: 每个测试应该独立运行，不依赖其他测试
2. **可重复性**: 测试应该产生一致的结果
3. **清晰性**: 测试名称和断言应该清楚地表达意图
4. **完整性**: 测试应该覆盖正常流程和异常情况
5. **性能**: 使用mock避免真实的外部调用

## 总结

这些集成测试提供了对AI分类模块的全面验证，确保:
- ✅ 所有核心功能正常工作
- ✅ 异常情况得到正确处理
- ✅ 数据完整性得到保证
- ✅ 多租户隔离有效
- ✅ 断点续传可靠

通过定期运行这些测试，可以及早发现问题，确保代码质量。
