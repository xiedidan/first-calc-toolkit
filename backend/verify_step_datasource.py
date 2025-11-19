"""验证步骤与数据源集成的代码完整性"""
import sys
import os

def check_file_exists(filepath, description):
    """检查文件是否存在"""
    if os.path.exists(filepath):
        print(f"✓ {description}: {filepath}")
        return True
    else:
        print(f"✗ {description} 不存在: {filepath}")
        return False

def check_code_content(filepath, search_strings, description):
    """检查文件中是否包含特定内容"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            all_found = True
            for search_str in search_strings:
                if search_str in content:
                    print(f"  ✓ 包含: {search_str[:50]}...")
                else:
                    print(f"  ✗ 缺失: {search_str[:50]}...")
                    all_found = False
            return all_found
    except Exception as e:
        print(f"  ✗ 读取文件失败: {e}")
        return False

def main():
    print("=" * 70)
    print("验证步骤与数据源集成")
    print("=" * 70)
    
    all_checks_passed = True
    
    # 1. 检查迁移文件
    print("\n1. 检查数据库迁移文件...")
    migration_file = "alembic/versions/add_datasource_to_steps.py"
    if check_file_exists(migration_file, "迁移文件"):
        check_code_content(
            migration_file,
            ["data_source_id", "python_env", "fk_calculation_steps_data_source_id"],
            "迁移文件内容"
        )
    else:
        all_checks_passed = False
    
    # 2. 检查模型文件
    print("\n2. 检查步骤模型...")
    model_file = "app/models/calculation_step.py"
    if check_file_exists(model_file, "模型文件"):
        if not check_code_content(
            model_file,
            [
                "data_source_id = Column",
                "python_env = Column",
                'relationship("DataSource"'
            ],
            "模型文件内容"
        ):
            all_checks_passed = False
    else:
        all_checks_passed = False
    
    # 3. 检查 Schema 文件
    print("\n3. 检查步骤 Schema...")
    schema_file = "app/schemas/calculation_step.py"
    if check_file_exists(schema_file, "Schema 文件"):
        if not check_code_content(
            schema_file,
            [
                "data_source_id: Optional[int]",
                "python_env: Optional[str]",
                "data_source_name: Optional[str]"
            ],
            "Schema 文件内容"
        ):
            all_checks_passed = False
    else:
        all_checks_passed = False
    
    # 4. 检查 API 文件
    print("\n4. 检查步骤 API...")
    api_file = "app/api/calculation_steps.py"
    if check_file_exists(api_file, "API 文件"):
        if not check_code_content(
            api_file,
            [
                "from app.models.data_source import DataSource",
                "from app.services.data_source_service import DataSourceService",
                "if step.code_type == 'sql':",
                "data_source_service.get_connection",
                "data_source_name"
            ],
            "API 文件内容"
        ):
            all_checks_passed = False
    else:
        all_checks_passed = False
    
    # 5. 检查前端 API 类型定义
    print("\n5. 检查前端 API 类型定义...")
    frontend_api_file = "../frontend/src/api/calculation-workflow.ts"
    if check_file_exists(frontend_api_file, "前端 API 文件"):
        if not check_code_content(
            frontend_api_file,
            [
                "data_source_id?: number",
                "data_source_name?: string",
                "python_env?: string"
            ],
            "前端 API 类型定义"
        ):
            all_checks_passed = False
    else:
        all_checks_passed = False
    
    # 6. 检查前端组件
    print("\n6. 检查前端组件...")
    frontend_component_file = "../frontend/src/views/CalculationWorkflows.vue"
    if check_file_exists(frontend_component_file, "前端组件文件"):
        if not check_code_content(
            frontend_component_file,
            [
                "dataSourceList",
                "data_source_id",
                "python_env",
                "loadDataSources",
                "handleCodeTypeChange"
            ],
            "前端组件内容"
        ):
            all_checks_passed = False
    else:
        all_checks_passed = False
    
    # 7. 检查测试文件
    print("\n7. 检查测试文件...")
    test_file = "test_step_integration.py"
    if check_file_exists(test_file, "集成测试文件"):
        print("  ✓ 集成测试脚本已创建")
    else:
        print("  ⚠ 集成测试脚本不存在（可选）")
    
    # 总结
    print("\n" + "=" * 70)
    if all_checks_passed:
        print("✓ 所有检查通过！")
        print("\n下一步:")
        print("1. 确保后端服务运行: uvicorn app.main:app --reload")
        print("2. 确保前端服务运行: npm run dev")
        print("3. 运行集成测试: python test_step_integration.py")
        print("4. 或手动测试前端界面")
    else:
        print("✗ 部分检查未通过，请检查上述错误")
        sys.exit(1)
    print("=" * 70)

if __name__ == "__main__":
    main()
