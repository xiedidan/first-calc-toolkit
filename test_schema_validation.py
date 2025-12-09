"""测试Schema验证"""
from pydantic import BaseModel, Field

class ValueMapping(BaseModel):
    """值映射Schema"""
    value: str
    source: str
    dimension_codes: list[str]

# 测试数据
test_data = {
    "value": "护理-病区护理-术中护理",
    "source": "dimension_plan",
    "dimension_codes": ["dim-nur-ward-op"]
}

try:
    mapping = ValueMapping(**test_data)
    print(f"验证成功: {mapping}")
except Exception as e:
    print(f"验证失败: {e}")

# 测试空字符串
test_data2 = {
    "value": "test",
    "source": "",
    "dimension_codes": ["dim1"]
}

try:
    mapping2 = ValueMapping(**test_data2)
    print(f"空source验证成功: {mapping2}")
except Exception as e:
    print(f"空source验证失败: {e}")

# 测试空列表
test_data3 = {
    "value": "test",
    "source": "dimension_plan",
    "dimension_codes": [""]
}

try:
    mapping3 = ValueMapping(**test_data3)
    print(f"空dimension_codes验证成功: {mapping3}")
except Exception as e:
    print(f"空dimension_codes验证失败: {e}")
