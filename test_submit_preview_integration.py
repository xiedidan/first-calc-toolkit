"""
集成测试：提交预览和批量提交功能
使用实际数据库进行测试
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

import requests
from datetime import datetime

# API基础URL
BASE_URL = "http://localhost:8000"

# 测试医疗机构ID
HOSPITAL_ID = 1


def test_submit_preview_and_submit():
    """测试提交预览和批量提交的完整流程"""
    print("\n" + "=" * 60)
    print("测试提交预览和批量提交功能")
    print("=" * 60)
    
    # 设置请求头
    headers = {
        "X-Hospital-ID": str(HOSPITAL_ID),
        "Content-Type": "application/json"
    }
    
    # 1. 查询现有的预案列表
    print("\n1. 查询预案列表...")
    response = requests.get(
        f"{BASE_URL}/api/v1/classification-plans",
        headers=headers,
        params={"status": "draft"}
    )
    
    if response.status_code != 200:
        print(f"✗ 查询预案列表失败: {response.status_code}")
        print(f"  响应: {response.text}")
        return False
    
    plans_data = response.json()
    print(f"  找到 {plans_data['total']} 个草稿预案")
    
    if plans_data['total'] == 0:
        print("  ⚠ 没有草稿预案可供测试")
        print("  请先创建一个分类任务并等待完成，然后再运行此测试")
        return False
    
    # 使用第一个草稿预案进行测试
    plan = plans_data['items'][0]
    plan_id = plan['id']
    print(f"  使用预案: {plan['plan_name']} (ID: {plan_id})")
    print(f"  任务名称: {plan['task_name']}")
    print(f"  总项目数: {plan['total_items']}")
    print(f"  已调整项目: {plan['adjusted_items']}")
    
    # 2. 生成提交预览
    print(f"\n2. 生成提交预览...")
    response = requests.post(
        f"{BASE_URL}/api/v1/classification-plans/{plan_id}/preview",
        headers=headers
    )
    
    if response.status_code != 200:
        print(f"✗ 生成预览失败: {response.status_code}")
        print(f"  响应: {response.text}")
        return False
    
    preview = response.json()
    print(f"  ✓ 预览生成成功")
    print(f"  预案名称: {preview['plan_name']}")
    print(f"  总项目数: {preview['total_items']}")
    print(f"  新增数量: {preview['new_count']}")
    print(f"  覆盖数量: {preview['overwrite_count']}")
    
    # 显示新增项目
    if preview['new_items']:
        print(f"\n  新增项目 ({len(preview['new_items'])} 个):")
        for i, item in enumerate(preview['new_items'][:5], 1):  # 只显示前5个
            print(f"    {i}. {item['item_name']}")
            print(f"       -> {item['dimension_name']}")
            print(f"       路径: {item['dimension_path']}")
        if len(preview['new_items']) > 5:
            print(f"    ... 还有 {len(preview['new_items']) - 5} 个项目")
    
    # 显示覆盖项目
    if preview['overwrite_items']:
        print(f"\n  覆盖项目 ({len(preview['overwrite_items'])} 个):")
        for i, item in enumerate(preview['overwrite_items'][:5], 1):  # 只显示前5个
            print(f"    {i}. {item['item_name']}")
            print(f"       原维度: {item['old_dimension_name']}")
            print(f"       新维度: {item['dimension_name']}")
        if len(preview['overwrite_items']) > 5:
            print(f"    ... 还有 {len(preview['overwrite_items']) - 5} 个项目")
    
    # 显示警告
    if preview.get('warnings'):
        print(f"\n  ⚠ 警告:")
        for warning in preview['warnings']:
            print(f"    - {warning}")
    
    # 3. 确认是否继续提交
    print(f"\n3. 准备提交预案...")
    print(f"  将新增 {preview['new_count']} 个映射")
    print(f"  将覆盖 {preview['overwrite_count']} 个映射")
    
    # 询问用户是否继续
    user_input = input("\n  是否继续提交？(y/n): ").strip().lower()
    if user_input != 'y':
        print("  用户取消提交")
        return True
    
    # 4. 提交预案
    print(f"\n4. 提交预案...")
    response = requests.post(
        f"{BASE_URL}/api/v1/classification-plans/{plan_id}/submit",
        headers=headers,
        json={}
    )
    
    if response.status_code != 200:
        print(f"✗ 提交失败: {response.status_code}")
        print(f"  响应: {response.text}")
        return False
    
    result = response.json()
    print(f"  ✓ 提交成功")
    print(f"  成功: {result['success']}")
    print(f"  消息: {result['message']}")
    print(f"  新增数量: {result['new_count']}")
    print(f"  覆盖数量: {result['overwrite_count']}")
    print(f"  提交时间: {result['submitted_at']}")
    
    # 5. 验证预案状态已更新
    print(f"\n5. 验证预案状态...")
    response = requests.get(
        f"{BASE_URL}/api/v1/classification-plans/{plan_id}",
        headers=headers
    )
    
    if response.status_code != 200:
        print(f"✗ 查询预案失败: {response.status_code}")
        return False
    
    updated_plan = response.json()
    print(f"  预案状态: {updated_plan['status']}")
    print(f"  提交时间: {updated_plan['submitted_at']}")
    
    if updated_plan['status'] != 'submitted':
        print(f"  ✗ 预案状态未更新为submitted")
        return False
    
    print(f"  ✓ 预案状态已正确更新")
    
    # 6. 尝试重复提交（应该失败）
    print(f"\n6. 测试防止重复提交...")
    response = requests.post(
        f"{BASE_URL}/api/v1/classification-plans/{plan_id}/submit",
        headers=headers,
        json={}
    )
    
    if response.status_code == 400:
        print(f"  ✓ 重复提交被正确阻止")
        print(f"  错误消息: {response.json()['detail']}")
    else:
        print(f"  ✗ 重复提交未被阻止 (状态码: {response.status_code})")
        return False
    
    print("\n" + "=" * 60)
    print("✓ 所有测试通过！")
    print("=" * 60)
    return True


def test_preview_only():
    """仅测试预览功能（不提交）"""
    print("\n" + "=" * 60)
    print("测试提交预览功能（仅预览）")
    print("=" * 60)
    
    # 设置请求头
    headers = {
        "X-Hospital-ID": str(HOSPITAL_ID),
        "Content-Type": "application/json"
    }
    
    # 查询草稿预案
    print("\n1. 查询草稿预案...")
    response = requests.get(
        f"{BASE_URL}/api/v1/classification-plans",
        headers=headers,
        params={"status": "draft"}
    )
    
    if response.status_code != 200:
        print(f"✗ 查询失败: {response.status_code}")
        return False
    
    plans_data = response.json()
    print(f"  找到 {plans_data['total']} 个草稿预案")
    
    if plans_data['total'] == 0:
        print("  ⚠ 没有草稿预案可供测试")
        return False
    
    # 对每个草稿预案生成预览
    for plan in plans_data['items']:
        plan_id = plan['id']
        print(f"\n2. 预览预案: {plan['plan_name']} (ID: {plan_id})")
        
        response = requests.post(
            f"{BASE_URL}/api/v1/classification-plans/{plan_id}/preview",
            headers=headers
        )
        
        if response.status_code != 200:
            print(f"  ✗ 预览失败: {response.status_code}")
            continue
        
        preview = response.json()
        print(f"  总项目: {preview['total_items']}")
        print(f"  新增: {preview['new_count']}")
        print(f"  覆盖: {preview['overwrite_count']}")
        
        if preview.get('warnings'):
            print(f"  警告: {len(preview['warnings'])} 个")
    
    print("\n" + "=" * 60)
    print("✓ 预览测试完成")
    print("=" * 60)
    return True


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="测试提交预览和批量提交功能")
    parser.add_argument(
        "--preview-only",
        action="store_true",
        help="仅测试预览功能，不执行提交"
    )
    parser.add_argument(
        "--hospital-id",
        type=int,
        default=1,
        help="医疗机构ID（默认: 1）"
    )
    
    args = parser.parse_args()
    HOSPITAL_ID = args.hospital_id
    
    try:
        if args.preview_only:
            success = test_preview_only()
        else:
            success = test_submit_preview_and_submit()
        
        if not success:
            sys.exit(1)
    except requests.exceptions.ConnectionError:
        print("\n✗ 无法连接到API服务器")
        print("  请确保后端服务正在运行: http://localhost:8000")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
