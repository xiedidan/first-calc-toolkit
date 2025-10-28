"""
计算流程管理集成测试
测试前后端API联调，包括完整的业务流程
"""
import requests
import json
import time
from typing import Dict, Any, Optional

# 配置
BASE_URL = "http://localhost:8000"
API_PREFIX = "/api/v1"

# 测试用户凭证
TEST_USER = {
    "username": "admin",
    "password": "admin123"
}

# 全局变量
token = None
headers = {}
test_data = {
    "version_id": None,
    "workflow_id": None,
    "workflow_copy_id": None,
    "step_ids": []
}


class Colors:
    """终端颜色"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'


def print_section(title: str):
    """打印章节标题"""
    print(f"\n{Colors.BLUE}{'=' * 70}{Colors.END}")
    print(f"{Colors.BLUE}{title}{Colors.END}")
    print(f"{Colors.BLUE}{'=' * 70}{Colors.END}")


def print_test(name: str):
    """打印测试名称"""
    print(f"\n{Colors.YELLOW}>>> {name}{Colors.END}")


def print_success(message: str):
    """打印成功消息"""
    print(f"{Colors.GREEN}✓ {message}{Colors.END}")


def print_error(message: str):
    """打印错误消息"""
    print(f"{Colors.RED}✗ {message}{Colors.END}")


def print_response(response: requests.Response):
    """打印响应信息"""
    print(f"状态码: {response.status_code}")
    try:
        data = response.json()
        print(f"响应: {json.dumps(data, indent=2, ensure_ascii=False)}")
    except:
        print(f"响应: {response.text}")


def login() -> bool:
    """登录获取token"""
    global token, headers
    print_test("用户登录")
    
    try:
        response = requests.post(
            f"{BASE_URL}{API_PREFIX}/auth/login",
            json=TEST_USER
        )
        
        if response.status_code == 200:
            data = response.json()
            token = data.get("access_token")
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
            print_success(f"登录成功，Token: {token[:30]}...")
            return True
        else:
            print_error(f"登录失败: {response.text}")
            return False
    except Exception as e:
        print_error(f"登录异常: {e}")
        return False


def get_or_create_version() -> bool:
    """获取或创建测试用的模型版本"""
    global test_data
    print_test("获取模型版本")
    
    try:
        # 先尝试获取版本列表
        response = requests.get(
            f"{BASE_URL}{API_PREFIX}/model-versions",
            headers=headers
        )
        
        if response.status_code == 200:
            versions = response.json()
            if versions:
                test_data["version_id"] = versions[0]["id"]
                print_success(f"使用现有版本，ID: {test_data['version_id']}")
                return True
        
        # 如果没有版本，创建一个
        print("没有找到版本，尝试创建...")
        response = requests.post(
            f"{BASE_URL}{API_PREFIX}/model-versions",
            headers=headers,
            json={
                "name": "测试版本",
                "description": "用于集成测试的版本",
                "is_active": True
            }
        )
        
        if response.status_code == 201:
            test_data["version_id"] = response.json()["id"]
            print_success(f"创建版本成功，ID: {test_data['version_id']}")
            return True
        else:
            print_error(f"创建版本失败: {response.text}")
            return False
            
    except Exception as e:
        print_error(f"获取版本异常: {e}")
        return False


def test_create_workflow() -> bool:
    """测试创建计算流程"""
    global test_data
    print_test("创建计算流程")
    
    workflow_data = {
        "version_id": test_data["version_id"],
        "name": f"集成测试流程_{int(time.time())}",
        "description": "这是一个完整的集成测试流程，包含多个计算步骤",
        "is_active": True
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}{API_PREFIX}/calculation-workflows",
            headers=headers,
            json=workflow_data
        )
        
        print_response(response)
        
        if response.status_code == 201:
            test_data["workflow_id"] = response.json()["id"]
            print_success(f"创建流程成功，ID: {test_data['workflow_id']}")
            return True
        else:
            print_error("创建流程失败")
            return False
    except Exception as e:
        print_error(f"创建流程异常: {e}")
        return False


def test_create_steps() -> bool:
    """测试创建多个计算步骤"""
    global test_data
    print_test("创建计算步骤")
    
    steps = [
        {
            "workflow_id": test_data["workflow_id"],
            "name": "步骤1: 数据准备",
            "description": "准备基础数据，查询科室信息",
            "code_type": "sql",
            "code_content": """
