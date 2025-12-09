"""
测试不同类别导向规则的复制功能
"""
import requests
import json
from datetime import datetime, timedelta
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


def create_test_rule(category, name_suffix):
    """创建测试用的导向规则"""
    print(f"\n=== 创建{category}类别的测试导向规则 ===")
    
    rule_data = {
        "name": f"测试{name_suffix}-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "category": category,
        "description": f"测试{category}类别的复制功能"
    }
    
    response = requests.post(
        f"{BASE_URL}/orientation-rules",
        headers=get_headers(),
        json=rule_data
    )
    
    if response.status_code == 200:
        rule = response.json()
        print(f"✓ 创建成功: ID={rule['id']}, 名称={rule['name']}")
        return rule
    else:
        print(f"✗ 创建失败: {response.text}")
        return None


def add_ladders_only(db, rule_id, hospital_id):
    """仅添加阶梯数据（用于direct_ladder类别）"""
    from app.models.orientation_ladder import OrientationLadder
    
    print(f"  添加阶梯数据...")
    
    for i in range(1, 3):
        ladder = OrientationLadder(
            hospital_id=hospital_id,
            rule_id=rule_id,
            ladder_order=i,
            lower_limit=i * 10.0,
            upper_limit=(i + 1) * 10.0,
            adjustment_intensity=0.5 + i * 0.1
        )
        db.add(ladder)
    
    db.commit()
    print(f"  ✓ 添加了2个阶梯")


def count_related_data(db, rule_id):
    """统计规则的关联数据"""
    from app.models.orientation_benchmark import OrientationBenchmark
    from app.models.orientation_ladder import OrientationLadder
    
    benchmark_count = db.query(OrientationBenchmark).filter(
        OrientationBenchmark.rule_id == rule_id
    ).count()
    
    ladder_count = db.query(OrientationLadder).filter(
        OrientationLadder.rule_id == rule_id
    ).count()
    
    return benchmark_count, ladder_count


def copy_and_verify(db, rule_id, expected_benchmarks, expected_ladders):
    """复制并验证"""
    print(f"\n  复制规则 {rule_id}...")
    
    response = requests.post(
        f"{BASE_URL}/orientation-rules/{rule_id}/copy",
        headers=get_headers()
    )
    
    if response.status_code != 200:
        print(f"  ✗ 复制失败: {response.text}")
        return None, False
    
    new_rule = response.json()
    print(f"  ✓ 复制成功: 新规则ID={new_rule['id']}")
    
    # 验证名称
    if "（副本）" not in new_rule['name']:
        print(f"  ✗ 名称未添加'（副本）'标识")
        return new_rule['id'], False
    
    # 验证关联数据
    new_benchmarks, new_ladders = count_related_data(db, new_rule['id'])
    
    success = True
    if new_benchmarks != expected_benchmarks:
        print(f"  ✗ 基准数量不正确: 期望{expected_benchmarks}, 实际{new_benchmarks}")
        success = False
    else:
        print(f"  ✓ 基准数量正确: {new_benchmarks}")
    
    if new_ladders != expected_ladders:
        print(f"  ✗ 阶梯数量不正确: 期望{expected_ladders}, 实际{new_ladders}")
        success = False
    else:
        print(f"  ✓ 阶梯数量正确: {new_ladders}")
    
    return new_rule['id'], success


def cleanup_rule(rule_id):
    """清理测试数据"""
    response = requests.delete(
        f"{BASE_URL}/orientation-rules/{rule_id}",
        headers=get_headers()
    )
    return response.status_code == 200


def test_direct_ladder_category(db):
    """测试direct_ladder类别（仅复制阶梯）"""
    print("\n" + "=" * 60)
    print("测试 direct_ladder 类别")
    print("=" * 60)
    
    # 创建规则
    rule = create_test_rule("direct_ladder", "直接阶梯")
    if not rule:
        return False
    
    rule_id = rule["id"]
    
    # 添加阶梯数据
    add_ladders_only(db, rule_id, HOSPITAL_ID)
    
    # 复制并验证（应该只复制阶梯，不复制基准）
    new_rule_id, success = copy_and_verify(db, rule_id, expected_benchmarks=0, expected_ladders=2)
    
    # 清理
    cleanup_rule(rule_id)
    if new_rule_id:
        cleanup_rule(new_rule_id)
    
    return success


def test_other_category(db):
    """测试other类别（不复制任何关联数据）"""
    print("\n" + "=" * 60)
    print("测试 other 类别")
    print("=" * 60)
    
    # 创建规则
    rule = create_test_rule("other", "其他")
    if not rule:
        return False
    
    rule_id = rule["id"]
    
    # 复制并验证（不应该复制任何关联数据）
    new_rule_id, success = copy_and_verify(db, rule_id, expected_benchmarks=0, expected_ladders=0)
    
    # 清理
    cleanup_rule(rule_id)
    if new_rule_id:
        cleanup_rule(new_rule_id)
    
    return success


def main():
    """主测试流程"""
    print("=" * 60)
    print("导向规则复制功能 - 不同类别测试")
    print("=" * 60)
    
    # 登录
    login()
    
    # 获取数据库会话
    db = get_db_session()
    
    try:
        results = []
        
        # 测试direct_ladder类别
        results.append(("direct_ladder", test_direct_ladder_category(db)))
        
        # 测试other类别
        results.append(("other", test_other_category(db)))
        
        # 输出总结
        print("\n" + "=" * 60)
        print("测试总结")
        print("=" * 60)
        
        all_passed = True
        for category, passed in results:
            status = "✓ 通过" if passed else "✗ 失败"
            print(f"{category:20s} {status}")
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
