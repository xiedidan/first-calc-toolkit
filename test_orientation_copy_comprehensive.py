"""
导向规则复制功能 - 综合测试
"""
import requests
from datetime import datetime, timedelta
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv("backend/.env")

BASE_URL = "http://localhost:8000/api/v1"
HOSPITAL_ID = 1
TOKEN = None


def login():
    """登录"""
    global TOKEN
    response = requests.post(
        f"{BASE_URL}/auth/login",
        json={"username": "admin", "password": "admin123"}
    )
    if response.status_code == 200:
        TOKEN = response.json()["access_token"]
        return True
    return False


def get_headers():
    """获取请求头"""
    return {
        "Authorization": f"Bearer {TOKEN}",
        "X-Hospital-ID": str(HOSPITAL_ID),
        "Content-Type": "application/json"
    }


def get_db():
    """获取数据库会话"""
    database_url = os.getenv("DATABASE_URL")
    engine = create_engine(database_url)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return SessionLocal()


def create_rule(name, category, description):
    """创建导向规则"""
    response = requests.post(
        f"{BASE_URL}/orientation-rules",
        headers=get_headers(),
        json={"name": name, "category": category, "description": description}
    )
    return response.json() if response.status_code == 200 else None


def copy_rule(rule_id):
    """复制导向规则"""
    response = requests.post(
        f"{BASE_URL}/orientation-rules/{rule_id}/copy",
        headers=get_headers()
    )
    return response.json() if response.status_code == 200 else None


def delete_rule(rule_id):
    """删除导向规则"""
    response = requests.delete(
        f"{BASE_URL}/orientation-rules/{rule_id}",
        headers=get_headers()
    )
    return response.status_code == 200


def add_benchmark(db, rule_id):
    """添加基准"""
    from app.models.orientation_benchmark import OrientationBenchmark, BenchmarkType
    
    benchmark = OrientationBenchmark(
        hospital_id=HOSPITAL_ID,
        rule_id=rule_id,
        department_code=f"DEPT{rule_id}",
        department_name=f"测试科室{rule_id}",
        benchmark_type=BenchmarkType.average,
        control_intensity=1.5,
        stat_start_date=datetime.now() - timedelta(days=30),
        stat_end_date=datetime.now(),
        benchmark_value=100.0
    )
    db.add(benchmark)
    db.commit()


def add_ladder(db, rule_id, order):
    """添加阶梯"""
    from app.models.orientation_ladder import OrientationLadder
    
    ladder = OrientationLadder(
        hospital_id=HOSPITAL_ID,
        rule_id=rule_id,
        ladder_order=order,
        lower_limit=order * 10.0,
        upper_limit=(order + 1) * 10.0,
        adjustment_intensity=0.5 + order * 0.1
    )
    db.add(ladder)
    db.commit()


def count_data(db, rule_id):
    """统计关联数据"""
    from app.models.orientation_benchmark import OrientationBenchmark
    from app.models.orientation_ladder import OrientationLadder
    
    benchmarks = db.query(OrientationBenchmark).filter(
        OrientationBenchmark.rule_id == rule_id
    ).count()
    
    ladders = db.query(OrientationLadder).filter(
        OrientationLadder.rule_id == rule_id
    ).count()
    
    return benchmarks, ladders


def print_header(text):
    """打印标题"""
    print(f"\n{'=' * 70}")
    print(f"  {text}")
    print('=' * 70)


def print_test(name, passed):
    """打印测试结果"""
    status = "✓" if passed else "✗"
    print(f"  {status} {name}")
    return passed


