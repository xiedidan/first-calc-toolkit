"""
测试维度目录映射查询
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal
from app.models.dimension_item_mapping import DimensionItemMapping
from app.models.charge_item import ChargeItem
from sqlalchemy import func

def test_query():
    db = SessionLocal()
    try:
        # 1. 查询总数
        total = db.query(DimensionItemMapping).count()
        print(f"维度目录映射总数: {total}")
        
        # 2. 按维度分组统计
        print("\n按维度分组统计:")
        stats = db.query(
            DimensionItemMapping.dimension_id,
            func.count(DimensionItemMapping.id).label('count')
        ).group_by(DimensionItemMapping.dimension_id).all()
        
        for dim_id, count in stats:
            print(f"  维度ID {dim_id}: {count} 条")
        
        # 3. 查询最近10条记录
        print("\n最近10条记录:")
        recent = db.query(DimensionItemMapping).order_by(
            DimensionItemMapping.created_at.desc()
        ).limit(10).all()
        
        for mapping in recent:
            print(f"  ID: {mapping.id}, 维度ID: {mapping.dimension_id}, 项目编码: {mapping.item_code}, 创建时间: {mapping.created_at}")
        
        # 4. 检查收费项目是否存在
        print("\n检查收费项目:")
        charge_items_count = db.query(ChargeItem).count()
        print(f"  收费项目总数: {charge_items_count}")
        
        if recent:
            first_mapping = recent[0]
            charge_item = db.query(ChargeItem).filter(
                ChargeItem.item_code == first_mapping.item_code
            ).first()
            if charge_item:
                print(f"  项目编码 {first_mapping.item_code} 存在: {charge_item.item_name}")
            else:
                print(f"  项目编码 {first_mapping.item_code} 不存在（这是正常的，映射可以独立存在）")
        
    finally:
        db.close()

if __name__ == "__main__":
    test_query()
