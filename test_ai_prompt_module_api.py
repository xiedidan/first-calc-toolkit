"""
测试AI提示词模块API

验证提示词模块的CRUD操作
"""
import requests
import json
import sys

# API配置
BASE_URL = "http://localhost:8000/api/v1"
HOSPITAL_ID = 1  # 测试用医疗机构ID

# 请求头
HEADERS = {
    "Content-Type": "application/json",
    "X-Hospital-ID": str(HOSPITAL_ID),
}


def get_auth_token():
    """获取认证token"""
    login_data = {
        "username": "maintainer",  # 使用maintainer用户
        "password": "maintainer123"
    }
    response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    if response.status_code == 200:
        data = response.json()
        return data.get("data", {}).get("access_token")
    else:
        print(f"登录失败: {response.status_code}")
        print(response.text)
        return None


def test_list_prompt_modules(token):
    """测试获取提示词模块列表"""
    print("\n=== 测试获取提示词模块列表 ===")
    
    headers = {**HEADERS, "Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/ai-prompt-modules", headers=headers)
    
    print(f"状态码: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        items = data.get("data", {}).get("items", [])
        total = data.get("data", {}).get("total", 0)
        print(f"总数: {total}")
        
        for item in items:
            print(f"  - {item['module_code']}: {item['module_name']}")
            print(f"    已配置AI接口: {item['is_configured']}")
            print(f"    温度: {item['temperature']}")
        
        return items
    else:
        print(f"错误: {response.text}")
        return []


def test_get_prompt_module(token, module_code):
    """测试获取单个提示词模块"""
    print(f"\n=== 测试获取提示词模块: {module_code} ===")
    
    headers = {**HEADERS, "Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/ai-prompt-modules/{module_code}", headers=headers)
    
    print(f"状态码: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        module = data.get("data", {})
        print(f"模块代码: {module.get('module_code')}")
        print(f"模块名称: {module.get('module_name')}")
        print(f"描述: {module.get('description', '')[:50]}...")
        print(f"温度: {module.get('temperature')}")
        print(f"占位符数量: {len(module.get('placeholders', []))}")
        print(f"系统提示词长度: {len(module.get('system_prompt', '') or '')}")
        print(f"用户提示词长度: {len(module.get('user_prompt', ''))}")
        return module
    else:
        print(f"错误: {response.text}")
        return None


def test_update_prompt_module(token, module_code):
    """测试更新提示词模块"""
    print(f"\n=== 测试更新提示词模块: {module_code} ===")
    
    headers = {**HEADERS, "Authorization": f"Bearer {token}"}
    
    # 更新温度
    update_data = {
        "temperature": 0.5,
    }
    
    response = requests.put(
        f"{BASE_URL}/ai-prompt-modules/{module_code}",
        headers=headers,
        json=update_data
    )
    
    print(f"状态码: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        module = data.get("data", {})
        print(f"更新后温度: {module.get('temperature')}")
        
        # 恢复原值
        restore_data = {"temperature": 0.3}
        requests.put(
            f"{BASE_URL}/ai-prompt-modules/{module_code}",
            headers=headers,
            json=restore_data
        )
        print("已恢复原值")
        return True
    else:
        print(f"错误: {response.text}")
        return False


def test_update_with_invalid_interface(token, module_code):
    """测试使用无效AI接口更新"""
    print(f"\n=== 测试使用无效AI接口更新 ===")
    
    headers = {**HEADERS, "Authorization": f"Bearer {token}"}
    
    update_data = {
        "ai_interface_id": 99999,  # 不存在的接口ID
    }
    
    response = requests.put(
        f"{BASE_URL}/ai-prompt-modules/{module_code}",
        headers=headers,
        json=update_data
    )
    
    print(f"状态码: {response.status_code}")
    
    if response.status_code == 400:
        print("正确返回400错误（无效的AI接口）")
        return True
    else:
        print(f"响应: {response.text}")
        return False


def test_get_nonexistent_module(token):
    """测试获取不存在的模块"""
    print("\n=== 测试获取不存在的模块 ===")
    
    headers = {**HEADERS, "Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/ai-prompt-modules/nonexistent_module", headers=headers)
    
    print(f"状态码: {response.status_code}")
    
    if response.status_code == 404:
        print("正确返回404错误")
        return True
    else:
        print(f"响应: {response.text}")
        return False


def main():
    """主测试函数"""
    print("=" * 60)
    print("AI提示词模块API测试")
    print("=" * 60)
    
    # 获取认证token
    print("\n获取认证token...")
    token = get_auth_token()
    
    if not token:
        print("无法获取认证token，请确保:")
        print("1. 后端服务正在运行")
        print("2. maintainer用户存在且密码正确")
        sys.exit(1)
    
    print(f"Token获取成功: {token[:20]}...")
    
    # 运行测试
    results = []
    
    # 测试1: 获取模块列表
    modules = test_list_prompt_modules(token)
    results.append(("获取模块列表", len(modules) > 0))
    
    if modules:
        # 测试2: 获取单个模块
        module_code = modules[0]["module_code"]
        module = test_get_prompt_module(token, module_code)
        results.append(("获取单个模块", module is not None))
        
        # 测试3: 更新模块
        success = test_update_prompt_module(token, module_code)
        results.append(("更新模块", success))
        
        # 测试4: 使用无效AI接口更新
        success = test_update_with_invalid_interface(token, module_code)
        results.append(("无效AI接口验证", success))
    
    # 测试5: 获取不存在的模块
    success = test_get_nonexistent_module(token)
    results.append(("不存在模块404", success))
    
    # 打印测试结果
    print("\n" + "=" * 60)
    print("测试结果汇总")
    print("=" * 60)
    
    all_passed = True
    for name, passed in results:
        status = "✓ 通过" if passed else "✗ 失败"
        print(f"  {name}: {status}")
        if not passed:
            all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("所有测试通过！")
    else:
        print("部分测试失败，请检查日志")
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
