"""
测试API是否能正确返回孤儿记录
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.api.dimension_items import get_dimension_items
from app.api.deps import get_db
from unittest.mock import MagicMock

# 创建数据库连接
engine = create_engine(settings.SQLALCHEMY_DATABASE_URI)
SessionLocal = sessionmaker(bind=engine)

def test_api_with_orphan_records():
    """测试API查询包含孤儿记录的维度"""
    db = SessionLocal()
    
    try:
        print("=" * 80)
        print("测试API查询孤儿记录")
        print("=" * 80)
        
        # 首先找到有孤儿记录的维度
        query = text("""
            SELECT DISTINCT dim.dimension_id
            FROM dimension_item_mapping dim
            LEFT JOIN charge_items ci ON dim.item_code = ci.item_code
            WHERE ci.item_code IS NULL
            LIMIT 1
        """)
        
        result = db.execute(query)
        row = result.fetchone()
        
        if not row:
            print("\n✓ 数据库中没有孤儿记录，无需测试")
            return
        
        test_dimension_id = row.dimension_id
        print(f"\n找到包含孤儿记录的维度ID: {test_dimension_id}")
        
        # 测试1: 不带关键词查询
        print("\n" + "-" * 80)
        print("测试1: 查询所有记录（不带关键词）")
        print("-" * 80)
        
        mock_user = MagicMock()
        result = get_dimension_items(
            dimension_id=test_dimension_id,
            keyword=None,
            page=1,
            size=100,
            db=db,
            current_user=mock_user
        )
        
        print(f"总记录数: {result.total}")
        print(f"返回记录数: {len(result.items)}")
        
        orphan_count = sum(1 for item in result.items if item.item_name is None)
        normal_count = len(result.items) - orphan_count
        
        print(f"孤儿记录: {orphan_count}")
        print(f"正常记录: {normal_count}")
        
        if orphan_count > 0:
            print("\n孤儿记录示例：")
            for item in result.items:
                if item.item_name is None:
                    print(f"  - ID: {item.id}, 编码: {item.item_code}, "
                          f"名称: {item.item_name}, 分类: {item.item_category}")
                    break
        
        # 测试2: 使用孤儿记录的编码搜索
        print("\n" + "-" * 80)
        print("测试2: 使用孤儿记录的编码搜索")
        print("-" * 80)
        
        if orphan_count > 0:
            orphan_item = next(item for item in result.items if item.item_name is None)
            search_keyword = orphan_item.item_code[:5]  # 使用编码的前5个字符
            
            print(f"搜索关键词: {search_keyword}")
            
            search_result = get_dimension_items(
                dimension_id=test_dimension_id,
                keyword=search_keyword,
                page=1,
                size=100,
                db=db,
                current_user=mock_user
            )
            
            print(f"搜索结果数: {search_result.total}")
            
            found_orphan = any(
                item.item_code == orphan_item.item_code 
                for item in search_result.items
            )
            
            if found_orphan:
                print(f"✓ 成功找到孤儿记录: {orphan_item.item_code}")
            else:
                print(f"✗ 未找到孤儿记录: {orphan_item.item_code}")
        
        # 测试3: 验证SQL查询
        print("\n" + "-" * 80)
        print("测试3: 直接SQL查询验证")
        print("-" * 80)
        
        query = text("""
            SELECT 
                dim.id,
                dim.item_code,
                ci.item_name,
                ci.item_category,
                CASE WHEN ci.item_code IS NULL THEN '孤儿记录' ELSE '正常记录' END as status
            FROM dimension_item_mapping dim
            LEFT JOIN charge_items ci ON dim.item_code = ci.item_code
            WHERE dim.dimension_id = :dimension_id
            ORDER BY status DESC, dim.id
            LIMIT 10
        """)
        
        result = db.execute(query, {"dimension_id": test_dimension_id})
        rows = result.fetchall()
        
        print(f"\n前10条记录：")
        for row in rows:
            print(f"  {row.status} | ID: {row.id}, 编码: {row.item_code}, "
                  f"名称: {row.item_name or '(无)'}")
        
        print("\n" + "=" * 80)
        print("测试完成！")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n✗ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    test_api_with_orphan_records()
