"""
测试导向阶梯API的完整功能
"""
import requests
import json
from datetime import datetime

# 配置
BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api/v1"

# 测试用户凭证
TEST_USER = {
    "username": "admin",
    "password": "admin123"
}

def get_auth_token():
    """获取认证token"""
    response = requests.post(
        f"{API_BASE}/auth/login",
        json={
            "username": TEST_USER["username"],
            "password": TEST_USER["password"]
        }
    )
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        print(f"登录失败: {response.status_code}")
        print(response.text)
        return None

def get_headers(token):
    """获取请求头"""
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "X-Hospital-ID": "1"  # 使用医疗机构ID 1
    }

def test_create_orientation_rule(token):
    """创建测试用的导向规则"""
    headers = get_headers(token)
    
    # 创建基准阶梯类别的导向规则
    rule_data = {
        "name": f"测试阶梯导向-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "category": "benchmark_ladder",
        "description": "用于测试阶梯API的导向规则"
    }
    
    response = requests.post(
        f"{API_BASE}/orientation-rules",
        headers=headers,
        json=rule_data
    )
    
    if response.status_code == 200:
        rule = response.json()
        print(f"✓ 创建导向规则成功: ID={rule['id']}, 名称={rule['name']}")
        return rule
    else:
        print(f"✗ 创建导向规则失败: {response.status_code}")
        print(response.text)
        return None

def test_create_direct_ladder_rule(token):
    """创建直接阶梯类别的导向规则"""
    headers = get_headers(token)
    
    rule_data = {
        "name": f"测试直接阶梯-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "category": "direct_ladder",
        "description": "用于测试直接阶梯的导向规则"
    }
    
    response = requests.post(
        f"{API_BASE}/orientation-rules",
        headers=headers,
        json=rule_data
    )
    
    if response.status_code == 200:
        rule = response.json()
        print(f"✓ 创建直接阶梯导向规则成功: ID={rule['id']}, 名称={rule['name']}")
        return rule
    else:
        print(f"✗ 创建直接阶梯导向规则失败: {response.status_code}")
        print(response.text)
        return None

def test_create_ladder(token, rule_id):
    """测试创建导向阶梯"""
    headers = get_headers(token)
    
    print("\n=== 测试创建导向阶梯 ===")
    
    # 创建第一个阶梯（有上下限）
    ladder_data = {
        "rule_id": rule_id,
        "ladder_order": 1,
        "lower_limit": 0.0,
        "upper_limit": 100.0,
        "adjustment_intensity": 1.2500
    }
    
    response = requests.post(
        f"{API_BASE}/orientation-ladders",
        headers=headers,
        json=ladder_data
    )
    
    if response.status_code == 200:
        ladder = response.json()
        print(f"✓ 创建阶梯1成功: ID={ladder['id']}, 次序={ladder['ladder_order']}")
        print(f"  上限={ladder['upper_limit']}, 下限={ladder['lower_limit']}, 调整力度={ladder['adjustment_intensity']}")
        print(f"  导向名称={ladder.get('rule_name', 'N/A')}")
        
        # 创建第二个阶梯（下限为NULL，表示负无穷）
        ladder_data2 = {
            "rule_id": rule_id,
            "ladder_order": 2,
            "lower_limit": None,  # 负无穷
            "upper_limit": 0.0,
            "adjustment_intensity": 0.8000
        }
        
        response2 = requests.post(
            f"{API_BASE}/orientation-ladders",
            headers=headers,
            json=ladder_data2
        )
        
        if response2.status_code == 200:
            ladder2 = response2.json()
            print(f"✓ 创建阶梯2成功: ID={ladder2['id']}, 次序={ladder2['ladder_order']}")
            print(f"  上限={ladder2['upper_limit']}, 下限={ladder2['lower_limit']} (负无穷), 调整力度={ladder2['adjustment_intensity']}")
            return [ladder, ladder2]
        else:
            print(f"✗ 创建阶梯2失败: {response2.status_code}")
            print(response2.text)
            return [ladder]
    else:
        print(f"✗ 创建阶梯失败: {response.status_code}")
        print(response.text)
        return None