-- 查询所有启用的科室
SELECT 
    id,
    code,
    name,
    parent_id
FROM departments 
WHERE is_active = true
ORDER BY code
            """.strip(),
            "is_enabled": True
        },
        {
            "workflow_id": test_data["workflow_id"],
            "name": "步骤2: 计算工作量",
            "description": "计算各科室的工作量指标",
            "code_type": "sql",
            "code_content": """
-- 计算工作量（示例）
SELECT 
    department_id,
    COUNT(*) as workload_count,
    SUM(value) as total_value
FROM charge_items
WHERE year_month = '{current_year_month}'
GROUP BY department_id
            """.strip(),
            "is_enabled": True
        },
        {
            "workflow_id": test_data["workflow_id"],
            "name": "步骤3: 数据处理",
            "description": "使用Python处理计算结果",
            "code_type": "python",
            "code_content": """
# 数据处理示例
def process_data(data):
    result = []
    for item in data:
        processed = {
            'department_id': item['department_id'],
            'score': item['total_value'] * 1.2,
            'level': 'A' if item['total_value'] > 1000 else 'B'
        }
        result.append(processed)
    return result

# 执行处理
output = process_data(input_data)
            """.strip(),
            "is_enabled": True
        },
        {
            "workflow_id": test_data["workflow_id"],
            "name": "步骤4: 结果汇总",
            "description": "汇总最终结果",
            "code_type": "sql",
            "code_content": """
-- 汇总结果
SELECT 
    d.name as department_name,
    r.score,
    r.level
