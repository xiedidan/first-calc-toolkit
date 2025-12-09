"""
测试导向规则复制的事务回滚功能
"""
import requests
from datetime import datetime
import sys
import os

# 添加backend目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# 加载环境变量
load_dotenv("backend/.env")

# API基础URL
BASE_URL = "http://localhost:8000/api/v1"

# 测试用的医疗机构ID和认证token
HOSPITAL_ID = 1
TOKEN = None


def login():
    """登录获取token"""
    global TOKEN
    response = requests.post(
        f"{BASE_URL}/auth/login",
        json={
            "username": "admin",
            "password": "admin123"
        }
    )
    if response.status_code == 200:
        TOKEN = response.json()["access_token"]
        print(f"✓ 登录成功")
    else:
        print(f"✗ 登录失败: {response.text}")
        exit(1)


def get_headers():
    """获取请求头"""
    return {
        "Authorization": f"Bearer {TOKEN}",
        "X-Hospital-ID": str(HOSPITAL_ID),
        "Content-Type": "application/json"
    }


def get_db_session():
    """获取数据库会话"""
    database_url = os.getenv("DATABASE_URL")
    engine = create_engine(database_url)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return SessionLocal()


def test_copy_nonexistent_rule():
    """测试复制不存在的规则（应该返回404）"""
    print("\n=== 测试复制不存在的规则 ===")
    
    # 使用一个不太可能存在的ID
    nonexistent_id = 999999
    
    response = requests.post(
        f"{BASE_URL}/orientation-rules/{nonexistent_id}/copy",
        headers=get_headers()
    )
    
    if response.status_code == 404:
        print(f"✓ 正确返回404错误")
        return True
    else:
        print(f"✗ 未返回预期的404错误，实际状态码: {response.status_code}")
        print(f"  响应: {response.text}")
        return False


def test_copy_with_duplicate_name(db):
    """测试复制后名称冲突的情况"""
    print("\n=== 测试名称冲突处理 ===")
    
    # 创建第一个规则
    rule_data = {
        "name": f"测试名称冲突-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "category": "other",
        "description": "测试名称冲突"
    }
    
    response = requests.post(
        f"{BASE_URL}/orientation-rules",
        headers=get_headers(),
        json=rule_data
    )
    
    if response.status_code != 200:
        print(f"✗ 创建规则失败")
        return False
    
    rule1 = response.json()
    rule1_id = rule1["id"]
    print(f"  创建规则1: ID={rule1_id}, 名称={rule1['name']}")
    
    # 第一次复制
    response = requests.post(
        f"{BASE_URL}/orientation-rules/{rule1_id}/copy",
        headers=get_headers()
    )
    
    if response.status_code != 200:
        print(f"✗ 第一次复制失败")
        cleanup_rule(rule1_id)
        return False
    
    rule2 = response.json()
    rule2_id = rule2["id"]
    print(f"  第一次复制成功: ID={rule2_id}, 名称={rule2['name']}")
    
    # 第二次复制（名称会是"xxx（副本）（副本）"）
    response = requests.post(
        f"{BASE_URL}/orientation-rules/{rule2_id}/copy",
        headers=get_headers()
    )
    
    success = False
    if response.status_code == 200:
        rule3 = response.json()
        rule3_id = rule3["id"]
        print(f"  第二次复制成功: ID={rule3_id}, 名称={rule3['name']}")
        
        # 验证名称包含两个"（副本）"
        if rule3['name'].count("（副本）") == 2:
            print(f"  ✓ 名称正确包含两个'（副本）'")
            success = True
        else:
            print(f"  ✗ 名称格式不正确")
        
        cleanup_rule(rule3_id)
    else:
        print(f"  ✗ 第二次复制失败: {response.text}")
    
    # 清理
    cleanup_rule(rule1_id)
    cleanup_rule(rule2_id)
    
    return success


