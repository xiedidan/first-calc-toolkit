"""
测试导向规则导出API
"""
import requests
from datetime import datetime

# API基础URL
BASE_URL = "http://localhost:8000/api/v1"

# 测试用户凭证
USERNAME = "admin"
PASSWORD = "admin123"


def get_auth_token():
    """获取认证token"""
    response = requests.post(
        f"{BASE_URL}/auth/login",
        json={"username": USERNAME, "password": PASSWORD}
    )
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        raise Exception(f"登录失败: {response.text}")


def test_export_api():
    """测试导出API"""
    print("\n=== 测试导向规则导出API ===")
    
    # 获取token
    token = get_auth_token()
    headers = {
        "Authorization": f"Bearer {token}",
        "X-Hospital-ID": "1"
    }
    
    # 创建测试导向规则
    print("\n1. 创建测试导向规则...")
    create_data = {
        "name": f"API导出测试_{datetime.now().strftime('%H%M%S')}",
        "category": "benchmark_ladder",
        "description": "用于测试API导出功能"
    }
    
    response = requests.post(
        f"{BASE_URL}/orientation-rules",
        json=create_data,
        headers=headers
    )
    
    if response.status_code != 200:
        print(f"✗ 创建失败: {response.text}")
        return
    
    rule = response.json()
    rule_id = rule["id"]
    print(f"✓ 创建成功: ID={rule_id}, 名称={rule['name']}")
    
    # 添加基准数据
    print("\n2. 添加导向基准...")
    benchmark_data = {
        "rule_id": rule_id,
        "department_code": "TEST001",
        "department_name": "测试科室",
        "benchmark_type": "average",
        "control_intensity": 0.85,
        "stat_start_date": "2024-01-01T00:00:00",
        "stat_end_date": "2024-12-31T23:59:59",
        "benchmark_value": 1000.0
    }
    
    response = requests.post(
        f"{BASE_URL}/orientation-benchmarks",
        json=benchmark_data,
        headers=headers
    )
    
    if response.status_code == 200:
        print(f"✓ 添加基准成功")
    else:
        print(f"⚠ 添加基准失败（可能API未实现）: {response.status_code}")
    
    # 添加阶梯数据
    print("\n3. 添加导向阶梯...")
    ladder_data = {
        "rule_id": rule_id,
        "ladder_order": 1,
        "lower_limit": None,
        "upper_limit": 0.8,
        "adjustment_intensity": 0.5
    }
    
    response = requests.post(
        f"{BASE_URL}/orientation-ladders",
        json=ladder_data,
        headers=headers
    )
    
    if response.status_code == 200:
        print(f"✓ 添加阶梯成功")
    else:
        print(f"⚠ 添加阶梯失败（可能API未实现）: {response.status_code}")
    
    # 导出规则
    print("\n4. 导出导向规则...")
    response = requests.get(
        f"{BASE_URL}/orientation-rules/{rule_id}/export",
        headers=headers
    )
    
    if response.status_code != 200:
        print(f"✗ 导出失败: {response.status_code} - {response.text}")
        return
    
    print(f"✓ 导出成功")
    print(f"  - 状态码: {response.status_code}")
    print(f"  - Content-Type: {response.headers.get('Content-Type')}")
    print(f"  - Content-Disposition: {response.headers.get('Content-Disposition')}")
    print(f"  - 内容长度: {len(response.content)} 字节")
    
    # 解析文件名
    content_disposition = response.headers.get('Content-Disposition', '')
    if 'filename*=' in content_disposition:
        # 提取URL编码的文件名
        filename_part = content_disposition.split('filename*=')[1]
        if filename_part.startswith("UTF-8''"):
            from urllib.parse import unquote
            encoded_filename = filename_part.replace("UTF-8''", "")
            filename = unquote(encoded_filename)
            print(f"  - 文件名: {filename}")
    
    # 显示内容预览
    content = response.content.decode('utf-8')
    print(f"\n--- Markdown 内容预览 ---")
    print(content[:500])
    if len(content) > 500:
        print("...")
    
    # 验证内容
    assert rule['name'] in content, "内容应包含导向名称"
    assert "基准阶梯" in content, "内容应包含导向类别"
    print("\n✓ 内容验证通过")
    
    # 清理测试数据
    print("\n5. 清理测试数据...")
    response = requests.delete(
        f"{BASE_URL}/orientation-rules/{rule_id}",
        headers=headers
    )
    
    if response.status_code == 200:
        print("✓ 清理完成")
    else:
        print(f"⚠ 清理失败: {response.status_code}")


def test_export_nonexistent_rule():
    """测试导出不存在的规则"""
    print("\n=== 测试导出不存在的规则 ===")
    
    # 获取token
    token = get_auth_token()
    headers = {
        "Authorization": f"Bearer {token}",
        "X-Hospital-ID": "1"
    }
    
    # 尝试导出不存在的规则
    response = requests.get(
        f"{BASE_URL}/orientation-rules/999999/export",
        headers=headers
    )
    
    print(f"状态码: {response.status_code}")
    print(f"响应: {response.text}")
    
    assert response.status_code == 404, "应返回404状态码"
    print("✓ 正确返回404错误")


def test_export_without_hospital():
    """测试未激活医疗机构时导出"""
    print("\n=== 测试未激活医疗机构时导出 ===")
    
    # 获取token
    token = get_auth_token()
    headers = {
        "Authorization": f"Bearer {token}",
        # 不设置 X-Hospital-ID
    }
    
    # 尝试导出
    response = requests.get(
        f"{BASE_URL}/orientation-rules/1/export",
        headers=headers
    )
    
    print(f"状态码: {response.status_code}")
    print(f"响应: {response.text}")
    
    assert response.status_code == 400, "应返回400状态码"
    print("✓ 正确返回400错误")


if __name__ == "__main__":
    print("开始测试导向规则导出API...")
    
    try:
        test_export_api()
        test_export_nonexistent_rule()
        test_export_without_hospital()
        
        print("\n" + "="*50)
        print("所有API测试完成！")
    except Exception as e:
        print(f"\n✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