def test_create_ladder_with_wrong_category(token):
    """测试创建阶梯时验证导向类别"""
    headers = get_headers(token)
    
    print("\n=== 测试类别验证 ===")
    
    # 创建"其他"类别的导向规则
    rule_data = {
        "name": f"测试其他类别-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "category": "other",
        "description": "不应该能创建阶梯"
    }
    
    response = requests.post(
        f"{API_BASE}/orientation-rules",
        headers=headers,
        json=rule_data
    )
    
    if response.status_code == 200:
        rule = response.json()
        print(f"✓ 创建'其他'类别导向规则成功: ID={rule['id']}")
        
        # 尝试为"其他"类别创建阶梯（应该失败）
        ladder_data = {
            "rule_id": rule['id'],
            "ladder_order": 1,
            "lower_limit": 0.0,
            "upper_limit": 100.0,
            "adjustment_intensity": 1.0
        }
        
        response2 = requests.post(
            f"{API_BASE}/orientation-ladders",
            headers=headers,
            json=ladder_data
        )
        
        if response2.status_code == 400:
            print(f"✓ 正确拒绝为'其他'类别创建阶梯: {response2.json()['detail']}")
        else:
            print(f"✗ 应该拒绝但没有拒绝: {response2.status_code}")
            print(response2.text)

def test_create_duplicate_order(token, rule_id):
    """测试创建重复次序的阶梯"""
    headers = get_headers(token)
    
    print("\n=== 测试次序唯一性验证 ===")
    
    # 创建第一个阶梯
    ladder_data = {
        "rule_id": rule_id,
        "ladder_order": 10,
        "lower_limit": 0.0,
        "upper_limit": 100.0,
        "adjustment_intensity": 1.0
    }
    
    response = requests.post(
        f"{API_BASE}/orientation-ladders",
        headers=headers,
        json=ladder_data
    )
    
    if response.status_code == 200:
        print(f"✓ 创建阶梯次序10成功")
        
        # 尝试创建相同次序的阶梯（应该失败）
        response2 = requests.post(
            f"{API_BASE}/orientation-ladders",
            headers=headers,
            json=ladder_data
        )
        
        if response2.status_code == 400:
            print(f"✓ 正确拒绝重复次序: {response2.json()['detail']}")
        else:
            print(f"✗ 应该拒绝但没有拒绝: {response2.status_code}")

