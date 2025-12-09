"""
直接测试导向规则API端点
"""
import sys
sys.path.insert(0, 'backend')

from fastapi.testclient import TestClient
from app.main import app
from app.database import SessionLocal
from app.models.user import User
from app.models.hospital import Hospital
from app.utils.security import create_access_token

# 创建测试客户端
client = TestClient(app)

def get_test_token():
    """获取测试用token"""
    db = SessionLocal()
    try:
        # 获取第一个用户
        user = db.query(User).first()
        if not user:
            print("错误：数据库中没有用户")
            return None, None
        
        # 获取第一个医疗机构
        hospital = db.query(Hospital).first()
        if not hospital:
            print("错误：数据库中没有医疗机构")
            return None, None
        
        # 创建token
        token = create_access_token(
            data={"sub": str(user.id), "username": user.username}
        )
        
        return token, hospital.id
    finally:
        db.close()


def test_create_rule(token, hospital_id):
    """测试创建导向规则"""
    print("\n=== 测试创建导向规则 ===")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "X-Hospital-ID": str(hospital_id)
    }
    
    data = {
        "name": "API测试导向规则",
        "category": "benchmark_ladder",
        "description": "通过API创建的测试规则"
    }
    
    response = client.post("/api/v1/orientation-rules", headers=headers, json=data)
    print(f"状态码: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"✓ 创建成功: ID={result['id']}, 名称={result['name']}")
        return result['id']
    else:
        print(f"✗ 创建失败: {response.text}")
        return None


def test_list_rules(token, hospital_id):
    """测试获取导向规则列表"""
    print("\n=== 测试获取导向规则列表 ===")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "X-Hospital-ID": str(hospital_id)
    }
    
    response = client.get("/api/v1/orientation-rules", headers=headers)
    print(f"状态码: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"✓ 查询成功: 共 {result['total']} 条记录")
        for item in result['items']:
            print(f"  - {item['name']} ({item['category']})")
    else:
        print(f"✗ 查询失败: {response.text}")


def test_get_rule(token, hospital_id, rule_id):
    """测试获取导向规则详情"""
    print(f"\n=== 测试获取导向规则详情 (ID: {rule_id}) ===")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "X-Hospital-ID": str(hospital_id)
    }
    
    response = client.get(f"/api/v1/orientation-rules/{rule_id}", headers=headers)
    print(f"状态码: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"✓ 查询成功: {result['name']}")
    else:
        print(f"✗ 查询失败: {response.text}")


def test_update_rule(token, hospital_id, rule_id):
    """测试更新导向规则"""
    print(f"\n=== 测试更新导向规则 (ID: {rule_id}) ===")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "X-Hospital-ID": str(hospital_id)
    }
    
    data = {
        "description": "API更新后的描述"
    }
    
    response = client.put(f"/api/v1/orientation-rules/{rule_id}", headers=headers, json=data)
    print(f"状态码: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"✓ 更新成功: {result['description']}")
    else:
        print(f"✗ 更新失败: {response.text}")


def test_delete_rule(token, hospital_id, rule_id):
    """测试删除导向规则"""
    print(f"\n=== 测试删除导向规则 (ID: {rule_id}) ===")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "X-Hospital-ID": str(hospital_id)
    }
    
    response = client.delete(f"/api/v1/orientation-rules/{rule_id}", headers=headers)
    print(f"状态码: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"✓ 删除成功: {result['message']}")
    else:
        print(f"✗ 删除失败: {response.text}")


def test_search_rules(token, hospital_id):
    """测试搜索和筛选"""
    print("\n=== 测试搜索和筛选 ===")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "X-Hospital-ID": str(hospital_id)
    }
    
    # 测试关键词搜索
    response = client.get("/api/v1/orientation-rules?keyword=测试", headers=headers)
    print(f"关键词搜索 - 状态码: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"✓ 找到 {result['total']} 条记录")
    
    # 测试类别筛选
    response = client.get("/api/v1/orientation-rules?category=benchmark_ladder", headers=headers)
    print(f"类别筛选 - 状态码: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"✓ 找到 {result['total']} 条记录")


def main():
    """主测试流程"""
    print("开始测试导向规则API...")
    
    # 获取测试token
    token, hospital_id = get_test_token()
    if not token or not hospital_id:
        print("无法获取测试token，测试终止")
        return
    
    print(f"使用医疗机构ID: {hospital_id}")
    
    # 测试创建
    rule_id = test_create_rule(token, hospital_id)
    
    if rule_id:
        # 测试列表
        test_list_rules(token, hospital_id)
        
        # 测试详情
        test_get_rule(token, hospital_id, rule_id)
        
        # 测试更新
        test_update_rule(token, hospital_id, rule_id)
        
        # 测试搜索
        test_search_rules(token, hospital_id)
        
        # 测试删除
        test_delete_rule(token, hospital_id, rule_id)
        
        # 再次查询列表
        test_list_rules(token, hospital_id)
    
    print("\n所有测试完成！")


if __name__ == "__main__":
    main()
