"""
测试导向规则PDF导出功能
"""
import requests
import sys
import os

# 配置
BASE_URL = "http://localhost:8000/api/v1"
USERNAME = "admin"
PASSWORD = "admin123"

# 全局变量
token = None
headers = {}


def login():
    """登录获取token"""
    global token, headers
    print("\n1. 登录获取token...")
    response = requests.post(
        f"{BASE_URL}/auth/login",
        data={"username": USERNAME, "password": PASSWORD}
    )
    if response.status_code == 200:
        token = response.json()["access_token"]
        headers = {
            "Authorization": f"Bearer {token}",
            "X-Hospital-ID": "1"
        }
        print(f"✓ 登录成功，token: {token[:20]}...")
        return True
    else:
        print(f"✗ 登录失败: {response.text}")
        return False


def test_export_markdown():
    """测试导出Markdown"""
    print("\n2. 测试导出Markdown...")
    
    # 创建测试导向规则
    rule_data = {
        "name": "PDF导出测试规则",
        "category": "benchmark_ladder",
        "description": "用于测试PDF导出功能的规则"
    }
    
    response = requests.post(
        f"{BASE_URL}/orientation-rules",
        json=rule_data,
        headers=headers
    )
    
    if response.status_code != 200:
        print(f"✗ 创建规则失败: {response.text}")
        return None
    
    rule_id = response.json()["id"]
    print(f"✓ 创建规则成功，ID: {rule_id}")
    
    # 导出Markdown
    response = requests.get(
        f"{BASE_URL}/orientation-rules/{rule_id}/export",
        params={"format": "markdown"},
        headers=headers
    )
    
    if response.status_code == 200:
        # 保存文件
        filename = f"test_export_{rule_id}.md"
        with open(filename, 'wb') as f:
            f.write(response.content)
        print(f"✓ 导出Markdown成功，文件: {filename}")
        print(f"  文件大小: {len(response.content)} 字节")
        
        # 验证内容类型
        content_type = response.headers.get("content-type", "")
        if "text/markdown" in content_type:
            print(f"✓ Content-Type正确: {content_type}")
        else:
            print(f"✗ Content-Type错误: {content_type}")
        
        return rule_id
    else:
        print(f"✗ 导出Markdown失败: {response.text}")
        return None


def test_export_pdf(rule_id):
    """测试导出PDF"""
    print("\n3. 测试导出PDF...")
    
    response = requests.get(
        f"{BASE_URL}/orientation-rules/{rule_id}/export",
        params={"format": "pdf"},
        headers=headers
    )
    
    if response.status_code == 200:
        # 保存文件
        filename = f"test_export_{rule_id}.pdf"
        with open(filename, 'wb') as f:
            f.write(response.content)
        print(f"✓ 导出PDF成功，文件: {filename}")
        print(f"  文件大小: {len(response.content)} 字节")
        
        # 验证内容类型
        content_type = response.headers.get("content-type", "")
        if "application/pdf" in content_type:
            print(f"✓ Content-Type正确: {content_type}")
        else:
            print(f"✗ Content-Type错误: {content_type}")
        
        # 验证PDF文件头
        if response.content[:4] == b'%PDF':
            print(f"✓ PDF文件格式正确")
        else:
            print(f"✗ PDF文件格式错误")
        
        return True
    else:
        print(f"✗ 导出PDF失败: {response.text}")
        return False


def cleanup(rule_id):
    """清理测试数据"""
    print("\n4. 清理测试数据...")
    
    response = requests.delete(
        f"{BASE_URL}/orientation-rules/{rule_id}",
        headers=headers
    )
    
    if response.status_code == 200:
        print(f"✓ 删除规则成功")
    else:
        print(f"✗ 删除规则失败: {response.text}")
    
    # 删除测试文件
    for ext in ['md', 'pdf']:
        filename = f"test_export_{rule_id}.{ext}"
        if os.path.exists(filename):
            os.remove(filename)
            print(f"✓ 删除文件: {filename}")


def main():
    print("=" * 60)
    print("测试导向规则PDF导出功能")
    print("=" * 60)
    
    # 登录
    if not login():
        sys.exit(1)
    
    # 测试导出Markdown
    rule_id = test_export_markdown()
    if not rule_id:
        sys.exit(1)
    
    # 测试导出PDF
    if not test_export_pdf(rule_id):
        cleanup(rule_id)
        sys.exit(1)
    
    # 清理
    cleanup(rule_id)
    
    print("\n" + "=" * 60)
    print("所有测试通过！")
    print("=" * 60)


if __name__ == "__main__":
    main()