def cleanup_rule(rule_id):
    """清理测试数据"""
    response = requests.delete(
        f"{BASE_URL}/orientation-rules/{rule_id}",
        headers=get_headers()
    )
    return response.status_code == 200


def count_rules(db):
    """统计规则数量"""
    from app.models.orientation_rule import OrientationRule
    
    return db.query(OrientationRule).filter(
        OrientationRule.hospital_id == HOSPITAL_ID
    ).count()


def test_transaction_integrity(db):
    """测试事务完整性（确保复制是原子操作）"""
    print("\n=== 测试事务完整性 ===")
    
    # 记录初始规则数量
    initial_count = count_rules(db)
    print(f"  初始规则数量: {initial_count}")
    
    # 创建一个规则
    rule_data = {
        "name": f"测试事务-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "category": "benchmark_ladder",
        "description": "测试事务完整性"
    }
    
    response = requests.post(
        f"{BASE_URL}/orientation-rules",
        headers=get_headers(),
        json=rule_data
    )
    
    if response.status_code != 200:
        print(f"✗ 创建规则失败")
        return False
    
    rule = response.json()
    rule_id = rule["id"]
    
    # 添加一些测试数据
    from app.models.orientation_ladder import OrientationLadder
    
    for i in range(1, 4):
        ladder = OrientationLadder(
            hospital_id=HOSPITAL_ID,
            rule_id=rule_id,
            ladder_order=i,
            lower_limit=i * 10.0,
            upper_limit=(i + 1) * 10.0,
            adjustment_intensity=0.5 + i * 0.1
        )
        db.add(ladder)
    db.commit()
    
    # 复制规则
    response = requests.post(
        f"{BASE_URL}/orientation-rules/{rule_id}/copy",
        headers=get_headers()
    )
    
    if response.status_code != 200:
        print(f"✗ 复制失败")
        cleanup_rule(rule_id)
        return False
    
    new_rule = response.json()
    new_rule_id = new_rule["id"]
    
    # 验证规则数量增加了1
    final_count = count_rules(db)
    print(f"  最终规则数量: {final_count}")
    
    success = False
    if final_count == initial_count + 2:  # 原始规则 + 复制的规则
        print(f"  ✓ 规则数量正确增加")
        
        # 验证新规则的阶梯数量
        from app.models.orientation_ladder import OrientationLadder
        ladder_count = db.query(OrientationLadder).filter(
            OrientationLadder.rule_id == new_rule_id
        ).count()
        
        if ladder_count == 3:
            print(f"  ✓ 阶梯数据正确复制")
            success = True
        else:
            print(f"  ✗ 阶梯数据复制不完整: 期望3个, 实际{ladder_count}个")
    else:
        print(f"  ✗ 规则数量不正确")
    
    # 清理
    cleanup_rule(rule_id)
    cleanup_rule(new_rule_id)
    
    return success


def main():
    """主测试流程"""
    print("=" * 60)
    print("导向规则复制功能 - 事务和错误处理测试")
    print("=" * 60)
    
    # 登录
    login()
    
    # 获取数据库会话
    db = get_db_session()
    
    try:
        results = []
        
        # 测试复制不存在的规则
        results.append(("复制不存在的规则", test_copy_nonexistent_rule()))
        
        # 测试名称冲突处理
        results.append(("名称冲突处理", test_copy_with_duplicate_name(db)))
        
        # 测试事务完整性
        results.append(("事务完整性", test_transaction_integrity(db)))
        
        # 输出总结
        print("\n" + "=" * 60)
        print("测试总结")
        print("=" * 60)
        
        all_passed = True
        for test_name, passed in results:
            status = "✓ 通过" if passed else "✗ 失败"
            print(f"{test_name:30s} {status}")
            if not passed:
                all_passed = False
        
        print("=" * 60)
        if all_passed:
            print("✓ 所有测试通过")
        else:
            print("✗ 部分测试失败")
        print("=" * 60)
        
    finally:
        db.close()


if __name__ == "__main__":
    main()
