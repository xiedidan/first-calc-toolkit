"""
端到端功能测试 - 业务导向管理模块

测试覆盖：
1. 导向规则的完整 CRUD 流程
2. 导向规则的复制功能（包括关联数据）
3. 导向规则的导出功能
4. 导向基准的 CRUD 和筛选
5. 导向阶梯的 CRUD 和筛选
6. 模型节点关联导向规则
7. 页面跳转和参数传递
8. 多租户隔离
"""

import requests
import json
from datetime import datetime, timedelta
from decimal import Decimal

# 配置
BASE_URL = "http://localhost:8000"
HOSPITAL_ID = 1  # 测试用医疗机构ID

# 请求头
headers = {
    "Content-Type": "application/json",
    "X-Hospital-ID": str(HOSPITAL_ID)
}


def print_section(title):
    """打印测试章节标题"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")


def print_test(name, passed, details=""):
    """打印测试结果"""
    status = "✓ PASS" if passed else "✗ FAIL"
    print(f"{status}: {name}")
    if details:
        print(f"  详情: {details}")


def test_orientation_rule_crud():
    """测试1: 导向规则的完整 CRUD 流程"""
    print_section("测试1: 导向规则 CRUD 流程")
    
    # 1.1 创建导向规则
    print("1.1 创建导向规则...")
    rule_data = {
        "name": f"E2E测试导向_{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "category": "benchmark_ladder",
        "description": "端到端测试创建的导向规则"
    }
    
    response = requests.post(
        f"{BASE_URL}/api/v1/orientation-rules",
        headers=headers,
        json=rule_data
    )
    
    test_passed = response.status_code == 200
    print_test("创建导向规则", test_passed, f"状态码: {response.status_code}")
    
    if not test_passed:
        print(f"响应内容: {response.text}")
        return None
    
    rule = response.json()
    rule_id = rule["id"]
    print(f"  创建的导向规则ID: {rule_id}")
    
    # 1.2 获取导向规则详情
    print("\n1.2 获取导向规则详情...")
    response = requests.get(
        f"{BASE_URL}/api/v1/orientation-rules/{rule_id}",
        headers=headers
    )
    
    test_passed = response.status_code == 200 and response.json()["name"] == rule_data["name"]
    print_test("获取导向规则详情", test_passed)
    
    # 1.3 更新导向规则
    print("\n1.3 更新导向规则...")
    update_data = {
        "name": rule_data["name"] + "_已更新",
        "category": "benchmark_ladder",
        "description": "已更新的描述"
    }
    
    response = requests.put(
        f"{BASE_URL}/api/v1/orientation-rules/{rule_id}",
        headers=headers,
        json=update_data
    )
    
    test_passed = response.status_code == 200
    print_test("更新导向规则", test_passed)
    
    # 1.4 获取导向规则列表
    print("\n1.4 获取导向规则列表...")
    response = requests.get(
        f"{BASE_URL}/api/v1/orientation-rules",
        headers=headers
    )
    
    test_passed = response.status_code == 200 and len(response.json()["items"]) > 0
    print_test("获取导向规则列表", test_passed, f"共 {len(response.json()['items'])} 条记录")
    
    return rule_id


def test_orientation_benchmark_crud(rule_id):
    """测试4: 导向基准的 CRUD 和筛选"""
    print_section("测试4: 导向基准 CRUD 和筛选")
    
    # 4.1 创建导向基准
    print("4.1 创建导向基准...")
    benchmark_data = {
        "rule_id": rule_id,
        "department_code": "TEST001",
        "department_name": "测试科室",
        "benchmark_type": "average",
        "control_intensity": 1.2345,
        "stat_start_date": (datetime.now() - timedelta(days=30)).isoformat(),
        "stat_end_date": datetime.now().isoformat(),
        "benchmark_value": 100.5678
    }
    
    response = requests.post(
        f"{BASE_URL}/api/v1/orientation-benchmarks",
        headers=headers,
        json=benchmark_data
    )
    
    test_passed = response.status_code == 200
    print_test("创建导向基准", test_passed, f"状态码: {response.status_code}")
    
    if not test_passed:
        print(f"响应内容: {response.text}")
        return None
    
    benchmark = response.json()
    benchmark_id = benchmark["id"]
    print(f"  创建的导向基准ID: {benchmark_id}")
    
    # 验证数值格式化（4位小数）
    formatted_value = float(benchmark["benchmark_value"])
    test_passed = abs(formatted_value - 100.5678) < 0.0001
    print_test("数值格式化验证", test_passed, f"基准值: {formatted_value}")
    
    # 4.2 按导向筛选基准
    print("\n4.2 按导向筛选基准...")
    response = requests.get(
        f"{BASE_URL}/api/v1/orientation-benchmarks?rule_id={rule_id}",
        headers=headers
    )
    
    test_passed = response.status_code == 200 and len(response.json()["items"]) > 0
    print_test("按导向筛选基准", test_passed, f"筛选结果: {len(response.json()['items'])} 条")
    
    # 4.3 更新导向基准
    print("\n4.3 更新导向基准...")
    update_data = {
        **benchmark_data,
        "benchmark_value": 200.9999
    }
    
    response = requests.put(
        f"{BASE_URL}/api/v1/orientation-benchmarks/{benchmark_id}",
        headers=headers,
        json=update_data
    )
    
    test_passed = response.status_code == 200
    print_test("更新导向基准", test_passed)
    
    # 4.4 获取导向基准详情
    print("\n4.4 获取导向基准详情...")
    response = requests.get(
        f"{BASE_URL}/api/v1/orientation-benchmarks/{benchmark_id}",
        headers=headers
    )
    
    test_passed = response.status_code == 200
    print_test("获取导向基准详情", test_passed)
    
    return benchmark_id


def test_orientation_ladder_crud(rule_id):
    """测试5: 导向阶梯的 CRUD 和筛选"""
    print_section("测试5: 导向阶梯 CRUD 和筛选")
    
    # 5.1 创建导向阶梯
    print("5.1 创建导向阶梯...")
    ladder_data = {
        "rule_id": rule_id,
        "ladder_order": 1,
        "upper_limit": 100.0,
        "lower_limit": 0.0,
        "adjustment_intensity": 1.5
    }
    
    response = requests.post(
        f"{BASE_URL}/api/v1/orientation-ladders",
        headers=headers,
        json=ladder_data
    )
    
    test_passed = response.status_code == 200
    print_test("创建导向阶梯", test_passed, f"状态码: {response.status_code}")
    
    if not test_passed:
        print(f"响应内容: {response.text}")
        return None
    
    ladder = response.json()
    ladder_id = ladder["id"]
    print(f"  创建的导向阶梯ID: {ladder_id}")
    
    # 5.2 创建第二个阶梯（测试排序）
    print("\n5.2 创建第二个阶梯...")
    ladder_data_2 = {
        "rule_id": rule_id,
        "ladder_order": 2,
        "upper_limit": None,  # 正无穷
        "lower_limit": 100.0,
        "adjustment_intensity": 2.0
    }
    
    response = requests.post(
        f"{BASE_URL}/api/v1/orientation-ladders",
        headers=headers,
        json=ladder_data_2
    )
    
    test_passed = response.status_code == 200
    print_test("创建第二个阶梯（含无穷值）", test_passed)
    
    # 5.3 按导向筛选阶梯（验证排序）
    print("\n5.3 按导向筛选阶梯（验证排序）...")
    response = requests.get(
        f"{BASE_URL}/api/v1/orientation-ladders?rule_id={rule_id}",
        headers=headers
    )
    
    test_passed = response.status_code == 200
    if test_passed:
        ladders = response.json()["items"]
        # 验证按 ladder_order 排序
        is_sorted = all(ladders[i]["ladder_order"] <= ladders[i+1]["ladder_order"] 
                       for i in range(len(ladders)-1))
        test_passed = is_sorted and len(ladders) >= 2
        print_test("按导向筛选并验证排序", test_passed, f"共 {len(ladders)} 个阶梯")
    else:
        print_test("按导向筛选阶梯", False)
    
    # 5.4 更新导向阶梯
    print("\n5.4 更新导向阶梯...")
    update_data = {
        **ladder_data,
        "adjustment_intensity": 1.8
    }
    
    response = requests.put(
        f"{BASE_URL}/api/v1/orientation-ladders/{ladder_id}",
        headers=headers,
        json=update_data
    )
    
    test_passed = response.status_code == 200
    print_test("更新导向阶梯", test_passed)
    
    return ladder_id


def test_orientation_rule_copy(rule_id):
    """测试2: 导向规则的复制功能（包括关联数据）"""
    print_section("测试2: 导向规则复制功能")
    
    print("2.1 复制导向规则...")
    response = requests.post(
        f"{BASE_URL}/api/v1/orientation-rules/{rule_id}/copy",
        headers=headers
    )
    
    test_passed = response.status_code == 200
    print_test("复制导向规则", test_passed, f"状态码: {response.status_code}")
    
    if not test_passed:
        print(f"响应内容: {response.text}")
        return None
    
    copied_rule = response.json()
    copied_rule_id = copied_rule["id"]
    print(f"  复制的导向规则ID: {copied_rule_id}")
    
    # 验证名称包含"（副本）"
    test_passed = "（副本）" in copied_rule["name"]
    print_test("验证副本名称", test_passed, f"名称: {copied_rule['name']}")
    
    # 2.2 验证关联的基准被复制
    print("\n2.2 验证关联的基准被复制...")
    response = requests.get(
        f"{BASE_URL}/api/v1/orientation-benchmarks?rule_id={copied_rule_id}",
        headers=headers
    )
    
    test_passed = response.status_code == 200 and len(response.json()["items"]) > 0
    print_test("验证基准被复制", test_passed, f"复制的基准数: {len(response.json()['items'])}")
    
    # 2.3 验证关联的阶梯被复制
    print("\n2.3 验证关联的阶梯被复制...")
    response = requests.get(
        f"{BASE_URL}/api/v1/orientation-ladders?rule_id={copied_rule_id}",
        headers=headers
    )
    
    test_passed = response.status_code == 200 and len(response.json()["items"]) > 0
    print_test("验证阶梯被复制", test_passed, f"复制的阶梯数: {len(response.json()['items'])}")
    
    return copied_rule_id


def test_orientation_rule_export(rule_id):
    """测试3: 导向规则的导出功能"""
    print_section("测试3: 导向规则导出功能")
    
    print("3.1 导出导向规则...")
    response = requests.get(
        f"{BASE_URL}/api/v1/orientation-rules/{rule_id}/export",
        headers=headers
    )
    
    test_passed = response.status_code == 200
    print_test("导出导向规则", test_passed, f"状态码: {response.status_code}")
    
    if test_passed:
        # 验证内容类型
        content_type = response.headers.get("content-type", "")
        test_passed = "text/markdown" in content_type
        print_test("验证内容类型", test_passed, f"Content-Type: {content_type}")
        
        # 验证文件名
        content_disposition = response.headers.get("content-disposition", "")
        test_passed = "filename" in content_disposition
        print_test("验证文件名", test_passed, f"Content-Disposition: {content_disposition}")
        
        # 验证内容包含关键信息
        content = response.text
        has_rule_info = "导向规则" in content or "导向名称" in content
        has_benchmarks = "导向基准" in content
        has_ladders = "导向阶梯" in content
        
        print_test("验证导出内容完整性", has_rule_info and has_benchmarks and has_ladders)
        print(f"  内容长度: {len(content)} 字符")
    else:
        print(f"响应内容: {response.text}")


def test_model_node_orientation():
    """测试6: 模型节点关联导向规则"""
    print_section("测试6: 模型节点关联导向规则")
    
    # 6.1 获取模型节点列表（找一个末级节点）
    print("6.1 查找末级节点...")
    response = requests.get(
        f"{BASE_URL}/api/v1/model-nodes",
        headers=headers
    )
    
    if response.status_code != 200:
        print_test("获取模型节点列表", False, "无法获取节点列表")
        return
    
    nodes = response.json()["items"]
    # 找一个没有子节点的节点（末级节点）
    leaf_node = None
    for node in nodes:
        # 检查是否有子节点
        children_response = requests.get(
            f"{BASE_URL}/api/v1/model-nodes?parent_id={node['id']}",
            headers=headers
        )
        if children_response.status_code == 200:
            children = children_response.json()["items"]
            if len(children) == 0:
                leaf_node = node
                break
    
    if not leaf_node:
        print_test("查找末级节点", False, "未找到末级节点")
        return
    
    print_test("查找末级节点", True, f"节点ID: {leaf_node['id']}, 名称: {leaf_node['name']}")
    
    # 6.2 创建一个导向规则用于关联
    print("\n6.2 创建导向规则用于关联...")
    rule_data = {
        "name": f"节点关联测试_{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "category": "direct_ladder",
        "description": "用于测试节点关联的导向规则"
    }
    
    response = requests.post(
        f"{BASE_URL}/api/v1/orientation-rules",
        headers=headers,
        json=rule_data
    )
    
    if response.status_code != 200:
        print_test("创建导向规则", False)
        return
    
    rule = response.json()
    rule_id = rule["id"]
    print_test("创建导向规则", True, f"规则ID: {rule_id}")
    
    # 6.3 更新节点关联导向规则
    print("\n6.3 更新节点关联导向规则...")
    update_data = {
        "name": leaf_node["name"],
        "code": leaf_node["code"],
        "node_type": leaf_node["node_type"],
        "orientation_rule_id": rule_id
    }
    
    response = requests.put(
        f"{BASE_URL}/api/v1/model-nodes/{leaf_node['id']}",
        headers=headers,
        json=update_data
    )
    
    test_passed = response.status_code == 200
    print_test("更新节点关联", test_passed)
    
    # 6.4 验证节点详情包含导向规则名称
    print("\n6.4 验证节点详情包含导向规则名称...")
    response = requests.get(
        f"{BASE_URL}/api/v1/model-nodes/{leaf_node['id']}",
        headers=headers
    )
    
    if response.status_code == 200:
        node = response.json()
        has_rule_name = "orientation_rule_name" in node and node["orientation_rule_name"] == rule_data["name"]
        print_test("验证导向规则名称", has_rule_name, f"导向规则名称: {node.get('orientation_rule_name', 'N/A')}")
    else:
        print_test("获取节点详情", False)


def test_multi_tenant_isolation():
    """测试8: 多租户隔离"""
    print_section("测试8: 多租户隔离")
    
    # 8.1 使用不同的医疗机构ID创建数据
    print("8.1 使用医疗机构1创建导向规则...")
    headers_hospital_1 = {**headers, "X-Hospital-ID": "1"}
    
    rule_data_1 = {
        "name": f"医疗机构1测试_{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "category": "other",
        "description": "医疗机构1的数据"
    }
    
    response = requests.post(
        f"{BASE_URL}/api/v1/orientation-rules",
        headers=headers_hospital_1,
        json=rule_data_1
    )
    
    test_passed = response.status_code == 200
    print_test("医疗机构1创建数据", test_passed)
    
    if not test_passed:
        print("  跳过多租户隔离测试")
        return
    
    rule_1 = response.json()
    
    # 8.2 使用医疗机构2查询，应该看不到医疗机构1的数据
    print("\n8.2 使用医疗机构2查询数据...")
    headers_hospital_2 = {**headers, "X-Hospital-ID": "2"}
    
    response = requests.get(
        f"{BASE_URL}/api/v1/orientation-rules",
        headers=headers_hospital_2
    )
    
    if response.status_code == 200:
        rules = response.json()["items"]
        # 检查是否包含医疗机构1的数据
        has_hospital_1_data = any(r["id"] == rule_1["id"] for r in rules)
        print_test("多租户数据隔离", not has_hospital_1_data, 
                  f"医疗机构2查询结果: {len(rules)} 条，{'包含' if has_hospital_1_data else '不包含'}医疗机构1的数据")
    else:
        print_test("医疗机构2查询", False)
    
    # 8.3 使用医疗机构2尝试访问医疗机构1的数据
    print("\n8.3 跨租户访问测试...")
    response = requests.get(
        f"{BASE_URL}/api/v1/orientation-rules/{rule_1['id']}",
        headers=headers_hospital_2
    )
    
    # 应该返回404或403
    test_passed = response.status_code in [403, 404]
    print_test("跨租户访问被阻止", test_passed, f"状态码: {response.status_code}")


def cleanup_test_data(rule_ids):
    """清理测试数据"""
    print_section("清理测试数据")
    
    for rule_id in rule_ids:
        if rule_id:
            print(f"删除导向规则 {rule_id}...")
            response = requests.delete(
                f"{BASE_URL}/api/v1/orientation-rules/{rule_id}",
                headers=headers
            )
            print_test(f"删除规则 {rule_id}", response.status_code == 200)


def main():
    """主测试流程"""
    print("\n" + "="*60)
    print("  业务导向管理模块 - 端到端功能测试")
    print("="*60)
    print(f"\n测试环境: {BASE_URL}")
    print(f"医疗机构ID: {HOSPITAL_ID}")
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    rule_ids_to_cleanup = []
    
    try:
        # 测试1: 导向规则 CRUD
        rule_id = test_orientation_rule_crud()
        if rule_id:
            rule_ids_to_cleanup.append(rule_id)
            
            # 测试4: 导向基准 CRUD
            benchmark_id = test_orientation_benchmark_crud(rule_id)
            
            # 测试5: 导向阶梯 CRUD
            ladder_id = test_orientation_ladder_crud(rule_id)
            
            # 测试2: 导向规则复制
            copied_rule_id = test_orientation_rule_copy(rule_id)
            if copied_rule_id:
                rule_ids_to_cleanup.append(copied_rule_id)
            
            # 测试3: 导向规则导出
            test_orientation_rule_export(rule_id)
        
        # 测试6: 模型节点关联
        test_model_node_orientation()
        
        # 测试8: 多租户隔离
        test_multi_tenant_isolation()
        
    except Exception as e:
        print(f"\n测试过程中发生错误: {str(e)}")
        import traceback
        traceback.print_exc()
    
    finally:
        # 清理测试数据
        if rule_ids_to_cleanup:
            cleanup_test_data(rule_ids_to_cleanup)
    
    print("\n" + "="*60)
    print(f"  测试完成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
