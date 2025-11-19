"""
测试维度Code迁移
验证所有功能是否正常工作
"""
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app.models.dimension_item_mapping import DimensionItemMapping
from app.models.model_node import ModelNode
from app.models.charge_item import ChargeItem

# 数据库连接
DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/performance_system"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)


def test_table_structure():
    """测试表结构是否正确"""
    print("\n=== 测试1: 检查表结构 ===")
    
    inspector = inspect(engine)
    columns = inspector.get_columns('dimension_item_mappings')
    column_names = [col['name'] for col in columns]
    
    print(f"表字段: {column_names}")
    
    # 检查是否有 dimension_code 字段
    if 'dimension_code' in column_names:
        print("✅ dimension_code 字段存在")
    else:
        print("❌ dimension_code 字段不存在")
        return False
    
    # 检查是否没有 dimension_id 字段
    if 'dimension_id' not in column_names:
        print("✅ dimension_id 字段已删除")
    else:
        print("❌ dimension_id 字段仍然存在")
        return False
    
    # 检查索引
    indexes = inspector.get_indexes('dimension_item_mappings')
    index_names = [idx['name'] for idx in indexes]
    print(f"索引: {index_names}")
    
    if 'ix_dimension_item_mappings_dimension_code' in index_names:
        print("✅ dimension_code 索引存在")
    else:
        print("⚠️  dimension_code 索引不存在")
    
    return True


def test_data_migration():
    """测试数据迁移是否正确"""
    print("\n=== 测试2: 检查数据迁移 ===")
    
    db = SessionLocal()
    try:
        # 查询所有映射
        mappings = db.query(DimensionItemMapping).limit(10).all()
        
        if not mappings:
            print("⚠️  没有找到映射数据")
            return True
        
        print(f"找到 {len(mappings)} 条映射记录")
        
        # 检查每条记录
        all_valid = True
        for mapping in mappings:
            # 检查 dimension_code 是否有值
            if not mapping.dimension_code:
                print(f"❌ 映射 {mapping.id} 的 dimension_code 为空")
                all_valid = False
                continue
            
            # 检查 dimension_code 是否对应有效的节点
            node = db.query(ModelNode).filter(ModelNode.code == mapping.dimension_code).first()
            if not node:
                print(f"❌ 映射 {mapping.id} 的 dimension_code '{mapping.dimension_code}' 找不到对应的节点")
                all_valid = False
            else:
                print(f"✅ 映射 {mapping.id}: code={mapping.dimension_code}, item={mapping.item_code}")
        
        return all_valid
    
    finally:
        db.close()


def test_query_by_code():
    """测试按code查询"""
    print("\n=== 测试3: 按code查询 ===")
    
    db = SessionLocal()
    try:
        # 获取一个有效的维度code
        node = db.query(ModelNode).filter(ModelNode.code.isnot(None)).first()
        if not node:
            print("⚠️  没有找到有效的维度节点")
            return True
        
        print(f"测试维度: {node.name} (code={node.code})")
        
        # 查询该维度的所有映射
        mappings = db.query(DimensionItemMapping).filter(
            DimensionItemMapping.dimension_code == node.code
        ).all()
        
        print(f"✅ 找到 {len(mappings)} 条映射记录")
        
        # 测试JOIN查询
        results = db.query(
            DimensionItemMapping.id,
            DimensionItemMapping.dimension_code,
            DimensionItemMapping.item_code,
            ChargeItem.item_name,
            ModelNode.name.label('dimension_name')
        ).outerjoin(
            ChargeItem,
            DimensionItemMapping.item_code == ChargeItem.item_code
        ).outerjoin(
            ModelNode,
            DimensionItemMapping.dimension_code == ModelNode.code
        ).filter(
            DimensionItemMapping.dimension_code == node.code
        ).limit(5).all()
        
        print(f"✅ JOIN查询成功，返回 {len(results)} 条记录")
        
        for r in results:
            print(f"  - {r.dimension_name} / {r.item_code} / {r.item_name}")
        
        return True
    
    except Exception as e:
        print(f"❌ 查询失败: {e}")
        return False
    
    finally:
        db.close()


def test_create_mapping():
    """测试创建映射"""
    print("\n=== 测试4: 创建映射 ===")
    
    db = SessionLocal()
    try:
        # 获取一个有效的维度code和收费项目code
        node = db.query(ModelNode).filter(ModelNode.code.isnot(None)).first()
        charge_item = db.query(ChargeItem).first()
        
        if not node or not charge_item:
            print("⚠️  没有找到测试数据")
            return True
        
        # 检查是否已存在
        existing = db.query(DimensionItemMapping).filter(
            DimensionItemMapping.dimension_code == node.code,
            DimensionItemMapping.item_code == charge_item.item_code
        ).first()
        
        if existing:
            print(f"✅ 映射已存在: {node.code} - {charge_item.item_code}")
            return True
        
        # 创建新映射
        mapping = DimensionItemMapping(
            dimension_code=node.code,
            item_code=charge_item.item_code
        )
        db.add(mapping)
        db.commit()
        
        print(f"✅ 成功创建映射: {node.code} - {charge_item.item_code}")
        
        # 删除测试数据
        db.delete(mapping)
        db.commit()
        print("✅ 测试数据已清理")
        
        return True
    
    except Exception as e:
        print(f"❌ 创建映射失败: {e}")
        db.rollback()
        return False
    
    finally:
        db.close()


def main():
    """运行所有测试"""
    print("=" * 60)
    print("维度Code迁移测试")
    print("=" * 60)
    
    tests = [
        ("表结构检查", test_table_structure),
        ("数据迁移检查", test_data_migration),
        ("按code查询", test_query_by_code),
        ("创建映射", test_create_mapping),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n❌ 测试 '{name}' 出错: {e}")
            results.append((name, False))
    
    # 打印总结
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{status} - {name}")
    
    print(f"\n总计: {passed}/{total} 测试通过")
    
    if passed == total:
        print("\n🎉 所有测试通过！迁移成功！")
        return 0
    else:
        print("\n⚠️  部分测试失败，请检查问题")
        return 1


if __name__ == "__main__":
    sys.exit(main())
