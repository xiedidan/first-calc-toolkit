"""
集成测试运行器

运行所有AI分类集成测试:
1. AI接口集成测试
2. 端到端分类流程测试
3. 断点续传场景测试
"""

import sys
import subprocess


def run_test(test_file, test_name):
    """运行单个测试文件"""
    print(f"\n{'='*80}")
    print(f"运行测试: {test_name}")
    print(f"文件: {test_file}")
    print(f"{'='*80}\n")
    
    try:
        result = subprocess.run(
            [sys.executable, test_file],
            capture_output=False,
            text=True
        )
        
        return result.returncode == 0
        
    except Exception as e:
        print(f"✗ 运行测试时出错: {e}")
        return False


def main():
    """运行所有集成测试"""
    print("\n" + "="*80)
    print("AI分类集成测试套件")
    print("="*80)
    
    tests = [
        ("test_ai_interface_integration.py", "AI接口集成测试"),
        ("test_e2e_classification_flow.py", "端到端分类流程测试"),
        ("test_breakpoint_resume.py", "断点续传场景测试")
    ]
    
    results = []
    
    for test_file, test_name in tests:
        success = run_test(test_file, test_name)
        results.append((test_name, success))
    
    # 汇总结果
    print("\n" + "="*80)
    print("测试结果汇总")
    print("="*80)
    
    for name, success in results:
        status = "✓ 通过" if success else "✗ 失败"
        print(f"{status} - {name}")
    
    all_passed = all(success for _, success in results)
    
    if all_passed:
        print("\n" + "="*80)
        print("✓ 所有集成测试通过！")
        print("="*80)
        return 0
    else:
        print("\n" + "="*80)
        print("✗ 部分测试失败")
        print("="*80)
        return 1


if __name__ == "__main__":
    sys.exit(main())
