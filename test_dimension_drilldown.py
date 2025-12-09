"""
测试维度下钻功能
"""
import requests
import json

BASE_URL = "http://localhost:8000/api/v1"
HOSPITAL_ID = 1

# 登录获取 token
def login():
    response = requests.post(
        f"{BASE_URL}/auth/login",
        json={
            "username": "admin",
            "password": "admin123"
        }
    )
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        print(f"登录失败: {response.text}")
        return None

# 获取报告列表
def get_reports(token):
    headers = {
        "Authorization": f"Bearer {token}",
        "X-Hospital-ID": str(HOSPITAL_ID)
    }
    response = requests.get(
        f"{BASE_URL}/analysis-reports",
        headers=headers,
        params={"size": 10}
    )
    if response.status_code == 200:
        return response.json()
    else:
        print(f"获取报告列表失败: {response.text}")
        return None

# 获取价值分布
def get_value_distribution(token, report_id):
    headers = {
        "Authorization": f"Bearer {token}",
        "X-Hospital-ID": str(HOSPITAL_ID)
    }
    response = requests.get(
        f"{BASE_URL}/analysis-reports/{report_id}/value-distribution",
        headers=headers
    )
    if response.status_code == 200:
        return response.json()
    else:
        print(f"获取价值分布失败: {response.text}")
        return None

# 测试下钻
def test_drilldown(token, report_id, node_id):
    headers = {
        "Authorization": f"Bearer {token}",
        "X-Hospital-ID": str(HOSPITAL_ID)
    }
    response = requests.get(
        f"{BASE_URL}/analysis-reports/{report_id}/dimension-drilldown/{node_id}",
        headers=headers
    )
    print(f"\n下钻请求: report_id={report_id}, node_id={node_id}")
    print(f"状态码: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"维度名称: {data['dimension_name']}")
        print(f"明细数量: {len(data['items'])}")
        print(f"总金额: {data['total_amount']}")
        print(f"总数量: {data['total_quantity']}")
        if data['message']:
            print(f"提示信息: {data['message']}")
        
        # 显示前5条明细
        if data['items']:
            print("\n前5条明细:")
            for item in data['items'][:5]:
                print(f"  {item['item_code']} - {item['item_name']}: {item['amount']} ({item['quantity']})")
        
        return data
    else:
        print(f"下钻失败: {response.text}")
        return None

def main():
    # 登录
    print("=== 登录 ===")
    token = login()
    if not token:
        return
    print("登录成功")
    
    # 先创建一个有数据的报告（科室ID=4有计算结果）
    print("\n=== 创建测试报告 ===")
    headers = {
        "Authorization": f"Bearer {token}",
        "X-Hospital-ID": str(HOSPITAL_ID)
    }
    
    # 检查是否已存在
    existing = requests.get(
        f"{BASE_URL}/analysis-reports",
        headers=headers,
        params={"period": "2025-10", "size": 100}
    ).json()
    
    report = None
    for item in existing['items']:
        if item['department_id'] == 4:
            report = item
            print(f"使用已存在的报告: ID={report['id']}")
            break
    
    if not report:
        # 创建新报告
        response = requests.post(
            f"{BASE_URL}/analysis-reports",
            headers=headers,
            json={
                "department_id": 4,
                "period": "2025-10",
                "current_issues": "测试",
                "future_plans": "测试"
            }
        )
        if response.status_code == 200:
            report = response.json()
            print(f"创建新报告: ID={report['id']}")
        else:
            print(f"创建报告失败: {response.text}")
            return
    
    print(f"使用报告: ID={report['id']}, 科室={report['department_name']}, 年月={report['period']}")
    
    # 获取价值分布
    print("\n=== 获取价值分布 ===")
    distribution = get_value_distribution(token, report['id'])
    if not distribution or not distribution['items']:
        print("没有找到价值分布数据")
        return
    
    print(f"找到 {len(distribution['items'])} 个维度")
    for item in distribution['items'][:5]:
        print(f"  排名{item['rank']}: {item['dimension_name']} (node_id={item['node_id']}) - {item['value']} ({item['ratio']}%)")
    
    # 测试下钻第一个维度
    if distribution['items']:
        first_dim = distribution['items'][0]
        print(f"\n=== 测试下钻: {first_dim['dimension_name']} ===")
        test_drilldown(token, report['id'], first_dim['node_id'])
    
    # 测试下钻第二个维度（如果存在）
    if len(distribution['items']) > 1:
        second_dim = distribution['items'][1]
        print(f"\n=== 测试下钻: {second_dim['dimension_name']} ===")
        test_drilldown(token, report['id'], second_dim['node_id'])

if __name__ == "__main__":
    main()
