"""
测试导出文件名是否包含医院名称
"""
import requests
import sys

# 配置
BASE_URL = "http://localhost:8000/api/v1"
USERNAME = "admin"
PASSWORD = "admin123"

# 全局变量
token = None
headers = {}


def login():
    """登录获取token"""
    global token, headers
    print("\n1. 登录获取token...")
    response = requests.post(
        f"{BASE_URL}/auth/login",
        data={"username": USERNAME, "password": PASSWORD}
    )
    if response.status_code == 200:
        token = response.json()["access_token"]
        headers = {
            "Authorization": f"Bearer {token}",
            "X-Hospital-ID": "1"
        }
        print(f"✓ 登录成功")
        return True
    else:
        print(f"✗ 登录失败: {response.text}")
        return False


def test_orientation_rule_export():
    """测试导向规则导出"""
    print("\n2. 测试导向规则导出...")
    
    # 获取第一个导向规则
    response = requests.get(
        f"{BASE_URL}/orientation-rules",
        params={"page": 1, "size": 1},
        headers=headers
    )
    
    if response.status_code != 200 or not response.json().get("items"):
        print("✗ 没有导向规则数据，跳过测试")
        return
    
    rule_id = response.json()["items"][0]["id"]
    rule_name = response.json()["items"][0]["name"]
    print(f"  规则ID: {rule_id}, 名称: {rule_name}")
    
    # 测试Markdown导出
    print("\n  测试Markdown导出...")
    response = requests.get(
        f"{BASE_URL}/orientation-rules/{rule_id}/export",
        params={"format": "markdown"},
        headers=headers
    )
    
    if response.status_code == 200:
        content_disposition = response.headers.get("Content-Disposition", "")
        print(f"  Content-Disposition: {content_disposition}")
        
        # 检查是否包含医院名称
        if "filename*=UTF-8''" in content_disposition:
            from urllib.parse import unquote
            filename = unquote(content_disposition.split("filename*=UTF-8''")[1])
            print(f"  ✓ Markdown文件名: {filename}")
            
            if filename.count("_") >= 2:  # 医院名称_规则名称_时间戳
                print(f"  ✓ 文件名格式正确（包含医院名称前缀）")
            else:
                print(f"  ✗ 文件名格式错误（缺少医院名称前缀）")
        else:
            print(f"  ✗ 无法解析文件名")
    else:
        print(f"  ✗ Markdown导出失败: {response.status_code}")
    
    # 测试PDF导出
    print("\n  测试PDF导出...")
    response = requests.get(
        f"{BASE_URL}/orientation-rules/{rule_id}/export",
        params={"format": "pdf"},
        headers=headers
    )
    
    if response.status_code == 200:
        content_disposition = response.headers.get("Content-Disposition", "")
        print(f"  Content-Disposition: {content_disposition}")
        
        if "filename*=UTF-8''" in content_disposition:
            from urllib.parse import unquote
            filename = unquote(content_disposition.split("filename*=UTF-8''")[1])
            print(f"  ✓ PDF文件名: {filename}")
            
            if filename.count("_") >= 2:
                print(f"  ✓ 文件名格式正确（包含医院名称前缀）")
            else:
                print(f"  ✗ 文件名格式错误（缺少医院名称前缀）")
        else:
            print(f"  ✗ 无法解析文件名")
    else:
        print(f"  ✗ PDF导出失败: {response.status_code}")


def test_cost_benchmark_export():
    """测试成本基准导出"""
    print("\n3. 测试成本基准导出...")
    
    response = requests.get(
        f"{BASE_URL}/cost-benchmarks/export",
        headers=headers
    )
    
    if response.status_code == 200:
        content_disposition = response.headers.get("Content-Disposition", "")
        print(f"  Content-Disposition: {content_disposition}")
        
        if "filename*=UTF-8''" in content_disposition:
            from urllib.parse import unquote
            filename = unquote(content_disposition.split("filename*=UTF-8''")[1])
            print(f"  ✓ 文件名: {filename}")
            
            if filename.count("_") >= 2:  # 医院名称_成本基准_时间戳
                print(f"  ✓ 文件名格式正确（包含医院名称前缀）")
            else:
                print(f"  ✗ 文件名格式错误（缺少医院名称前缀）")
        else:
            print(f"  ✗ 无法解析文件名")
    elif response.status_code == 400:
        print(f"  ⚠ 没有成本基准数据: {response.json().get('detail')}")
    else:
        print(f"  ✗ 导出失败: {response.status_code} - {response.text}")


