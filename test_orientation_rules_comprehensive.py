"""
综合测试导向规则API - 包括多租户隔离和关联检查
"""
import sys
sys.path.insert(0, 'backend')

from fastapi.testclient import TestClient
from app.main import app
from app.database import SessionLocal
from app.models.user import User
from app.models.hospital import Hospital
from app.models.orientation_rule import OrientationRule, OrientationCategory
from app.models.model_node import ModelNode
from app.utils.security import create_access_token

client = TestClient(app)

def get_test_token_and_hospital():
    """获取测试token和医疗机构"""
    db = SessionLocal()
    try:
        user = db.query(User).first()
        hospital = db.query(Hospital).first()
        
        if not user or not hospital:
            return None, None
        
        token = create_access_token(
            data={"sub": str(user.id), "username": user.username}
        )
        
        return token, hospital.id
    finally:
        db.close()


def test_duplicate_name_validation(token, hospital_id):
    """测试重复名称验证"""
    print("\n=== 测试重复名称验证 ===")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "X-Hospital-ID": str(hospital_id)
    }
    
    # 创建第一个规则
    data1 = {
        "name": "重复名称测试",
        "category": "benchmark_ladder",
        "description": "第一个规则"
    }
    response1 = client.post("/api/v1/orientation-rules", headers=headers, json=data1)
    print(f"创建第一个规则 - 状态码: {response1.status_code}")
    
    if response1.status_code == 200:
        rule_id = response1.json()['id']
        
        # 尝试创建同名规则
        data2 = {
            "name": "重复名称测试",
            "category": "direct_ladder",
            "description": "第二个规则"
        }
        response2 = client.post("/api/v1/orientation-rules", headers=headers, json=data2)
        print(f"创建同名规则 - 状态码: {response2.status_code}")
        
        if response2.status_code == 400:
            print(f"✓ 正确拒绝重复名称: {response2.json()['detail']}")
        else:
            print(f"✗ 应该拒绝重复名称")
        
        # 清理
        client.delete(f"/api/v1/orientation-rules/{rule_id}", headers=headers)
    else:
        print(f"✗ 创建第一个规则失败")


def test_delete_with_association(token, hospital_id):
    """测试有关联时的删除约束"""
    print("\n=== 测试删除关联检查 ===")
    
    db = SessionLocal()
    try:
        # 创建一个导向规则
        rule = OrientationRule(
            hospital_id=hospital_id,
            name="关联测试规则",
            category=OrientationCategory.benchmark_ladder,
            description="用于测试关联的规则"
        )
        db.add(rule)
        db.commit()
        db.refresh(rule)
        print(f"创建测试规则: ID={rule.id}")
        
        # 查找一个模型节点并关联（通过version关联hospital）
        from app.models.model_version import ModelVersion
        node = db.query(ModelNode).join(
            ModelVersion, ModelNode.version_id == ModelVersion.id
        ).filter(
            ModelVersion.hospital_id == hospital_id
        ).first()
        
        if node:
            node.orientation_rule_id = rule.id
            db.commit()
            print(f"关联模型节点: ID={node.id}")
            
            # 尝试删除规则
            headers = {
                "Authorization": f"Bearer {token}",
                "X-Hospital-ID": str(hospital_id)
            }
            
            response = client.delete(f"/api/v1/orientation-rules/{rule.id}", headers=headers)
            print(f"删除关联规则 - 状态码: {response.status_code}")
            
            if response.status_code == 400:
                print(f"✓ 正确阻止删除: {response.json()['detail']}")
            else:
                print(f"✗ 应该阻止删除有关联的规则")
            
            # 清理：先解除关联
            node.orientation_rule_id = None
            db.commit()
            
            # 再删除规则
            response = client.delete(f"/api/v1/orientation-rules/{rule.id}", headers=headers)
            if response.status_code == 200:
                print("✓ 解除关联后成功删除")
            else:
                db.delete(rule)
                db.commit()
        else:
            print("⚠ 没有找到模型节点，跳过关联测试")
            db.delete(rule)
            db.commit()
            
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        db.rollback()
    finally:
        db.close()


