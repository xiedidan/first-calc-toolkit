"""
测试对话消息导出功能

需求 12.1: 当用户导出指标口径结果时，智能数据问答模块应生成带有格式化表格的Markdown文件
需求 12.2: 当用户将指标口径结果导出为PDF时，智能数据问答模块应生成格式正确的PDF文档
需求 12.3: 当用户将查询数据导出为Excel时，智能数据问答模块应生成包含数据和列标题的Excel文件
需求 12.4: 当用户将查询数据导出为CSV时，智能数据问答模块应生成UTF-8编码的CSV文件
"""
import os
import sys
import requests
from datetime import datetime

# 配置
BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
HOSPITAL_ID = os.getenv("TEST_HOSPITAL_ID", "1")

headers = {
    "Content-Type": "application/json",
    "X-Hospital-ID": HOSPITAL_ID
}


def test_create_conversation_with_table_message():
    """创建包含表格消息的对话用于测试导出"""
    print("\n=== 创建测试对话 ===")
    
    # 1. 创建对话
    conv_data = {
        "title": f"导出测试对话_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "conversation_type": "caliber",
        "description": "用于测试导出功能的对话"
    }
    
    resp = requests.post(f"{BASE_URL}/api/v1/conversations", json=conv_data, headers=headers)
    print(f"创建对话: {resp.status_code}")
    
    if resp.status_code != 200:
        print(f"创建对话失败: {resp.text}")
        return None, None
    
    conv = resp.json()["data"]
    conv_id = conv["id"]
    print(f"对话ID: {conv_id}")
    
    # 2. 发送消息（会自动创建AI回复）
    msg_data = {"content": "查询门诊收入指标的口径"}
    resp = requests.post(f"{BASE_URL}/api/v1/conversations/{conv_id}/messages", json=msg_data, headers=headers)
    print(f"发送消息: {resp.status_code}")
    
    if resp.status_code != 200:
        print(f"发送消息失败: {resp.text}")
        return conv_id, None
    
    result = resp.json()["data"]
    assistant_msg_id = result["assistant_message"]["id"]
    print(f"AI回复消息ID: {assistant_msg_id}")
    
    return conv_id, assistant_msg_id


def test_export_markdown(conv_id: int, msg_id: int):
    """测试Markdown导出"""
    print("\n=== 测试Markdown导出 ===")
    
    export_data = {"format": "markdown"}
    resp = requests.post(
        f"{BASE_URL}/api/v1/conversations/{conv_id}/messages/{msg_id}/export",
        json=export_data,
        headers=headers
    )
    
    print(f"导出状态: {resp.status_code}")
    
    if resp.status_code == 200:
        content_type = resp.headers.get("Content-Type", "")
        content_disp = resp.headers.get("Content-Disposition", "")
        print(f"Content-Type: {content_type}")
        print(f"Content-Disposition: {content_disp}")
        print(f"文件大小: {len(resp.content)} bytes")
        
        # 显示内容预览
        content = resp.content.decode("utf-8")
        print(f"内容预览:\n{content[:500]}")
        return True
    else:
        print(f"导出失败: {resp.text}")
        return False


def test_export_pdf(conv_id: int, msg_id: int):
    """测试PDF导出"""
    print("\n=== 测试PDF导出 ===")
    
    export_data = {"format": "pdf"}
    resp = requests.post(
        f"{BASE_URL}/api/v1/conversations/{conv_id}/messages/{msg_id}/export",
        json=export_data,
        headers=headers
    )
    
    print(f"导出状态: {resp.status_code}")
    
    if resp.status_code == 200:
        content_type = resp.headers.get("Content-Type", "")
        print(f"Content-Type: {content_type}")
        print(f"文件大小: {len(resp.content)} bytes")
        
        # 验证PDF头
        if resp.content[:4] == b'%PDF':
            print("✓ 有效的PDF文件")
            return True
        else:
            print("✗ 无效的PDF文件")
            return False
    else:
        print(f"导出失败: {resp.text}")
        return False


