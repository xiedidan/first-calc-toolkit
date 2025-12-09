"""
测试导向规则复制功能
"""
import requests
import json
from datetime import datetime, timedelta

# API基础URL
BASE_URL = "http://localhost:8000/api/v1"

# 测试用的医疗机构ID和认证token
HOSPITAL_ID = 1
TOKEN = None  # 需要先登录获取


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
        print(f"✓ 登录成功，获取token")
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


def create_test_rule():
    """创建测试用的导向规则"""
    print("\n=== 创建测试导向规则 ===")
    
    # 创建基准阶梯类型的导向规则
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


def create_test_benchmark_direct(db, rule_id, hospital_id):
    """直接在数据库中创建测试基准（API尚未实现）"""
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from backend.app.models.orientation_benchmark import OrientationBenchmark, BenchmarkType
    
    print(f"\n=== 直接在数据库中为导向规则 {rule_id} 创建基准 ===")
    
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
    db.commit()
    db.refresh(benchmark)
    print(f"✓ 创建基准成功: ID={benchmark.id}")
    return benchmark


def create_test_ladder_direct(db, rule_id, hospital_id, order):
    """直接在数据库中创建测试阶梯（API尚未实现）"""
    from backend.app.models.orientation_ladder import OrientationLadder
    
    print(f"\n=== 直接在数据库中为导向规则 {rule_id} 创建阶梯 {order} ===")
    
    ladder = OrientationLadder(
        hospital_id=hospital_id,
        rule_id=rule_id,
        ladder_order=order,
        lower_limit=order * 10.0,
        upper_limit=(order + 1) * 10.0,
        adjustment_intensity=0.5 + order * 0.1
    )
    
    db.add(ladder)
    db.commit()
    db.refresh(ladder)
    print(f"✓ 创建阶梯成功: ID={ladder.id}, 次序={ladder.ladder_order}")
    return ladder


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
        return new_rule
    else:
        print(f"✗ 复制失败: {response.text}")
        return None


def get_benchmarks_direct(db, rule_id):
    """直接从数据库获取导向规则的基准列表"""
    from backend.app.models.orientation_benchmark import OrientationBenchmark
    
    benchmarks = db.query(OrientationBenchmark).filter(
        OrientationBenchmark.rule_id == rule_id
    ).all()
    return benchmarks


def get_ladders_direct(db, rule_id):
    """直接从数据库获取导向规则的阶梯列表"""
    from backend.app.models.orientation_ladder import OrientationLadder
    
    ladders = db.query(OrientationLadder).filter(
        OrientationLadder.rule_id == rule_id
    ).all()
    return ladders


def verify_copy(db, original_rule_id, new_rule_id):
    """验证复制结果"""
    print(f"\n=== 验证复制结果 ===")
    
    # 获取原始规则的基准和阶梯
    original_benchmarks = get_benchmarks_direct(db, original_rule_id)
    original_ladders = get_ladders_direct(db, original_rule_id)
    
    # 获取新规则的基准和阶梯
    new_benchmarks = get_benchmarks_direct(db, new_rule_id)
    new_ladders = get_ladders_direct(db, new_rule_id)
    
    print(f"\n原始规则 (ID={original_rule_id}):")
    print(f"  - 基准数量: {len(original_benchmarks)}")
    print(f"  - 阶梯数量: {len(original_ladders)}")
    
    print(f"\n新规则 (ID={new_rule_id}):")
    print(f"  - 基准数量: {len(new_benchmarks)}")
    print(f"  - 阶梯数量: {len(new_ladders)}")
    
    # 验证数量是否一致
    success = True
    if len(original_benchmarks) != len(new_benchmarks):
        print(f"✗ 基准数量不一致")
        success = False
    else:
        print(f"✓ 基准数量一致")
    
    if len(original_ladders) != len(new_ladders):
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


def get_db_session():
    """获取数据库会话"""
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    import os
    from dotenv import load_dotenv
    
    # 加载环境变量
    load_dotenv("backend/.env")
    
    database_url = os.getenv("DATABASE_URL")
    engine = create_engine(database_url)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return SessionLocal()


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
        
        # 创建关联数据（直接在数据库中）
        create_test_benchmark_direct(db, rule_id, HOSPITAL_ID)
        create_test_ladder_direct(db, rule_id, HOSPITAL_ID, 1)
        create_test_ladder_direct(db, rule_id, HOSPITAL_ID, 2)
        
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
            print("✓ 测试通过")
        else:
            print("✗ 测试失败")
        print("=" * 60)
    finally:
        db.close()


if __name__ == "__main__":
    main()
