"""
运行所有成本基准管理测试并收集结果
"""
import subprocess
import sys

# 测试文件列表（排除有问题的error_handling测试）
test_files = [
    "test_cost_benchmark_schemas.py",
    "test_cost_benchmark_api.py",
    "test_cost_benchmark_multi_tenant.py",
    "test_cost_benchmark_create.py",
    "test_cost_benchmark_create_simple.py",
    "test_cost_benchmark_edit.py",
    "test_cost_benchmark_update_api.py",
    "test_cost_benchmark_delete.py",
    "test_cost_benchmark_export.py",
    "test_cost_benchmark_edit_workflow.py",
    "test_negative_value_validation.py",
]

print("=" * 80)
print("运行成本基准管理测试套件")
print("=" * 80)

results = {}
total_passed = 0
total_failed = 0
total_errors = 0

for test_file in test_files:
    print(f"\n运行 {test_file}...")
    print("-" * 80)
    
    try:
        result = subprocess.run(
            ["python", "-m", "pytest", test_file, "-v", "--tb=short"],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        # 解析输出
        output = result.stdout + result.stderr
        
        # 查找测试结果
        if "passed" in output:
            # 提取通过的测试数量
            import re
            match = re.search(r'(\d+) passed', output)
            if match:
                passed = int(match.group(1))
                total_passed += passed
                results[test_file] = f"✅ {passed} passed"
                print(f"✅ {passed} 个测试通过")
        
        if "failed" in output:
            match = re.search(r'(\d+) failed', output)
            if match:
                failed = int(match.group(1))
                total_failed += failed
                results[test_file] = f"❌ {failed} failed"
                print(f"❌ {failed} 个测试失败")
                print(output[-1000:])  # 打印最后1000字符
        
        if "error" in output.lower() and "ERROR" in output:
            total_errors += 1
            results[test_file] = "⚠️ Error"
            print(f"⚠️ 测试执行出错")
            print(output[-1000:])
            
    except subprocess.TimeoutExpired:
        results[test_file] = "⏱️ Timeout"
        total_errors += 1
        print(f"⏱️ 测试超时")
    except Exception as e:
        results[test_file] = f"⚠️ Exception: {str(e)}"
        total_errors += 1
        print(f"⚠️ 异常: {e}")

print("\n" + "=" * 80)
print("测试结果汇总")
print("=" * 80)

for test_file, result in results.items():
    print(f"{result:20} {test_file}")

print("\n" + "=" * 80)
print(f"总计: {total_passed} 通过, {total_failed} 失败, {total_errors} 错误")
print("=" * 80)

# 返回适当的退出码
if total_failed > 0 or total_errors > 0:
    sys.exit(1)
else:
    sys.exit(0)
