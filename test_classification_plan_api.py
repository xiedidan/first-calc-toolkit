"""
测试分类预案API端点
"""
import sys
import os

# 添加backend目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

import requests
import json

# API基础URL
BASE_URL = "http://localhost:8000/api/v1"

# 测试用的医疗机构ID
HOSPITAL_ID = 1


def test_classification_plan_api():
    """测试分类预案API"""
    
    print("=" * 80)
    print("测试分类预案API端点")
    print("=" * 80)
    
    # 设置请求头
    headers = {
        "Content-Type": "application/json",
        "X-Hospital-ID": str(HOSPITAL_ID)
    }
    
    try:
        # 1. 测试获取预案列表
        print("\n1. 测试获取预案列表...")
        response = requests.get(
            f"{BASE_URL}/classification-plans",
            headers=headers,
            params={"skip": 0, "limit": 10}
        )
        print(f"   状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✓ 查询到 {data['total']} 个预案")
            if data['items']:
                print(f"   ✓ 第一个预案: {data['items'][0]['plan_name']}")
        else:
            print(f"   响应: {response.text}")
        
        # 2. 测试获取预案详情（假设存在ID为1的预案）
        print("\n2. 测试获取预案详情...")
        response = requests.get(
            f"{BASE_URL}/classification-plans/1",
            headers=headers
        )
        print(f"   状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✓ 预案名称: {data.get('plan_name', 'N/A')}")
            print(f"   ✓ 状态: {data.get('status', 'N/A')}")
            print(f"   ✓ 总项目数: {data.get('total_items', 0)}")
        elif response.status_code == 404:
            print(f"   预案不存在（这是正常的，如果数据库中没有预案）")
        else:
            print(f"   响应: {response.text}")
        
        # 3. 测试获取预案项目列表
        print("\n3. 测试获取预案项目列表...")
        response = requests.get(
            f"{BASE_URL}/classification-plans/1/items",
            headers=headers,
            params={"page": 1, "size": 10}
        )
        print(f"   状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✓ 查询到 {data['total']} 个项目")
        elif response.status_code == 404:
            print(f"   预案不存在（这是正常的）")
        else:
            print(f"   响应: {response.text}")
        
        # 4. 测试生成提交预览
        print("\n4. 测试生成提交预览...")
        response = requests.post(
            f"{BASE_URL}/classification-plans/1/preview",
            headers=headers
        )
        print(f"   状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✓ 新增项目数: {data.get('new_count', 0)}")
            print(f"   ✓ 覆盖项目数: {data.get('overwrite_count', 0)}")
        elif response.status_code == 404:
            print(f"   预案不存在（这是正常的）")
        else:
            print(f"   响应: {response.text}")
        
        # 5. 测试API路由是否正确注册
        print("\n5. 测试API路由注册...")
        response = requests.get(f"{BASE_URL}/docs")
        print(f"   状态码: {response.status_code}")
        if response.status_code == 200:
            print(f"   ✓ API文档可访问")
            print(f"   ✓ 可以在浏览器中访问 {BASE_URL}/docs 查看完整API文档")
        
        print("\n" + "=" * 80)
        print("✓ API端点测试完成！")
        print("=" * 80)
        print("\n注意：")
        print("- 如果看到404错误，这是正常的，因为数据库中可能还没有预案数据")
        print("- 如果看到500错误，请检查后端服务是否正常运行")
        print("- 如果看到连接错误，请确保后端服务已启动在 http://localhost:8000")
        
    except requests.exceptions.ConnectionError:
        print("\n✗ 无法连接到后端服务")
        print("   请确保后端服务已启动：")
        print("   cd backend && python -m uvicorn app.main:app --reload")
    except Exception as e:
        print(f"\n✗ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_classification_plan_api()
