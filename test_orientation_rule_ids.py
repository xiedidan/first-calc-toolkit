"""
测试模型节点支持多个导向规则ID
"""
import requests

BASE_URL = "http://localhost:8000/api/v1"
HOSPITAL_ID = 1

# 登录获取token
login_response = requests.post(f"{BASE_URL}/auth/login", json={
    "username": "admin",
    "password": "admin123"
})
token = login_response.json()["access_token"]

headers = {
    "Authorization": f"Bearer {token}",
    "X-Hospital-ID": str(HOSPITAL_ID)
}

print("=" * 60)
print("测试模型节点多导向规则功能")
print("=" * 60)

# 1. 获取导向规则列表
print("\n1. 获取导向规则列表...")
rules_response = requests.get(f"{BASE_URL}/orientation-rules", headers=headers)
rules = rules_response.json()["items"]
print(f"   找到 {len(rules)} 个导向规则")
for rule in rules[:3]:
    print(f"   - ID: {rule['id']}, 名称: {rule['name']}")

# 2. 获取模型版本
print("\n2. 获取模型版本...")
versions_response = requests.get(f"{BASE_URL}/model-versions", headers=headers)
versions = versions_response.json()["items"]
if not versions:
    print("   ❌ 没有找到模型版本")
    exit(1)
version_id = versions[0]["id"]
print(f"   使用版本: {versions[0]['name']} (ID: {version_id})")

# 3. 获取末级节点
print("\n3. 获取末级节点...")
nodes_response = requests.get(
    f"{BASE_URL}/model-nodes",
    params={"version_id": version_id},
    headers=headers
)
nodes = nodes_response.json()["items"]

# 找到一个末级节点
leaf_node = None
def find_leaf(nodes_list):
    for node in nodes_list:
        if node.get("is_leaf"):
            return node
        if node.get("children"):
            result = find_leaf(node["children"])
            if result:
                return result
    return None

leaf_node = find_leaf(nodes)
if not leaf_node:
    print("   ❌ 没有找到末级节点")
    exit(1)

print(f"   找到末级节点: {leaf_node['name']} (ID: {leaf_node['id']})")
print(f"   当前导向规则: {leaf_node.get('orientation_rule_names', [])}")

# 4. 更新节点，设置多个导向规则
if len(rules) >= 2:
    print("\n4. 更新节点，设置多个导向规则...")
    rule_ids = [rules[0]["id"], rules[1]["id"]]
    update_data = {
        "orientation_rule_ids": rule_ids
    }
    update_response = requests.put(
        f"{BASE_URL}/model-nodes/{leaf_node['id']}",
        json=update_data,
        headers=headers
    )
    if update_response.status_code == 200:
        updated_node = update_response.json()
        print(f"   ✓ 更新成功")
        print(f"   导向规则ID: {updated_node.get('orientation_rule_ids', [])}")
        print(f"   导向规则名称: {updated_node.get('orientation_rule_names', [])}")
    else:
        print(f"   ❌ 更新失败: {update_response.text}")

# 5. 清空导向规则
print("\n5. 清空导向规则...")
clear_data = {
    "orientation_rule_ids": []
}
clear_response = requests.put(
    f"{BASE_URL}/model-nodes/{leaf_node['id']}",
    json=clear_data,
    headers=headers
)
if clear_response.status_code == 200:
    cleared_node = clear_response.json()
    print(f"   ✓ 清空成功")
    print(f"   导向规则ID: {cleared_node.get('orientation_rule_ids', [])}")
    print(f"   导向规则名称: {cleared_node.get('orientation_rule_names', [])}")
else:
    print(f"   ❌ 清空失败: {clear_response.text}")

print("\n" + "=" * 60)
print("测试完成！")
print("=" * 60)