def test_get_ladders(token, rule_id):
    """测试获取导向阶梯列表"""
    headers = get_headers(token)
    
    print("\n=== 测试获取阶梯列表 ===")
    
    # 获取所有阶梯
    response = requests.get(
        f"{API_BASE}/orientation-ladders",
        headers=headers,
        params={"page": 1, "size": 10}
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✓ 获取所有阶梯成功: 总数={data['total']}")
        for item in data['items'][:3]:  # 只显示前3个
            print(f"  - ID={item['id']}, 导向={item.get('rule_name', 'N/A')}, 次序={item['ladder_order']}")
    else:
        print(f"✗ 获取阶梯列表失败: {response.status_code}")
        print(response.text)
    
    # 按导向筛选
    response2 = requests.get(
        f"{API_BASE}/orientation-ladders",
        headers=headers,
        params={"rule_id": rule_id, "page": 1, "size": 10}
    )
    
    if response2.status_code == 200:
        data2 = response2.json()
        print(f"✓ 按导向筛选成功: 总数={data2['total']}")
        print(f"  阶梯按次序排序:")
        for item in data2['items']:
            print(f"  - 次序={item['ladder_order']}, 上限={item['upper_limit']}, 下限={item['lower_limit']}")
    else:
        print(f"✗ 按导向筛选失败: {response2.status_code}")

def test_get_ladder_detail(token, ladder_id):
    """测试获取阶梯详情"""
    headers = get_headers(token)
    
    print("\n=== 测试获取阶梯详情 ===")
    
    response = requests.get(
        f"{API_BASE}/orientation-ladders/{ladder_id}",
        headers=headers
    )
    
    if response.status_code == 200:
        ladder = response.json()
        print(f"✓ 获取阶梯详情成功:")
        print(f"  ID={ladder['id']}")
        print(f"  导向名称={ladder.get('rule_name', 'N/A')}")
        print(f"  阶梯次序={ladder['ladder_order']}")
        print(f"  上限={ladder['upper_limit']}, 下限={ladder['lower_limit']}")
        print(f"  调整力度={ladder['adjustment_intensity']}")
    else:
        print(f"✗ 获取阶梯详情失败: {response.status_code}")
        print(response.text)

def test_update_ladder(token, ladder_id):
    """测试更新导向阶梯"""
    headers = get_headers(token)
    
    print("\n=== 测试更新阶梯 ===")
    
    # 更新调整力度和上限
    update_data = {
        "upper_limit": 200.0,
        "adjustment_intensity": 1.5000
    }
    
    response = requests.put(
        f"{API_BASE}/orientation-ladders/{ladder_id}",
        headers=headers,
        json=update_data
    )
    
    if response.status_code == 200:
        ladder = response.json()
        print(f"✓ 更新阶梯成功:")
        print(f"  新上限={ladder['upper_limit']}")
        print(f"  新调整力度={ladder['adjustment_intensity']}")
    else:
        print(f"✗ 更新阶梯失败: {response.status_code}")
        print(response.text)

def test_decimal_formatting(token, rule_id):
    """测试数值字段自动格式化为4位小数"""
    headers = get_headers(token)
    
    print("\n=== 测试数值格式化 ===")
    
    # 创建阶梯，输入不规则的小数位数
    ladder_data = {
        "rule_id": rule_id,
        "ladder_order": 99,
        "lower_limit": 10.123456789,  # 超过4位小数
        "upper_limit": 20.1,  # 少于4位小数
        "adjustment_intensity": 1.23  # 2位小数
    }
    
    response = requests.post(
        f"{API_BASE}/orientation-ladders",
        headers=headers,
        json=ladder_data
    )
    
    if response.status_code == 200:
        ladder = response.json()
        print(f"✓ 创建阶梯成功，验证格式化:")
        print(f"  输入下限=10.123456789 -> 存储={ladder['lower_limit']} (应为4位小数)")
        print(f"  输入上限=20.1 -> 存储={ladder['upper_limit']} (应为4位小数)")
        print(f"  输入调整力度=1.23 -> 存储={ladder['adjustment_intensity']} (应为4位小数)")
        
        # 验证是否正确格式化
        if str(ladder['lower_limit']) == "10.1235":  # 四舍五入
            print(f"  ✓ 下限格式化正确")
        if str(ladder['upper_limit']) == "20.1000":
            print(f"  ✓ 上限格式化正确")
        if str(ladder['adjustment_intensity']) == "1.2300":
            print(f"  ✓ 调整力度格式化正确")
    else:
        print(f"✗ 创建阶梯失败: {response.status_code}")
        print(response.text)

def test_delete_ladder(token, ladder_id):
    """测试删除导向阶梯"""
    headers = get_headers(token)
    
    print("\n=== 测试删除阶梯 ===")
    
    response = requests.delete(
        f"{API_BASE}/orientation-ladders/{ladder_id}",
        headers=headers
    )
    
    if response.status_code == 200:
        print(f"✓ 删除阶梯成功: {response.json()['message']}")
    else:
        print(f"✗ 删除阶梯失败: {response.status_code}")
        print(response.text)

def main():
    """主测试流程"""
    print("=" * 60)
    print("导向阶梯API测试")
    print("=" * 60)
    
    # 获取token
    token = get_auth_token()
    if not token:
        print("无法获取认证token，测试终止")
        return
    
    print(f"✓ 获取认证token成功\n")
    
    # 创建测试用的导向规则
    rule = test_create_orientation_rule(token)
    if not rule:
        print("无法创建测试导向规则，测试终止")
        return
    
    rule_id = rule['id']
    
    # 创建直接阶梯类别的导向规则
    direct_rule = test_create_direct_ladder_rule(token)
    
    # 测试创建阶梯
    ladders = test_create_ladder(token, rule_id)
    if not ladders:
        print("无法创建测试阶梯，部分测试跳过")
        return
    
    ladder_id = ladders[0]['id']
    
    # 测试类别验证
    test_create_ladder_with_wrong_category(token)
    
    # 测试次序唯一性
    test_create_duplicate_order(token, rule_id)
    
    # 测试获取列表
    test_get_ladders(token, rule_id)
    
    # 测试获取详情
    test_get_ladder_detail(token, ladder_id)
    
    # 测试更新
    test_update_ladder(token, ladder_id)
    
    # 测试数值格式化
    test_decimal_formatting(token, rule_id)
    
    # 测试删除
    if len(ladders) > 1:
        test_delete_ladder(token, ladders[1]['id'])
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)

if __name__ == "__main__":
    main()
