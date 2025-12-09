"""测试修改后的 AI 接口"""
import sys
sys.path.insert(0, 'backend')

from app.utils.ai_interface import call_ai_classification, call_ai_text_generation

api_endpoint = "https://newapi.netlib.re/v1"
api_key = "sk-sPiUwYg21beir7MqKALd5vO0vvHYFbQxdMuoDEdiGip4SfjW"
model_name = "deepseek-r1-0528"

print("=" * 50)
print("测试1: 调用 call_ai_classification")
print("=" * 50)

try:
    result = call_ai_classification(
        api_endpoint=api_endpoint,
        api_key=api_key,
        prompt_template="请为以下医技项目分类：\n\n待分类项目列表：\n{items}\n\n可选维度列表：\n{dimensions}\n\n请返回JSON格式的分类结果。",
        item_name="CT检查",
        dimensions=[
            {"id": 1, "name": "检查费", "path": "医技/检查费"},
            {"id": 2, "name": "放射费", "path": "医技/放射费"},
            {"id": 3, "name": "化验费", "path": "医技/化验费"},
        ],
        model_name=model_name,
        max_retries=1,
        timeout=60
    )
    print(f"成功!")
    print(f"结果: {result}")
except Exception as e:
    print(f"失败: {e}")

print()
print("=" * 50)
print("测试2: 调用 call_ai_text_generation")
print("=" * 50)

try:
    content = call_ai_text_generation(
        api_endpoint=api_endpoint,
        api_key=api_key,
        system_prompt="你是一个助手，请简洁回答问题。",
        user_prompt="请用一句话介绍什么是CT检查。",
        model_name=model_name,
        max_retries=1,
        timeout=60
    )
    print(f"成功!")
    print(f"内容: {content[:200]}")
except Exception as e:
    print(f"失败: {e}")
