"""
测试学科规则加载问题
"""
import requests

BASE_URL = "http://localhost:8000/api/v1"
HOSPITAL_ID = 1

# 先登录获取 token
def get_token():
    resp = requests.post(
        f"{BASE_URL}/auth/login",
        json={"username": "admin", "password": "admin123"}
    )
    if resp.status_code == 200:
        return resp.json().get("access_token")
    print(f"登录失败: {resp.status_code} - {resp.text}")
    return None

token = get_token()
if not token:
    print("无法获取 token，退出")
    exit(1)

headers = {
    "X-Hospital-ID": str(HOSPITAL_ID),
    "Content-Type": "application/json",
    "Authorization": f"Bearer {token}"
}

def test_discipline_rules():
    """测试学科规则查询"""
    
    # 1. 获取最新完成的任务
    print("1. 获取最新完成的任务...")
    resp = requests.get(
        f"{BASE_URL}/calculation/tasks",
        params={"status": "completed", "page": 1, "size": 1},
        headers=headers
    )
    if resp.status_code != 200:
        print(f"   错误: {resp.status_code} - {resp.text}")
        return
    
    tasks = resp.json()
    if not tasks.get("items"):
        print("   没有完成的任务")
        return
    
    task = tasks["items"][0]
    task_id = task["task_id"]
    version_id = task["model_version_id"]
    print(f"   任务ID: {task_id}")
    print(f"   版本ID: {version_id}")
    
    # 2. 获取汇总数据
    print("\n2. 获取汇总数据...")
    resp = requests.get(
        f"{BASE_URL}/calculation/results/summary",
        params={"task_id": task_id},
        headers=headers
    )
    if resp.status_code != 200:
        print(f"   错误: {resp.status_code} - {resp.text}")
        return
    
    summary = resp.json()
    departments = summary.get("departments", [])
    print(f"   科室数量: {len(departments)}")
    
    if departments:
        dept = departments[0]
        dept_id = dept["department_id"]
        dept_code = dept["department_code"]
        dept_name = dept["department_name"]
        print(f"   第一个科室: ID={dept_id}, Code={dept_code}, Name={dept_name}")
    
    # 3. 获取明细数据
    print("\n3. 获取明细数据...")
    resp = requests.get(
        f"{BASE_URL}/calculation/results/detail",
        params={"task_id": task_id, "dept_id": dept_id},
        headers=headers
    )
    if resp.status_code != 200:
        print(f"   错误: {resp.status_code} - {resp.text}")
        return
    
    detail = resp.json()
    doctor_rows = detail.get("doctor", [])
    print(f"   医生序列行数: {len(doctor_rows)}")
    
    # 打印原始数据结构
    if doctor_rows:
        print(f"   第一行原始数据: {doctor_rows[0]}")
    
    # 找一个叶子节点（没有 children 的节点）
    def find_leaf_node(rows):
        for row in rows:
            if not row.get("children"):
                return row
            leaf = find_leaf_node(row.get("children", []))
            if leaf:
                return leaf
        return None
    
    leaf_row = find_leaf_node(doctor_rows)
    if leaf_row:
        node_id = leaf_row.get("node_id") or leaf_row.get("id")
        node_code = leaf_row.get("dimension_code") or leaf_row.get("node_code")
        node_name = leaf_row.get("dimension_name")
        print(f"   叶子节点: node_id={node_id}, node_code={node_code}, name={node_name}")
        print(f"   叶子节点原始数据: {leaf_row}")
    elif doctor_rows:
        row = doctor_rows[0]
        node_id = row.get("node_id") or row.get("id")
        node_code = row.get("dimension_code") or row.get("node_code")
        node_name = row.get("dimension_name")
        print(f"   第一行: node_id={node_id}, node_code={node_code}, name={node_name}")
    
    # 4. 查询学科规则
    print("\n4. 查询学科规则...")
    print(f"   参数: version_id={version_id}, department_code={dept_code}")
    
    # 4.1 不带 dimension_code 查询
    resp = requests.get(
        f"{BASE_URL}/discipline-rules",
        params={
            "version_id": version_id,
            "department_code": dept_code,
            "size": 10
        },
        headers=headers
    )
    if resp.status_code != 200:
        print(f"   错误: {resp.status_code} - {resp.text}")
        return
    
    rules = resp.json()
    print(f"   该科室的学科规则数量: {rules.get('total', 0)}")
    
    if rules.get("items"):
        for rule in rules["items"][:3]:
            print(f"   - {rule['dimension_name']}: 系数={rule['rule_coefficient']}")
    
    # 4.2 带 dimension_code 查询
    if node_code:
        print(f"\n5. 查询特定维度的学科规则...")
        print(f"   参数: version_id={version_id}, department_code={dept_code}, dimension_code={node_code}")
        
        resp = requests.get(
            f"{BASE_URL}/discipline-rules",
            params={
                "version_id": version_id,
                "department_code": dept_code,
                "dimension_code": node_code,
                "size": 1
            },
            headers=headers
        )
        if resp.status_code != 200:
            print(f"   错误: {resp.status_code} - {resp.text}")
            return
        
        rules = resp.json()
        print(f"   匹配的学科规则数量: {rules.get('total', 0)}")
        
        if rules.get("items"):
            rule = rules["items"][0]
            print(f"   规则: {rule['dimension_name']}, 系数={rule['rule_coefficient']}")
        else:
            print("   未找到匹配的学科规则")
    
    # 5. 检查所有学科规则
    print("\n6. 检查所有学科规则...")
    resp = requests.get(
        f"{BASE_URL}/discipline-rules",
        params={"version_id": version_id, "size": 100},
        headers=headers
    )
    if resp.status_code != 200:
        print(f"   错误: {resp.status_code} - {resp.text}")
        return
    
    all_rules = resp.json()
    print(f"   版本 {version_id} 的学科规则总数: {all_rules.get('total', 0)}")
    
    if all_rules.get("items"):
        dept_codes = set(r["department_code"] for r in all_rules["items"])
        print(f"   涉及的科室代码: {dept_codes}")

if __name__ == "__main__":
    test_discipline_rules()
