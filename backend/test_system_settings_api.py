"""
系统设置API测试脚本
"""
import requests
import json

BASE_URL = "http://localhost:8000/api/v1"


def test_get_system_settings():
    """测试获取系统设置"""
    print("\n=== 测试获取系统设置 ===")
    
    response = requests.get(f"{BASE_URL}/system/settings")
    print(f"状态码: {response.status_code}")
    print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    
    return response.json()


def test_update_system_settings():
    """测试更新系统设置"""
    print("\n=== 测试更新系统设置 ===")
    
    data = {
        "current_period": "2025-10",
        "system_name": "医院科室业务价值评估工具 v2"
    }
    
    response = requests.put(
        f"{BASE_URL}/system/settings",
        json=data
    )
    print(f"状态码: {response.status_code}")
    print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    
    return response.json()


def test_update_current_period_only():
    """测试只更新当期年月"""
    print("\n=== 测试只更新当期年月 ===")
    
    data = {
        "current_period": "2025-11"
    }
    
    response = requests.put(
        f"{BASE_URL}/system/settings",
        json=data
    )
    print(f"状态码: {response.status_code}")
    print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    
    return response.json()


def test_invalid_period_format():
    """测试无效的年月格式"""
    print("\n=== 测试无效的年月格式 ===")
    
    data = {
        "current_period": "2025-13"  # 无效月份
    }
    
    response = requests.put(
        f"{BASE_URL}/system/settings",
        json=data
    )
    print(f"状态码: {response.status_code}")
    print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")


def main():
    """主函数"""
    print("=" * 60)
    print("系统设置API测试")
    print("=" * 60)
    
    try:
        # 1. 获取系统设置
        test_get_system_settings()
        
        # 2. 更新系统设置
        test_update_system_settings()
        
        # 3. 再次获取验证
        test_get_system_settings()
        
        # 4. 只更新当期年月
        test_update_current_period_only()
        
        # 5. 再次获取验证
        test_get_system_settings()
        
        # 6. 测试无效格式
        test_invalid_period_format()
        
        print("\n" + "=" * 60)
        print("测试完成！")
        print("=" * 60)
        
    except requests.exceptions.ConnectionError:
        print("\n错误: 无法连接到服务器，请确保后端服务正在运行")
    except Exception as e:
        print(f"\n错误: {str(e)}")


if __name__ == "__main__":
    main()