def test_field_validation(token, hospital_id):
    """测试字段验证"""
    print("\n=== 测试字段验证 ===")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "X-Hospital-ID": str(hospital_id)
    }
    
    # 测试空名称
    data = {
        "name": "",
        "category": "benchmark_ladder"
    }
    response = client.post("/api/v1/orientation-rules", headers=headers, json=data)
    print(f"空名称 - 状态码: {response.status_code}")
    if response.status_code == 400:
        print("✓ 正确拒绝空名称")
    
    # 测试名称过长
    data = {
        "name": "a" * 101,
        "category": "benchmark_ladder"
    }
    response = client.post("/api/v1/orientation-rules", headers=headers, json=data)
    print(f"名称过长 - 状态码: {response.status_code}")
    if response.status_code == 400 or response.status_code == 422:
        print("✓ 正确拒绝过长名称")
    
    # 测试描述过长
    data = {
        "name": "描述过长测试",
        "category": "benchmark_ladder",
        "description": "a" * 1025
    }
    response = client.post("/api/v1/orientation-rules", headers=headers, json=data)
    print(f"描述过长 - 状态码: {response.status_code}")
    if response.status_code == 400 or response.status_code == 422:
        print("✓ 正确拒绝过长描述")
    
    # 测试无效类别
    data = {
        "name": "无效类别测试",
        "category": "invalid_category"
    }
    response = client.post("/api/v1/orientation-rules", headers=headers, json=data)
    print(f"无效类别 - 状态码: {response.status_code}")
    if response.status_code == 400 or response.status_code == 422:
        print("✓ 正确拒绝无效类别")


def test_pagination(token, hospital_id):
    """测试分页功能"""
    print("\n=== 测试分页功能 ===")
    
    db = SessionLocal()
    headers = {
        "Authorization": f"Bearer {token}",
        "X-Hospital-ID": str(hospital_id)
    }
    
    try:
        # 创建多个规则
        rule_ids = []
        for i in range(5):
            rule = OrientationRule(
                hospital_id=hospital_id,
                name=f"分页测试规则{i+1}",
                category=OrientationCategory.benchmark_ladder,
                description=f"第{i+1}个规则"
            )
            db.add(rule)
            db.commit()
            db.refresh(rule)
            rule_ids.append(rule.id)
        
        print(f"创建了 {len(rule_ids)} 个规则")
        
        # 测试第一页
        response = client.get("/api/v1/orientation-rules?page=1&size=2", headers=headers)
        if response.status_code == 200:
            result = response.json()
            print(f"✓ 第一页: {len(result['items'])} 条记录，总计 {result['total']} 条")
        
        # 测试第二页
        response = client.get("/api/v1/orientation-rules?page=2&size=2", headers=headers)
        if response.status_code == 200:
            result = response.json()
            print(f"✓ 第二页: {len(result['items'])} 条记录")
        
        # 清理
        for rule_id in rule_ids:
            client.delete(f"/api/v1/orientation-rules/{rule_id}", headers=headers)
        
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        db.rollback()
    finally:
        db.close()


def test_category_filter(token, hospital_id):
    """测试类别筛选"""
    print("\n=== 测试类别筛选 ===")
    
    db = SessionLocal()
    headers = {
        "Authorization": f"Bearer {token}",
        "X-Hospital-ID": str(hospital_id)
    }
    
    try:
        # 创建不同类别的规则
        rule1 = OrientationRule(
            hospital_id=hospital_id,
            name="基准阶梯规则",
            category=OrientationCategory.benchmark_ladder
        )
        rule2 = OrientationRule(
            hospital_id=hospital_id,
            name="直接阶梯规则",
            category=OrientationCategory.direct_ladder
        )
        rule3 = OrientationRule(
            hospital_id=hospital_id,
            name="其他规则",
            category=OrientationCategory.other
        )
        
        db.add_all([rule1, rule2, rule3])
        db.commit()
        
        # 筛选基准阶梯
        response = client.get("/api/v1/orientation-rules?category=benchmark_ladder", headers=headers)
        if response.status_code == 200:
            result = response.json()
            benchmark_count = sum(1 for item in result['items'] if item['category'] == 'benchmark_ladder')
            print(f"✓ 基准阶梯类别: {benchmark_count} 条记录")
        
        # 筛选直接阶梯
        response = client.get("/api/v1/orientation-rules?category=direct_ladder", headers=headers)
        if response.status_code == 200:
            result = response.json()
            direct_count = sum(1 for item in result['items'] if item['category'] == 'direct_ladder')
            print(f"✓ 直接阶梯类别: {direct_count} 条记录")
        
        # 清理
        db.delete(rule1)
        db.delete(rule2)
        db.delete(rule3)
        db.commit()
        
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        db.rollback()
    finally:
        db.close()


def main():
    """主测试流程"""
    print("开始综合测试导向规则API...")
    
    token, hospital_id = get_test_token_and_hospital()
    if not token or not hospital_id:
        print("无法获取测试环境，测试终止")
        return
    
    print(f"使用医疗机构ID: {hospital_id}")
    
    # 运行各项测试
    test_duplicate_name_validation(token, hospital_id)
    test_delete_with_association(token, hospital_id)
    test_field_validation(token, hospital_id)
    test_pagination(token, hospital_id)
    test_category_filter(token, hospital_id)
    
    print("\n所有综合测试完成！")


if __name__ == "__main__":
    main()
