"""
端到端测试：calculation_details 生成和下钻查询

测试流程：
1. 使用测试数据生成 calculation_details
2. 验证下钻 API 能正确从 calculation_details 查询数据
"""
import os
import sys
sys.path.insert(0, 'backend')

import requests
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv('backend/.env')

DATABASE_URL = os.getenv('DATABASE_URL')
engine = create_engine(DATABASE_URL)

# API 配置
BASE_URL = "http://localhost:8000/api/v1"
HEADERS = {
    "X-Hospital-ID": "1",
    "Content-Type": "application/json"
}

# 测试参数
task_id = 'test-calc-details-001'  # 使用之前测试生成的数据

print("=" * 60)
print("端到端测试：calculation_details 下钻查询")
print("=" * 60)

# 1. 检查测试数据是否存在
with engine.connect() as conn:
    result = conn.execute(text("""
        SELECT COUNT(*) FROM calculation_details WHERE task_id = :task_id
    """), {"task_id": task_id})
    count = result.scalar()
    print(f"\n1. 检查测试数据: {count} 条记录")
    
    if count == 0:
        print("   错误：测试数据不存在，请先运行 test_calculation_details.py")
        sys.exit(1)
    
    # 获取一个有数据的维度用于测试
    result = conn.execute(text("""
        SELECT DISTINCT node_id, node_code, node_name, department_id
        FROM calculation_details
        WHERE task_id = :task_id
        AND node_code LIKE 'dim-doc-sur-in-%'
        LIMIT 1
    """), {"task_id": task_id})
    row = result.fetchone()
    
    if not row:
        print("   错误：未找到手术维度数据")
        sys.exit(1)
    
    test_node_id = row[0]
    test_node_code = row[1]
    test_node_name = row[2]
    test_dept_id = row[3]
    
    print(f"   测试维度: {test_node_code} ({test_node_name})")
    print(f"   测试科室ID: {test_dept_id}")

# 2. 测试直接数据库查询
print("\n2. 直接数据库查询测试:")
with engine.connect() as conn:
    result = conn.execute(text("""
        SELECT 
            item_code,
            item_name,
            SUM(amount) as total_amount,
            SUM(quantity) as total_quantity
        FROM calculation_details
        WHERE task_id = :task_id
        AND department_id = :department_id
        AND node_id = :node_id
        GROUP BY item_code, item_name
        ORDER BY total_amount DESC
        LIMIT 5
    """), {
        "task_id": task_id,
        "department_id": test_dept_id,
        "node_id": test_node_id
    })
    
    rows = result.fetchall()
    print(f"   查询到 {len(rows)} 条记录")
    for row in rows[:3]:
        print(f"   - {row[0]}: {row[2]}")

# 3. 测试 API 查询（需要后端服务运行）
print("\n3. API 查询测试:")
print("   注意：需要后端服务运行在 localhost:8000")

try:
    # 先登录获取 token
    login_resp = requests.post(
        f"{BASE_URL}/auth/login",
        json={"username": "admin", "password": "admin123"}
    )
    
    if login_resp.status_code == 200:
        token = login_resp.json().get("access_token")
        HEADERS["Authorization"] = f"Bearer {token}"
        print("   登录成功")
        
        # 测试下钻 API
        drilldown_url = f"{BASE_URL}/analysis-reports/dimension-drilldown"
        params = {
            "task_id": task_id,
            "department_id": test_dept_id,
            "node_id": test_node_id
        }
        
        resp = requests.get(drilldown_url, params=params, headers=HEADERS)
        
        if resp.status_code == 200:
            data = resp.json()
            print(f"   下钻查询成功!")
            print(f"   维度名称: {data.get('dimension_name')}")
            print(f"   项目数量: {len(data.get('items', []))}")
            print(f"   总金额: {data.get('total_amount')}")
        else:
            print(f"   下钻查询失败: {resp.status_code}")
            print(f"   响应: {resp.text[:200]}")
    else:
        print(f"   登录失败: {login_resp.status_code}")
        print("   跳过 API 测试")
        
except requests.exceptions.ConnectionError:
    print("   无法连接到后端服务，跳过 API 测试")
    print("   请确保后端服务运行在 localhost:8000")

print("\n" + "=" * 60)
print("测试完成")
print("=" * 60)
