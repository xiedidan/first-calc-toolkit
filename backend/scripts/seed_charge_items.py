"""
添加收费项目测试数据
"""
import sys
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.append(str(Path(__file__).parent.parent))

from app.database import SessionLocal
from app.models.charge_item import ChargeItem


def seed_charge_items():
    """添加收费项目测试数据"""
    db = SessionLocal()
    
    try:
        # 检查是否已有数据
        count = db.query(ChargeItem).count()
        if count > 0:
            print(f"数据库中已有 {count} 条收费项目数据，跳过初始化")
            return
        
        # 测试数据
        test_items = [
            # 检查类
            {"item_code": "CK001", "item_name": "血常规", "item_category": "检验", "unit_price": "25.00"},
            {"item_code": "CK002", "item_name": "尿常规", "item_category": "检验", "unit_price": "15.00"},
            {"item_code": "CK003", "item_name": "肝功能", "item_category": "检验", "unit_price": "80.00"},
            {"item_code": "CK004", "item_name": "肾功能", "item_category": "检验", "unit_price": "60.00"},
            {"item_code": "CK005", "item_name": "心电图", "item_category": "检查", "unit_price": "30.00"},
            {"item_code": "CK006", "item_name": "胸部X光", "item_category": "检查", "unit_price": "80.00"},
            {"item_code": "CK007", "item_name": "腹部B超", "item_category": "检查", "unit_price": "120.00"},
            {"item_code": "CK008", "item_name": "CT扫描", "item_category": "检查", "unit_price": "350.00"},
            
            # 治疗类
            {"item_code": "ZL001", "item_name": "静脉输液", "item_category": "治疗", "unit_price": "10.00"},
            {"item_code": "ZL002", "item_name": "肌肉注射", "item_category": "治疗", "unit_price": "5.00"},
            {"item_code": "ZL003", "item_name": "换药", "item_category": "治疗", "unit_price": "15.00"},
            {"item_code": "ZL004", "item_name": "雾化吸入", "item_category": "治疗", "unit_price": "20.00"},
            
            # 手术类
            {"item_code": "SS001", "item_name": "阑尾切除术", "item_category": "手术", "unit_price": "2500.00"},
            {"item_code": "SS002", "item_name": "胆囊切除术", "item_category": "手术", "unit_price": "3500.00"},
            {"item_code": "SS003", "item_name": "剖腹产", "item_category": "手术", "unit_price": "4000.00"},
            
            # 药品类
            {"item_code": "YP001", "item_name": "阿莫西林胶囊", "item_category": "西药", "unit_price": "12.50"},
            {"item_code": "YP002", "item_name": "头孢克肟", "item_category": "西药", "unit_price": "28.00"},
            {"item_code": "YP003", "item_name": "布洛芬缓释胶囊", "item_category": "西药", "unit_price": "15.00"},
            {"item_code": "YP004", "item_name": "板蓝根颗粒", "item_category": "中成药", "unit_price": "18.00"},
            {"item_code": "YP005", "item_name": "感冒灵颗粒", "item_category": "中成药", "unit_price": "22.00"},
        ]
        
        # 批量添加
        for item_data in test_items:
            item = ChargeItem(**item_data)
            db.add(item)
        
        db.commit()
        print(f"成功添加 {len(test_items)} 条收费项目测试数据")
        
    except Exception as e:
        print(f"添加测试数据失败: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    seed_charge_items()