def test_data_issues_export():
    """测试数据问题导出"""
    print("\n4. 测试数据问题导出...")
    
    response = requests.get(
        f"{BASE_URL}/data-issues/export",
        headers=headers
    )
    
    if response.status_code == 200:
        content_disposition = response.headers.get("Content-Disposition", "")
        print(f"  Content-Disposition: {content_disposition}")
        
        if "filename*=UTF-8''" in content_disposition:
            from urllib.parse import unquote
            filename = unquote(content_disposition.split("filename*=UTF-8''")[1])
            print(f"  ✓ 文件名: {filename}")
            
            if filename.count("_") >= 2:  # 医院名称_数据问题记录_日期
                print(f"  ✓ 文件名格式正确（包含医院名称前缀）")
            else:
                print(f"  ✗ 文件名格式错误（缺少医院名称前缀）")
        else:
            print(f"  ✗ 无法解析文件名")
    else:
        print(f"  ✗ 导出失败: {response.status_code}")


def test_report_export():
    """测试报表导出"""
    print("\n5. 测试报表导出...")
    
    # 获取最新的计算任务
    response = requests.get(
        f"{BASE_URL}/calculation-tasks",
        params={"page": 1, "size": 1, "status": "completed"},
        headers=headers
    )
    
    if response.status_code != 200 or not response.json().get("items"):
        print("  ⚠ 没有已完成的计算任务，跳过报表导出测试")
        return
    
    task = response.json()["items"][0]
    task_id = task["task_id"]
    period = task["period"]
    print(f"  任务ID: {task_id}, 期间: {period}")
    
    # 测试汇总表导出
    print("\n  测试汇总表导出...")
    response = requests.get(
        f"{BASE_URL}/calculation-tasks/results/export/summary",
        params={"period": period},
        headers=headers
    )
    
    if response.status_code == 200:
        content_disposition = response.headers.get("Content-Disposition", "")
        print(f"  Content-Disposition: {content_disposition}")
        
        if "filename*=UTF-8''" in content_disposition:
            from urllib.parse import unquote
            filename = unquote(content_disposition.split("filename*=UTF-8''")[1])
            print(f"  ✓ 汇总表文件名: {filename}")
            
            if filename.count("_") >= 2:  # 医院名称_科室业务价值汇总_期间
                print(f"  ✓ 文件名格式正确（包含医院名称前缀）")
            else:
                print(f"  ✗ 文件名格式错误（缺少医院名称前缀）")
        else:
            print(f"  ✗ 无法解析文件名")
    else:
        print(f"  ✗ 汇总表导出失败: {response.status_code}")
    
    # 测试明细表导出
    print("\n  测试明细表导出...")
    response = requests.get(
        f"{BASE_URL}/calculation-tasks/results/export/detail",
        params={"task_id": task_id},
        headers=headers
    )
    
    if response.status_code == 200:
        content_disposition = response.headers.get("Content-Disposition", "")
        print(f"  Content-Disposition: {content_disposition}")
        
        if "filename*=UTF-8''" in content_disposition:
            from urllib.parse import unquote
            filename = unquote(content_disposition.split("filename*=UTF-8''")[1])
            print(f"  ✓ 明细表文件名: {filename}")
            
            if filename.count("_") >= 2:  # 医院名称_业务价值明细表_期间
                print(f"  ✓ 文件名格式正确（包含医院名称前缀）")
            else:
                print(f"  ✗ 文件名格式错误（缺少医院名称前缀）")
        else:
            print(f"  ✗ 无法解析文件名")
    else:
        print(f"  ✗ 明细表导出失败: {response.status_code}")


def main():
    print("=" * 70)
    print("测试导出文件名是否包含医院名称")
    print("=" * 70)
    
    # 登录
    if not login():
        sys.exit(1)
    
    # 测试各个导出功能
    test_orientation_rule_export()
    test_cost_benchmark_export()
    test_data_issues_export()
    test_report_export()
    
    print("\n" + "=" * 70)
    print("测试完成！")
    print("=" * 70)
    print("\n提示：")
    print("- 如果文件名包含医院名称前缀，格式应为：医院名称_原文件名")
    print("- 文件名中至少应该有2个下划线（医院名称_xxx_时间戳）")
    print("- 如果测试失败，请检查后端服务是否已重启")


if __name__ == "__main__":
    main()