FROM results r
JOIN departments d ON r.department_id = d.id
ORDER BY r.score DESC
            """.strip(),
            "is_enabled": True
        }
    ]
    
    success_count = 0
    for i, step_data in enumerate(steps, 1):
        try:
            response = requests.post(
                f"{BASE_URL}{API_PREFIX}/calculation-steps",
                headers=headers,
                json=step_data
            )
            
            if response.status_code == 201:
                step_id = response.json()["id"]
                test_data["step_ids"].append(step_id)
                print_success(f"创建步骤 {i} 成功，ID: {step_id}")
                success_count += 1
            else:
                print_error(f"创建步骤 {i} 失败: {response.text}")
        except Exception as e:
            print_error(f"创建步骤 {i} 异常: {e}")
    
    return success_count == len(steps)


def test_get_workflow_detail() -> bool:
    """测试获取流程详情（包含步骤）"""
    print_test("获取流程详情")
    
    try:
        response = requests.get(
            f"{BASE_URL}{API_PREFIX}/calculation-workflows/{test_data['workflow_id']}",
            headers=headers
        )
        
        print_response(response)
        
        if response.status_code == 200:
            data = response.json()
            steps_count = len(data.get("steps", []))
            print_success(f"获取流程详情成功，包含 {steps_count} 个步骤")
            return True
        else:
            print_error("获取流程详情失败")
            return False
    except Exception as e:
        print_error(f"获取流程详情异常: {e}")
        return False


def test_update_workflow() -> bool:
    """测试更新流程"""
    print_test("更新流程信息")
    
    update_data = {
        "name": f"集成测试流程_{int(time.time())}_已更新",
        "description": "更新后的描述信息",
        "is_active": True
    }
    
    try:
        response = requests.put(
            f"{BASE_URL}{API_PREFIX}/calculation-workflows/{test_data['workflow_id']}",
            headers=headers,
            json=update_data
        )
        
        print_response(response)
        
        if response.status_code == 200:
            print_success("更新流程成功")
            return True
        else:
            print_error("更新流程失败")
            return False
    except Exception as e:
        print_error(f"更新流程异常: {e}")
        return False


def test_move_steps() -> bool:
    """测试移动步骤顺序"""
    print_test("测试步骤排序")
    
    if len(test_data["step_ids"]) < 2:
        print_error("步骤数量不足，跳过排序测试")
        return False
    
    # 获取第一个步骤
    first_step_id = test_data["step_ids"][0]
    
    try:
        # 下移第一个步骤
        response = requests.post(
            f"{BASE_URL}{API_PREFIX}/calculation-steps/{first_step_id}/move-down",
            headers=headers
        )
        
        if response.status_code == 200:
            print_success("下移步骤成功")
        else:
            print_error(f"下移步骤失败: {response.text}")
            return False
        
        # 上移回去
        response = requests.post(
            f"{BASE_URL}{API_PREFIX}/calculation-steps/{first_step_id}/move-up",
            headers=headers
        )
        
        if response.status_code == 200:
            print_success("上移步骤成功")
            return True
        else:
            print_error(f"上移步骤失败: {response.text}")
            return False
            
    except Exception as e:
        print_error(f"移动步骤异常: {e}")
        return False


def test_update_step() -> bool:
    """测试更新步骤"""
    print_test("更新步骤信息")
    
    if not test_data["step_ids"]:
        print_error("没有可用的步骤ID")
        return False
    
    step_id = test_data["step_ids"][0]
    update_data = {
        "name": "步骤1: 数据准备（已更新）",
        "description": "更新后的步骤描述",
        "is_enabled": True
    }
    
    try:
        response = requests.put(
            f"{BASE_URL}{API_PREFIX}/calculation-steps/{step_id}",
            headers=headers,
            json=update_data
        )
        
        print_response(response)
        
        if response.status_code == 200:
            print_success("更新步骤成功")
            return True
        else:
            print_error("更新步骤失败")
            return False
    except Exception as e:
        print_error(f"更新步骤异常: {e}")
        return False


def test_code_execution() -> bool:
    """测试代码测试功能"""
    print_test("测试代码执行")
    
    if not test_data["step_ids"]:
        print_error("没有可用的步骤ID")
        return False
    
    step_id = test_data["step_ids"][0]
    test_params = {
        "test_params": {
            "current_year_month": "2025-10",
            "department_id": 1
        }
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}{API_PREFIX}/calculation-steps/{step_id}/test",
            headers=headers,
            json=test_params
        )
        
        print_response(response)
        
        if response.status_code == 200:
            print_success("代码测试成功")
            return True
        else:
            print_error("代码测试失败")
            return False
    except Exception as e:
        print_error(f"代码测试异常: {e}")
        return False


def test_copy_workflow() -> bool:
    """测试复制流程"""
    global test_data
    print_test("复制流程")
    
    copy_data = {
        "name": f"集成测试流程_副本_{int(time.time())}",
        "description": "这是复制的流程"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}{API_PREFIX}/calculation-workflows/{test_data['workflow_id']}/copy",
            headers=headers,
            json=copy_data
        )
        
        print_response(response)
        
        if response.status_code == 200:
            test_data["workflow_copy_id"] = response.json()["id"]
            print_success(f"复制流程成功，新流程ID: {test_data['workflow_copy_id']}")
            return True
        else:
            print_error("复制流程失败")
            return False
    except Exception as e:
        print_error(f"复制流程异常: {e}")
        return False


def test_list_workflows() -> bool:
    """测试获取流程列表"""
    print_test("获取流程列表")
    
    try:
        response = requests.get(
            f"{BASE_URL}{API_PREFIX}/calculation-workflows",
            headers=headers,
            params={"version_id": test_data["version_id"]}
        )
        
        print_response(response)
        
        if response.status_code == 200:
            workflows = response.json()
            print_success(f"获取流程列表成功，共 {len(workflows)} 个流程")
            return True
        else:
            print_error("获取流程列表失败")
            return False
    except Exception as e:
        print_error(f"获取流程列表异常: {e}")
        return False


def test_list_steps() -> bool:
    """测试获取步骤列表"""
    print_test("获取步骤列表")
    
    try:
        response = requests.get(
            f"{BASE_URL}{API_PREFIX}/calculation-steps",
            headers=headers,
            params={"workflow_id": test_data["workflow_id"]}
        )
        
        print_response(response)
        
        if response.status_code == 200:
            steps = response.json()
            print_success(f"获取步骤列表成功，共 {len(steps)} 个步骤")
            return True
        else:
            print_error("获取步骤列表失败")
            return False
    except Exception as e:
        print_error(f"获取步骤列表异常: {e}")
        return False


def cleanup_test_data() -> bool:
    """清理测试数据"""
    print_test("清理测试数据")
    
    success = True
    
    # 删除复制的流程
    if test_data.get("workflow_copy_id"):
        try:
            response = requests.delete(
                f"{BASE_URL}{API_PREFIX}/calculation-workflows/{test_data['workflow_copy_id']}",
                headers=headers
            )
            if response.status_code == 204:
                print_success(f"删除复制流程成功 (ID: {test_data['workflow_copy_id']})")
            else:
                print_error(f"删除复制流程失败: {response.text}")
                success = False
        except Exception as e:
            print_error(f"删除复制流程异常: {e}")
            success = False
    
    # 删除原始流程（会级联删除步骤）
    if test_data.get("workflow_id"):
        try:
            response = requests.delete(
                f"{BASE_URL}{API_PREFIX}/calculation-workflows/{test_data['workflow_id']}",
                headers=headers
            )
            if response.status_code == 204:
                print_success(f"删除原始流程成功 (ID: {test_data['workflow_id']})")
            else:
                print_error(f"删除原始流程失败: {response.text}")
                success = False
        except Exception as e:
            print_error(f"删除原始流程异常: {e}")
            success = False
    
    return success


def main():
    """主测试流程"""
    print_section("计算流程管理 - 集成测试")
    print(f"测试服务器: {BASE_URL}")
    print(f"测试用户: {TEST_USER['username']}")
    
    # 测试用例列表
    test_cases = [
        ("用户登录", login),
        ("获取模型版本", get_or_create_version),
        ("创建计算流程", test_create_workflow),
        ("创建计算步骤", test_create_steps),
        ("获取流程详情", test_get_workflow_detail),
        ("更新流程信息", test_update_workflow),
        ("更新步骤信息", test_update_step),
        ("测试步骤排序", test_move_steps),
        ("测试代码执行", test_code_execution),
        ("复制流程", test_copy_workflow),
        ("获取流程列表", test_list_workflows),
        ("获取步骤列表", test_list_steps),
    ]
    
    # 执行测试
    results = []
    for test_name, test_func in test_cases:
        try:
            result = test_func()
            results.append((test_name, result))
            if not result:
                print_error(f"测试失败: {test_name}")
                # 继续执行其他测试
        except Exception as e:
            print_error(f"测试异常: {test_name} - {e}")
            results.append((test_name, False))
    
    # 清理测试数据
    print_section("清理测试数据")
    cleanup_result = cleanup_test_data()
    results.append(("清理测试数据", cleanup_result))
    
    # 打印测试结果汇总
    print_section("测试结果汇总")
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = f"{Colors.GREEN}✓{Colors.END}" if result else f"{Colors.RED}✗{Colors.END}"
        print(f"{status} {test_name}")
    
    print(f"\n通过: {passed}/{total}")
    
    if passed == total:
        print_success("所有测试通过！")
    else:
        print_error(f"有 {total - passed} 个测试失败")
    
    return passed == total


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)