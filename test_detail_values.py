"""测试业务明细中全院业务价值和科室业务价值的显示"""
import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

# 测试配置
HOSPITAL_ID = 1
TASK_ID = "test-task-1732779600-a1b2c3d4"  # 替换为实际的任务ID
DEPT_ID = 1  # 替换为实际的科室ID

def test_dept_detail():
    """测试科室明细API"""
    print("\n=== 测试科室明细 ===")
    
    url = f"{BASE_URL}/calculation-tasks/results/detail"
    params = {
        "dept_id": DEPT_ID,
        "task_id": TASK_ID
    }
    headers = {
        "X-Hospital-ID": str(HOSPITAL_ID),
        "Authorization": "Bearer test-token"  # 替换为实际token
    }
    
    response = requests.get(url, params=params, headers=headers)
    print(f"状态码: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        
        # 检查doctor数据
        if data.get("doctor"):
            print("\n医生序列数据:")
            for item in data["doctor"][:3]:  # 只显示前3条
                print(f"  维度: {item['dimension_name']}")
                print(f"    全院业务价值: {item['hospital_value']}")
                print(f"    科室业务价值: {item['dept_value']}")
                print(f"    是否相同: {item['hospital_value'] == item['dept_value']}")
                
                # 检查子节点
                if item.get("children"):
                    for child in item["children"][:2]:
                        print(f"      子维度: {child['dimension_name']}")
                        print(f"        全院: {child['hospital_value']}, 科室: {child['dept_value']}")
        
        # 检查nurse数据
        if data.get("nurse"):
            print("\n护理序列数据:")
            for item in data["nurse"][:2]:
                print(f"  维度: {item['dimension_name']}")
                print(f"    全院业务价值: {item['hospital_value']}")
                print(f"    科室业务价值: {item['dept_value']}")
    else:
        print(f"错误: {response.text}")


def test_hospital_detail():
    """测试全院汇总明细API"""
    print("\n=== 测试全院汇总明细 ===")
    
    url = f"{BASE_URL}/calculation-tasks/results/hospital-detail"
    params = {
        "task_id": TASK_ID
    }
    headers = {
        "X-Hospital-ID": str(HOSPITAL_ID),
        "Authorization": "Bearer test-token"
    }
    
    response = requests.get(url, params=params, headers=headers)
    print(f"状态码: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        
        # 检查doctor数据
        if data.get("doctor"):
            print("\n全院医生序列数据:")
            for item in data["doctor"][:3]:
                print(f"  维度: {item['dimension_name']}")
                print(f"    全院业务价值: {item['hospital_value']}")
                print(f"    科室业务价值: {item['dept_value']}")
                print(f"    是否相同: {item['hospital_value'] == item['dept_value']}")
    else:
        print(f"错误: {response.text}")


def check_calculation_results():
    """检查数据库中的calculation_results数据"""
    print("\n=== 检查数据库数据 ===")
    print("请在数据库中执行以下SQL查询:")
    print(f"""
    SELECT 
        node_name,
        node_type,
        weight,
        original_weight,
        CASE 
            WHEN original_weight IS NULL THEN '未设置'
            WHEN original_weight = weight THEN '相同'
            ELSE '不同'
        END as 比较
    FROM calculation_results
    WHERE task_id = '{TASK_ID}'
        AND department_id = {DEPT_ID}
        AND node_type = 'dimension'
    ORDER BY node_name
    LIMIT 10;
    """)


if __name__ == "__main__":
    print("业务明细价值显示测试")
    print("=" * 50)
    
    # 提示用户配置
    print("\n请先配置以下变量:")
    print(f"  HOSPITAL_ID: {HOSPITAL_ID}")
    print(f"  TASK_ID: {TASK_ID}")
    print(f"  DEPT_ID: {DEPT_ID}")
    print("\n按Enter继续...")
    input()
    
    # 运行测试
    test_dept_detail()
    test_hospital_detail()
    check_calculation_results()
    
    print("\n" + "=" * 50)
    print("测试完成")