def main():
    """主测试流程"""
    print_header("导向规则复制功能 - 综合测试")
    
    if not login():
        print("✗ 登录失败")
        return
    
    print("✓ 登录成功")
    
    db = get_db()
    test_results = []
    cleanup_ids = []
    
    try:
        # 测试1: benchmark_ladder类别完整复制
        print_header("测试1: benchmark_ladder 类别完整复制")
        
        rule1 = create_rule(
            f"基准阶梯测试-{datetime.now().strftime('%H%M%S')}",
            "benchmark_ladder",
            "测试基准阶梯类别的完整复制"
        )
        
        if rule1:
            cleanup_ids.append(rule1['id'])
            add_benchmark(db, rule1['id'])
            add_ladder(db, rule1['id'], 1)
            add_ladder(db, rule1['id'], 2)
            
            orig_b, orig_l = count_data(db, rule1['id'])
            print(f"  原始规则: {orig_b}个基准, {orig_l}个阶梯")
            
            new_rule1 = copy_rule(rule1['id'])
            if new_rule1:
                cleanup_ids.append(new_rule1['id'])
                new_b, new_l = count_data(db, new_rule1['id'])
                print(f"  新规则: {new_b}个基准, {new_l}个阶梯")
                
                test_results.append(print_test(
                    "名称包含'（副本）'",
                    "（副本）" in new_rule1['name']
                ))
                test_results.append(print_test(
                    "基准数量一致",
                    orig_b == new_b == 1
                ))
                test_results.append(print_test(
                    "阶梯数量一致",
                    orig_l == new_l == 2
                ))
        
        # 测试2: direct_ladder类别仅复制阶梯
        print_header("测试2: direct_ladder 类别仅复制阶梯")
        
        rule2 = create_rule(
            f"直接阶梯测试-{datetime.now().strftime('%H%M%S')}",
            "direct_ladder",
            "测试直接阶梯类别仅复制阶梯"
        )
        
        if rule2:
            cleanup_ids.append(rule2['id'])
            add_ladder(db, rule2['id'], 1)
            add_ladder(db, rule2['id'], 2)
            add_ladder(db, rule2['id'], 3)
            
            orig_b, orig_l = count_data(db, rule2['id'])
            print(f"  原始规则: {orig_b}个基准, {orig_l}个阶梯")
            
            new_rule2 = copy_rule(rule2['id'])
            if new_rule2:
                cleanup_ids.append(new_rule2['id'])
                new_b, new_l = count_data(db, new_rule2['id'])
                print(f"  新规则: {new_b}个基准, {new_l}个阶梯")
                
                test_results.append(print_test(
                    "不复制基准",
                    new_b == 0
                ))
                test_results.append(print_test(
                    "阶梯数量一致",
                    orig_l == new_l == 3
                ))
        
        # 测试3: other类别不复制关联数据
        print_header("测试3: other 类别不复制关联数据")
        
        rule3 = create_rule(
            f"其他类别测试-{datetime.now().strftime('%H%M%S')}",
            "other",
            "测试其他类别不复制关联数据"
        )
        
        if rule3:
            cleanup_ids.append(rule3['id'])
            
            new_rule3 = copy_rule(rule3['id'])
            if new_rule3:
                cleanup_ids.append(new_rule3['id'])
                new_b, new_l = count_data(db, new_rule3['id'])
                print(f"  新规则: {new_b}个基准, {new_l}个阶梯")
                
                test_results.append(print_test(
                    "不复制基准",
                    new_b == 0
                ))
                test_results.append(print_test(
                    "不复制阶梯",
                    new_l == 0
                ))
        
        # 测试4: 多次复制
        print_header("测试4: 多次复制")
        
        rule4 = create_rule(
            f"多次复制测试-{datetime.now().strftime('%H%M%S')}",
            "other",
            "测试多次复制名称累加"
        )
        
        if rule4:
            cleanup_ids.append(rule4['id'])
            
            # 第一次复制
            copy1 = copy_rule(rule4['id'])
            if copy1:
                cleanup_ids.append(copy1['id'])
                test_results.append(print_test(
                    "第一次复制名称正确",
                    copy1['name'].count("（副本）") == 1
                ))
                
                # 第二次复制
                copy2 = copy_rule(copy1['id'])
                if copy2:
                    cleanup_ids.append(copy2['id'])
                    test_results.append(print_test(
                        "第二次复制名称正确",
                        copy2['name'].count("（副本）") == 2
                    ))
        
        # 测试5: 错误处理
        print_header("测试5: 错误处理")
        
        # 复制不存在的规则
        response = requests.post(
            f"{BASE_URL}/orientation-rules/999999/copy",
            headers=get_headers()
        )
        test_results.append(print_test(
            "复制不存在的规则返回404",
            response.status_code == 404
        ))
        
        # 输出总结
        print_header("测试总结")
        
        passed = sum(test_results)
        total = len(test_results)
        
        print(f"\n  通过: {passed}/{total}")
        print(f"  失败: {total - passed}/{total}")
        print(f"  成功率: {passed/total*100:.1f}%")
        
        if passed == total:
            print("\n  ✓ 所有测试通过!")
        else:
            print("\n  ✗ 部分测试失败")
        
    finally:
        # 清理测试数据
        print_header("清理测试数据")
        for rule_id in cleanup_ids:
            if delete_rule(rule_id):
                print(f"  ✓ 删除规则 {rule_id}")
            else:
                print(f"  ✗ 删除规则 {rule_id} 失败")
        
        db.close()
        print()


if __name__ == "__main__":
    main()
