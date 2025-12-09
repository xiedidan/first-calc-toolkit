"""调试请求体数据"""
import json

# 用户提供的请求体
request_body = {
    "session_id": "16bfb418-a9e8-4090-80c8-bdd657803a3f",
    "value_mapping": [
        {
            "value": "护理-病区护理-术中护理",
            "source": "dimension_plan",
            "dimension_codes": ["dim-nur-ward-op"]
        },
        {
            "value": "护理-病区护理-拓展护理",
            "source": "dimension_plan",
            "dimension_codes": ["dim-nur-ward-extra"]
        },
        {
            "value": "护理-病区护理-医护协同护理2",
            "source": "dimension_plan",
            "dimension_codes": ["dim-nur-ward-collab"]
        },
        {
            "value": "护理-病区护理-独立护理",
            "source": "dimension_plan",
            "dimension_codes": ["dim-nur-ward-ind"]
        },
        {
            "value": "护理-病区护理-医护协同护理1",
            "source": "dimension_plan",
            "dimension_codes": ["dim-nur-ward-collab"]
        },
        {
            "value": "护理-病区护理-监测护理",
            "source": "dimension_plan",
            "dimension_codes": ["dim-nur-proc-collab"]
        },
        {
            "value": "护理-病区护理-气道护理",
            "source": "dimension_plan",
            "dimension_codes": ["dim-nur-proc-collab"]
        },
        {
            "value": "护理-病区护理-其他护理",
            "source": "dimension_plan",
            "dimension_codes": ["dim-nur-ward-other"]
        }
    ]
}

print("检查请求体数据...")
print(f"session_id: '{request_body['session_id']}'")
print(f"value_mapping 数量: {len(request_body['value_mapping'])}")

for i, mapping in enumerate(request_body['value_mapping']):
    print(f"\n映射 {i+1}:")
    print(f"  value: '{mapping['value']}' (长度: {len(mapping['value'])})")
    print(f"  source: '{mapping['source']}' (长度: {len(mapping['source'])})")
    print(f"  dimension_codes: {mapping['dimension_codes']}")
    
    # 检查是否有空字符串
    if not mapping['value']:
        print("  ⚠️ value 是空字符串!")
    if not mapping['source']:
        print("  ⚠️ source 是空字符串!")
    if any(not code for code in mapping['dimension_codes']):
        print("  ⚠️ dimension_codes 包含空字符串!")

print("\n✅ 所有数据检查完成")
