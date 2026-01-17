"""
测试放射科下钻问题
"""
import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

def get_token():
    response = requests.post(
        f"{BASE_URL}/auth/login",
        json={"username": "admin", "password": "admin123"}
    )
    if response.status_code == 200:
        return response.json()["access_token"]
    print(f"登录失败: {response.text}")
    return None

def test_radiology():
    token = get_token()
    if not token:
        return
    
    headers = {
        "Authorization": f"Bearer {token}",
        "X-Hospital-ID": "1"
    }
    
    # 获取最新任务
    resp = requests.get(
        f"{BASE_URL}/calculation/tasks",
        params={"status": "completed", "page": 1, "size": 10},
        headers=headers
    )
    tasks = resp.json().get("items", [])
    task = tasks[0]
    task_id = task["task_id"]
    print(f"任务: {task_id}")
    
    # 获取放射科明细
    resp = requests.get(
        f"{BASE_URL}/calculation/results/detail",
        params={"dept_id": 31, "task_id": task_id},
        headers=headers
    )
    
    detail = resp.json()
    
    # 打印医技序列的维度结构
    print("\n=== 医技序列维度 ===")
    tech_data = detail.get("tech", [])
    
    def print_dim(dim, depth=0):
        indent = "  " * depth
        dim_name = dim.get("dimension_name", "")
        node_id = dim.get("node_id") or dim.get("id")
        dim_code = dim.get("dimension_code", "")
        children = dim.get("children") or []
        is_leaf = not children
        
        # 判断是否可下钻（前端逻辑）
        can_drill = False
        if node_id and is_leaf:
            # 不是成本维度
            if '-cost' not in dim_code and dim_name not in ['人员经费', '不收费卫生材料费', '折旧（风险）费', '折旧风险费', '其他费用', '成本']:
                can_drill = True
        
        drill_mark = "✓可下钻" if can_drill else ""
        print(f"{indent}- {dim_name} (id={node_id}, code={dim_code}, leaf={is_leaf}) {drill_mark}")
        
        for child in children:
            print_dim(child, depth + 1)
    
    for dim in tech_data:
        print_dim(dim)
    
    # 测试下钻API
    print("\n=== 测试下钻API ===")
    # 找到叶子节点测试
    def find_leaves(dims, result):
        for dim in dims:
            children = dim.get("children") or []
            if not children:
                result.append(dim)
            else:
                find_leaves(children, result)
    
    leaves = []
    find_leaves(tech_data, leaves)
    
    for leaf in leaves[:5]:  # 测试前5个
        node_id = leaf.get("node_id") or leaf.get("id")
        dim_name = leaf.get("dimension_name")
        dim_code = leaf.get("dimension_code", "")
        
        resp = requests.get(
            f"{BASE_URL}/analysis-reports/dimension-drilldown",
            params={
                "task_id": task_id,
                "department_id": 31,
                "node_id": node_id
            },
            headers=headers
        )
        
        status = "✓" if resp.status_code == 200 else f"✗({resp.status_code})"
        error = ""
        if resp.status_code != 200:
            try:
                error = resp.json().get("detail", "")[:50]
            except:
                pass
        print(f"{status} {dim_name} (code={dim_code}) {error}")

if __name__ == "__main__":
    test_radiology()
