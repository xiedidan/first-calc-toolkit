"""
测试导向规则复制功能（简化版）
"""
import requests
import json
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


def create_test_rule():
    """创建测试用的导向规则"""
    print("\n=== 创建测试导向规则 ===")
    
    rule_data = {
        "name": f"测试导向规则-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "category": "benchmark_ladder",
        "description": "这是一个用于测试复制功能的导向规则"
    }
    
    response = requests.post(
        f"{BASE_URL}/orientation-rules",
        headers=get_headers(),
        json=rule_data
    )
    
    if response.status_code == 200:
        rule = response.json()
        print(f"✓ 创建导向规则成功: ID={rule['id']}, 名称={rule['name']}")
        return rule
    else:
        print(f"✗ 创建导向规则失败: {response.text}")
        return None


def add_test_data_to_db(db, rule_id, hospital_id):
    """直接在数据库中添加测试数据"""
    from app.models.orientation_benchmark import OrientationBenchmark, BenchmarkType
    from app.models.orientation_ladder import OrientationLadder
    from datetime import timedelta
    
    print(f"\n=== 在数据库中为规则 {rule_id} 添加测试数据 ===")
    
    # 创建基准
    benchmark = OrientationBenchmark(
        hospital_id=hospital_id,
        rule_id=rule_id,
        department_code="TEST001",
        department_name="测试科室",
        benchmark_type=BenchmarkType.average,
        control_intensity=1.2345,
        stat_start_date=datetime.now() - timedelta(days=30),
        stat_end_date=datetime.now(),
        benchmark_value=100.5678
    )
    db.add(benchmark)
    
    # 创建阶梯
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
    print(f"✓ 添加了1个基准和2个阶梯")


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


def copy_rule(rule_id):
    """复制导向规则"""
    print(f"\n=== 复制导向规则 {rule_id} ===")
    
    response = requests.post(
        f"{BASE_URL}/orientation-rules/{rule_id}/copy",
        headers=get_headers()
    )
    
    if response.status_code == 200:
        new_rule = response.json()
        print(f"✓ 复制成功:")
        print(f"  - 新规则ID: {new_rule['id']}")
        print(f"  - 新规则名称: {new_rule['name']}")
        print(f"  - 类别: {new_rule['category']}")
        
        # 验证名称包含"（副本）"
        if "（副本）" in new_rule['name']:
            print(f"✓ 名称正确添加了'（副本）'标识")
        else:
            print(f"✗ 名称未添加'（副本）'标识")
        
        return new_rule
    else:
        print(f"✗ 复制失败: {response.text}")
        return None


def verify_copy(db, original_rule_id, new_rule_id):
    """验证复制结果"""
    print(f"\n=== 验证复制结果 ===")
    
    # 统计原始规则的关联数据
    orig_benchmarks, orig_ladders = count_related_data(db, original_rule_id)
    
    # 统计新规则的关联数据
    new_benchmarks, new_ladders = count_related_data(db, new_rule_id)
    
    print(f"\n原始规则 (ID={original_rule_id}):")
    print(f"  - 基准数量: {orig_benchmarks}")
    print(f"  - 阶梯数量: {orig_ladders}")
    
    print(f"\n新规则 (ID={new_rule_id}):")
    print(f"  - 基准数量: {new_benchmarks}")
    print(f"  - 阶梯数量: {new_ladders}")
    
    # 验证数量是否一致
    success = True
    if orig_benchmarks != new_benchmarks:
        print(f"✗ 基准数量不一致")
        success = False
    else:
        print(f"✓ 基准数量一致")
    
    if orig_ladders != new_ladders:
        print(f"✗ 阶梯数量不一致")
        success = False
    else:
        print(f"✓ 阶梯数量一致")
    
    return success


def cleanup_rule(rule_id):
    """清理测试数据"""
    print(f"\n=== 清理测试数据 (规则ID={rule_id}) ===")
    
    response = requests.delete(
        f"{BASE_URL}/orientation-rules/{rule_id}",
        headers=get_headers()
    )
    
    if response.status_code == 200:
        print(f"✓ 删除成功")
    else:
        print(f"✗ 删除失败: {response.text}")


def main():
    """主测试流程"""
    print("=" * 60)
    print("导向规则复制功能测试")
    print("=" * 60)
    
    # 登录
    login()
    
    # 获取数据库会话
    db = get_db_session()
    
    try:
        # 创建测试导向规则
        rule = create_test_rule()
        if not rule:
            return
        
        rule_id = rule["id"]
        
        # 在数据库中添加测试数据
        add_test_data_to_db(db, rule_id, HOSPITAL_ID)
        
        # 复制导向规则
        new_rule = copy_rule(rule_id)
        if not new_rule:
            cleanup_rule(rule_id)
            return
        
        new_rule_id = new_rule["id"]
        
        # 验证复制结果
        success = verify_copy(db, rule_id, new_rule_id)
        
        # 清理测试数据
        cleanup_rule(rule_id)
        cleanup_rule(new_rule_id)
        
        print("\n" + "=" * 60)
        if success:
            print("✓ 所有测试通过")
        else:
            print("✗ 部分测试失败")
        print("=" * 60)
    finally:
        db.close()


if __name__ == "__main__":
    main()
