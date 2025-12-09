"""测试核算单元分组功能"""
import requests
import json

BASE_URL = "http://localhost:8000"
TASK_ID = "ae546d7b-5de8-40ec-b4a7-9e80502bd3ed"

# 设置请求头
headers = {
    "X-Hospital-ID": "1",
    "Authorization": "Bearer your_token_here"  # 需要替换为实际的token
}

# 测试汇总API
print("测试核算单元分组汇总...")
print("=" * 80)

try:
    response = requests.get(
        f"{BASE_URL}/api/v1/calculation/results/summary",
        params={"task_id": TASK_ID},
        headers=headers
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"任务ID: {data['task_id']}")
        print(f"\n全院汇总:")
        summary = data['summary']
        print(f"  科室名称: {summary['department_name']}")
        print(f"  总价值: {summary['total_value']}")
        
        print(f"\n核算单元列表 (共 {len(data['departments'])} 个):")
        print("-" * 80)
        
        # 统计核算单元代码出现次数
        unit_codes = {}
        for dept in data['departments']:
            code = dept['department_code']
            name = dept['department_name']
            if code not in unit_codes:
                unit_codes[code] = []
            unit_codes[code].append(name)
        
        # 显示所有核算单元
        for dept in data['departments']:
            print(f"  代码: {dept['department_code']:<10} "
                  f"名称: {dept['department_name']:<20} "
                  f"总价值: {dept['total_value']:>12.2f}")
        
        # 检查是否有重复
        print("\n" + "=" * 80)
        print("重复检查:")
        has_duplicates = False
        for code, names in unit_codes.items():
            if len(names) > 1:
                has_duplicates = True
                print(f"  ❌ 核算单元 {code} 出现 {len(names)} 次: {', '.join(names)}")
        
        if not has_duplicates:
            print("  ✅ 没有发现重复的核算单元")
        
    else:
        print(f"❌ 请求失败: {response.status_code}")
        print(f"错误信息: {response.text}")
        
except Exception as e:
    print(f"❌ 发生错误: {e}")
    print("\n提示: 请确保后端服务正在运行，并且已经登录获取了有效的token")
