"""
导入配置
"""

# 收费项目导入配置
CHARGE_ITEM_IMPORT_CONFIG = {
    "fields": {
        "item_code": {
            "label": "项目编码",
            "required": True,
            "unique": True,
            "type": "string",
            "max_length": 100
        },
        "item_name": {
            "label": "项目名称",
            "required": True,
            "type": "string",
            "max_length": 255
        },
        "item_category": {
            "label": "项目分类",
            "required": False,
            "type": "string",
            "max_length": 100
        },
        "unit_price": {
            "label": "单价",
            "required": False,
            "type": "string",
            "max_length": 50
        }
    },
    "default_mapping": {
        # 中文列名
        "项目编码": "item_code",
        "编码": "item_code",
        "收费项目编码": "item_code",
        "项目名称": "item_name",
        "名称": "item_name",
        "收费项目名称": "item_name",
        "项目分类": "item_category",
        "分类": "item_category",
        "类别": "item_category",
        "单价": "unit_price",
        "价格": "unit_price",
        # 英文列名
        "code": "item_code",
        "item_code": "item_code",
        "name": "item_name",
        "item_name": "item_name",
        "category": "item_category",
        "item_category": "item_category",
        "price": "unit_price",
        "unit_price": "unit_price"
    }
}

# 维度目录导入配置
DIMENSION_ITEM_IMPORT_CONFIG = {
    "fields": {
        "item_code": {
            "label": "收费项目编码",
            "required": True,
            "type": "string",
            "max_length": 100
        }
    },
    "default_mapping": {
        "项目编码": "item_code",
        "编码": "item_code",
        "收费项目编码": "item_code",
        "code": "item_code",
        "item_code": "item_code"
    }
}
