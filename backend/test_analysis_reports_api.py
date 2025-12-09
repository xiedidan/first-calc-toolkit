"""
测试科室运营分析报告 API
"""
import requests
import sys

# 配置
BASE_URL = "http://localhost:8000/api/v1"
HOSPITAL_ID = 1  # 测试医疗机构ID

# 登录获取 token
def login():
    """登录获取 token"""
    response = requests.post(
        f"{BASE_URL}/auth/login",
        data={"username": "admin", "password": "admin123"}
    )
    if response.status_code == 200:
        return response.json().get("access_token")
    else:
        print(f"登录失败: {response.status_code} - {response.text}")
        return None


def get_headers(token):
    """获取请求头"""
    return {
        "Authorization": f"Bearer {token}",
        "X-Hospital-ID": str(HOSPITAL_ID)
    }


def test_list_reports(token):
    """测试获取报告列表"""
    print("\n=== 测试获取报告列表 ===")
    response = requests.get(
        f"{BASE_URL}/analysis-reports",
        headers=get_headers(token),
        params={"page": 1, "size": 10}
    )
    print(f"状态码: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"总数: {data.get('total', 0)}")
        print(f"返回项数: {len(data.get('items', []))}")
        return True
    else:
        print(f"错误: {response.text}")
        return False


def test_create_report(token, department_id=1, period="2025-12"):
    """测试创建报告"""
    print("\n=== 测试创建报告 ===")
    response = requests.post(
        f"{BASE_URL}/analysis-reports",
        headers=get_headers(token),
        json={
            "department_id": department_id,
            "period": period,
            "current_issues": "# 当前问题\n\n- 问题1\n- 问题2",
            "future_plans": "# 未来计划\n\n1. 计划1\n2. 计划2"
        }
    )
    print(f"状态码: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"创建成功，报告ID: {data.get('id')}")
        return data.get('id')
    else:
        print(f"错误: {response.text}")
        return None


def test_get_report(token, report_id):
    """测试获取报告详情"""
    print(f"\n=== 测试获取报告详情 (ID: {report_id}) ===")
    response = requests.get(
        f"{BASE_URL}/analysis-reports/{report_id}",
        headers=get_headers(token)
    )
    print(f"状态码: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"报告ID: {data.get('id')}")
        print(f"科室: {data.get('department_name')}")
        print(f"年月: {data.get('period')}")
        return True
    else:
        print(f"错误: {response.text}")
        return False


def test_update_report(token, report_id):
    """测试更新报告"""
    print(f"\n=== 测试更新报告 (ID: {report_id}) ===")
    response = requests.put(
        f"{BASE_URL}/analysis-reports/{report_id}",
        headers=get_headers(token),
        json={
            "current_issues": "# 更新后的问题\n\n- 新问题1\n- 新问题2",
            "future_plans": "# 更新后的计划\n\n1. 新计划1\n2. 新计划2"
        }
    )
    print(f"状态码: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"更新成功")
        return True
    else:
        print(f"错误: {response.text}")
        return False


def test_value_distribution(token, report_id):
    """测试获取价值分布"""
    print(f"\n=== 测试获取价值分布 (ID: {report_id}) ===")
    response = requests.get(
        f"{BASE_URL}/analysis-reports/{report_id}/value-distribution",
        headers=get_headers(token)
    )
    print(f"状态码: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"项目数: {len(data.get('items', []))}")
        print(f"总价值: {data.get('total_value')}")
        if data.get('message'):
            print(f"消息: {data.get('message')}")
        return True
    else:
        print(f"错误: {response.text}")
        return False


def test_business_content(token, report_id):
    """测试获取业务内涵"""
    print(f"\n=== 测试获取业务内涵 (ID: {report_id}) ===")
    response = requests.get(
        f"{BASE_URL}/analysis-reports/{report_id}/business-content",
        headers=get_headers(token)
    )
    print(f"状态码: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"项目数: {len(data.get('items', []))}")
        if data.get('message'):
            print(f"消息: {data.get('message')}")
        return True
    else:
        print(f"错误: {response.text}")
        return False


def test_delete_report(token, report_id):
    """测试删除报告"""
    print(f"\n=== 测试删除报告 (ID: {report_id}) ===")
    response = requests.delete(
        f"{BASE_URL}/analysis-reports/{report_id}",
        headers=get_headers(token)
    )
    print(f"状态码: {response.status_code}")
    if response.status_code == 200:
        print("删除成功")
        return True
    else:
        print(f"错误: {response.text}")
        return False


def test_duplicate_create(token, department_id=1, period="2025-12"):
    """测试重复创建报告（应该失败）"""
    print("\n=== 测试重复创建报告（应该返回400错误）===")
    # 先创建一个
    report_id = test_create_report(token, department_id, period)
    if report_id:
        # 尝试再创建一个相同的
        response = requests.post(
            f"{BASE_URL}/analysis-reports",
            headers=get_headers(token),
            json={
                "department_id": department_id,
                "period": period,
                "current_issues": "重复测试"
            }
        )
        print(f"重复创建状态码: {response.status_code}")
        if response.status_code == 400:
            print("正确：重复创建被拒绝")
            # 清理
            test_delete_report(token, report_id)
            return True
        else:
            print(f"错误：应该返回400，实际返回 {response.status_code}")
            test_delete_report(token, report_id)
            return False
    return False


def test_content_length_validation(token, department_id=1):
    """测试内容长度验证"""
    print("\n=== 测试内容长度验证（超过2000字符应该失败）===")
    long_content = "x" * 2001
    response = requests.post(
        f"{BASE_URL}/analysis-reports",
        headers=get_headers(token),
        json={
            "department_id": department_id,
            "period": "2025-11",
            "current_issues": long_content
        }
    )
    print(f"状态码: {response.status_code}")
    if response.status_code == 422:
        print("正确：超长内容被拒绝")
        return True
    else:
        print(f"错误：应该返回422，实际返回 {response.status_code}")
        return False


def main():
    """主测试函数"""
    print("=" * 50)
    print("科室运营分析报告 API 测试")
    print("=" * 50)
    
    # 登录
    token = login()
    if not token:
        print("登录失败，无法继续测试")
        sys.exit(1)
    
    print(f"登录成功，获取到 token")
    
    # 测试列表
    test_list_reports(token)
    
    # 测试内容长度验证
    test_content_length_validation(token)
    
    # 测试重复创建
    test_duplicate_create(token)
    
    # 完整 CRUD 测试
    print("\n" + "=" * 50)
    print("完整 CRUD 测试")
    print("=" * 50)
    
    # 创建
    report_id = test_create_report(token, period="2025-10")
    if report_id:
        # 获取详情
        test_get_report(token, report_id)
        
        # 更新
        test_update_report(token, report_id)
        
        # 获取价值分布
        test_value_distribution(token, report_id)
        
        # 获取业务内涵
        test_business_content(token, report_id)
        
        # 删除
        test_delete_report(token, report_id)
    
    print("\n" + "=" * 50)
    print("测试完成")
    print("=" * 50)


if __name__ == "__main__":
    main()
