"""
测试AI API连接

使用方法：
    python test_ai_api.py
"""
import json

# 从配置文件读取
with open('report_data_config_real.json', 'r', encoding='utf-8') as f:
    config = json.load(f)

ai_config = config['ai_config']

print("="*70)
print("测试AI API连接")
print("="*70)
print(f"API端点: {ai_config['base_url']}")
print(f"模型: {ai_config['model']}")
print(f"API密钥: {ai_config['api_key'][:10]}...")
print()

try:
    import openai
    
    client = openai.OpenAI(
        api_key=ai_config['api_key'],
        base_url=ai_config['base_url'],
        timeout=ai_config.get('timeout', 60)
    )
    
    print("发送测试请求...")
    response = client.chat.completions.create(
        model=ai_config['model'],
        messages=[
            {"role": "system", "content": "你是一个助手"},
            {"role": "user", "content": "请用JSON格式返回：{\"test\": \"success\"}"}
        ],
        temperature=0.7,
        max_tokens=100
    )
    
    print(f"\n响应类型: {type(response)}")
    print(f"响应内容: {response}")
    
    if hasattr(response, 'choices'):
        print(f"\n✓ API调用成功!")
        print(f"返回内容: {response.choices[0].message.content}")
    else:
        print(f"\n⚠️  响应格式不标准")
        print(f"响应: {response}")

except Exception as e:
    print(f"\n❌ API调用失败: {str(e)}")
    import traceback
    traceback.print_exc()