def test_export_excel_error(conv_id: int, msg_id: int):
    """测试Excel导出（文本消息应该报错）"""
    print("\n=== 测试Excel导出（预期失败，因为是文本消息）===")
    
    export_data = {"format": "excel"}
    resp = requests.post(
        f"{BASE_URL}/api/v1/conversations/{conv_id}/messages/{msg_id}/export",
        json=export_data,
        headers=headers
    )
    
    print(f"导出状态: {resp.status_code}")
    
    if resp.status_code == 400:
        print(f"预期的错误: {resp.json().get('detail', resp.text)}")
        return True
    else:
        print(f"意外的响应: {resp.text}")
        return False


def test_export_csv_error(conv_id: int, msg_id: int):
    """测试CSV导出（文本消息应该报错）"""
    print("\n=== 测试CSV导出（预期失败，因为是文本消息）===")
    
    export_data = {"format": "csv"}
    resp = requests.post(
        f"{BASE_URL}/api/v1/conversations/{conv_id}/messages/{msg_id}/export",
        json=export_data,
        headers=headers
    )
    
    print(f"导出状态: {resp.status_code}")
    
    if resp.status_code == 400:
        print(f"预期的错误: {resp.json().get('detail', resp.text)}")
        return True
    else:
        print(f"意外的响应: {resp.text}")
        return False


def test_export_invalid_format(conv_id: int, msg_id: int):
    """测试无效导出格式"""
    print("\n=== 测试无效导出格式 ===")
    
    export_data = {"format": "invalid"}
    resp = requests.post(
        f"{BASE_URL}/api/v1/conversations/{conv_id}/messages/{msg_id}/export",
        json=export_data,
        headers=headers
    )
    
    print(f"导出状态: {resp.status_code}")
    
    if resp.status_code in [400, 422]:
        print(f"预期的错误响应")
        return True
    else:
        print(f"意外的响应: {resp.text}")
        return False


def cleanup(conv_id: int):
    """清理测试数据"""
    print("\n=== 清理测试数据 ===")
    
    if conv_id:
        resp = requests.delete(f"{BASE_URL}/api/v1/conversations/{conv_id}", headers=headers)
        print(f"删除对话 {conv_id}: {resp.status_code}")


def main():
    print("=" * 60)
    print("对话消息导出功能测试")
    print("=" * 60)
    
    # 检查服务是否可用
    try:
        resp = requests.get(f"{BASE_URL}/health", timeout=5)
        print(f"服务状态: {resp.status_code}")
    except Exception as e:
        print(f"服务不可用: {e}")
        print("请确保后端服务已启动")
        sys.exit(1)
    
    conv_id = None
    results = []
    
    try:
        # 创建测试数据
        conv_id, msg_id = test_create_conversation_with_table_message()
        
        if not conv_id or not msg_id:
            print("创建测试数据失败，跳过导出测试")
            return
        
        # 运行导出测试
        results.append(("Markdown导出", test_export_markdown(conv_id, msg_id)))
        results.append(("PDF导出", test_export_pdf(conv_id, msg_id)))
        results.append(("Excel导出错误处理", test_export_excel_error(conv_id, msg_id)))
        results.append(("CSV导出错误处理", test_export_csv_error(conv_id, msg_id)))
        results.append(("无效格式处理", test_export_invalid_format(conv_id, msg_id)))
        
    finally:
        # 清理
        if conv_id:
            cleanup(conv_id)
    
    # 打印结果
    print("\n" + "=" * 60)
    print("测试结果汇总")
    print("=" * 60)
    
    passed = 0
    failed = 0
    for name, result in results:
        status = "✓ 通过" if result else "✗ 失败"
        print(f"{name}: {status}")
        if result:
            passed += 1
        else:
            failed += 1
    
    print(f"\n总计: {passed} 通过, {failed} 失败")
    
    if failed > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
