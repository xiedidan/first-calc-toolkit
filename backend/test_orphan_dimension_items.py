"""
测试维度项目中的"孤儿"记录（收费编码不在收费项目表中的记录）
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# 创建数据库连接
engine = create_engine(settings.SQLALCHEMY_DATABASE_URI)
SessionLocal = sessionmaker(bind=engine)

def test_orphan_records():
    """测试查询孤儿记录"""
    db = SessionLocal()
    
    try:
        print("=" * 80)
        print("测试1: 查找所有孤儿记录（收费编码不在收费项目表中）")
        print("=" * 80)
        
        query = text("""
            SELECT 
                dim.id,
                dim.dimension_id,
                dim.item_code,
                dim.created_at,
                ci.item_name,
                ci.item_category
            FROM dimension_item_mapping dim
            LEFT JOIN charge_items ci ON dim.item_code = ci.item_code
            WHERE ci.item_code IS NULL
            LIMIT 20
        """)
        
        result = db.execute(query)
        orphan_records = result.fetchall()
        
        if orphan_records:
            print(f"\n找到 {len(orphan_records)} 条孤儿记录：")
            print("-" * 80)
            for record in orphan_records:
                print(f"ID: {record.id}, 维度ID: {record.dimension_id}, "
                      f"收费编码: {record.item_code}, 创建时间: {record.created_at}")
        else:
            print("\n✓ 没有找到孤儿记录")
        
        print("\n" + "=" * 80)
        print("测试2: 统计每个维度的孤儿记录数量")
        print("=" * 80)
        
        query = text("""
            SELECT 
                dim.dimension_id,
                COUNT(*) as orphan_count
            FROM dimension_item_mapping dim
            LEFT JOIN charge_items ci ON dim.item_code = ci.item_code
            WHERE ci.item_code IS NULL
            GROUP BY dim.dimension_id
            ORDER BY orphan_count DESC
        """)
        
        result = db.execute(query)
        stats = result.fetchall()
        
        if stats:
            print("\n各维度的孤儿记录统计：")
            print("-" * 80)
            for stat in stats:
                print(f"维度ID: {stat.dimension_id}, 孤儿记录数: {stat.orphan_count}")
        else:
            print("\n✓ 所有维度都没有孤儿记录")
        
        print("\n" + "=" * 80)
        print("测试3: 查询包含孤儿记录的维度的所有记录（模拟API查询）")
        print("=" * 80)
        
        if orphan_records:
            # 取第一个孤儿记录的维度ID
            test_dimension_id = orphan_records[0].dimension_id
            
            query = text("""
                SELECT 
                    dim.id,
                    dim.dimension_id,
                    dim.item_code,
                    dim.created_at,
                    ci.item_name,
                    ci.item_category
                FROM dimension_item_mapping dim
                LEFT JOIN charge_items ci ON dim.item_code = ci.item_code
                WHERE dim.dimension_id = :dimension_id
                ORDER BY dim.created_at DESC
                LIMIT 10
            """)
            
            result = db.execute(query, {"dimension_id": test_dimension_id})
            all_records = result.fetchall()
            
            print(f"\n维度 {test_dimension_id} 的所有记录（包括孤儿记录）：")
            print("-" * 80)
            for record in all_records:
                status = "✗ 孤儿记录" if record.item_name is None else "✓ 正常记录"
                print(f"{status} | ID: {record.id}, 编码: {record.item_code}, "
                      f"名称: {record.item_name or '(不存在)'}")
        
        print("\n" + "=" * 80)
        print("测试完成！")
        print("=" * 80)
        print("\n说明：")
        print("- 孤儿记录：维度项目映射表中存在，但对应的收费项目不存在")
        print("- 修复后的API会显示这些记录，item_name 和 item_category 为 None")
        print("- 前端会显示'项目不存在'标签，用户可以删除这些记录")
        
    except Exception as e:
        print(f"\n✗ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    test_orphan_records()
