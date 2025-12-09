"""
从收费项目目录创建维度映射
"""
import sys
import os
from dotenv import load_dotenv

load_dotenv('backend/.env')
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

DATABASE_URL = os.getenv('DATABASE_URL')
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

def create_mappings_from_items():
    """从收费项目目录创建映射"""
    db = SessionLocal()
    
    try:
        hospital_id = 1
        
        print("=" * 80)
        print("从收费项目目录创建维度映射")
        print("=" * 80)
        
        # 映射规则：基于item_category和item_name关键词
        mapping_rules = [
            # 门诊+住院 诊察类
            {
                'dimensions': ['dim-doc-out-diag-norm', 'dim-doc-in-diag-norm'],
                'dimension_name': '普通诊察',
                'category_keywords': ['诊察费', '挂号费'],
                'name_keywords': []
            },
            # 门诊+住院 检查化验类
            {
                'dimensions': ['dim-doc-out-eval-exam', 'dim-doc-in-eval-exam'],
                'dimension_name': '检查化验',
                'category_keywords': ['检查费', '化验费', '影像费'],
                'name_keywords': ['OCT', '视网膜', '图文报告', '照片', '检查', '化验', '测定', '超声', 'CT', 'MRI']
            },
            # 门诊+住院 中草药类
            {
                'dimensions': ['dim-doc-out-eval-drug', 'dim-doc-in-eval-drug'],
                'dimension_name': '中草药',
                'category_keywords': ['中药费', '中草药'],
                'name_keywords': ['饮片']
            },
        ]
        
        total_created = 0
        
        for rule in mapping_rules:
            dimensions = rule['dimensions']
            dimension_name = rule['dimension_name']
            category_keywords = rule['category_keywords']
            name_keywords = rule['name_keywords']
            
            print(f"\n【{dimension_name}】")
            print(f"  目标维度: {', '.join(dimensions)}")
            print("-" * 80)
            
            # 构建查询条件
            conditions = []
            
            # 类别匹配
            if category_keywords:
                category_conditions = " OR ".join([f"ci.item_category LIKE '%{kw}%'" for kw in category_keywords])
                conditions.append(f"({category_conditions})")
            
            # 名称匹配
            if name_keywords:
                name_conditions = " OR ".join([f"ci.item_name LIKE '%{kw}%'" for kw in name_keywords])
                conditions.append(f"({name_conditions})")
            
            if not conditions:
                continue
            
            where_clause = " OR ".join(conditions)
            
            # 查询匹配的收费项目
            sql = text(f"""
                SELECT DISTINCT
                    ci.item_code,
                    ci.item_name,
                    ci.item_category
                FROM charge_items ci
                LEFT JOIN dimension_item_mappings dim 
                    ON ci.item_code = dim.item_code 
                    AND dim.hospital_id = :hospital_id
                    AND dim.dimension_code = ANY(:dimensions)
                WHERE ci.hospital_id = :hospital_id
                  AND ({where_clause})
                  AND dim.id IS NULL
                ORDER BY ci.item_category, ci.item_name
            """)
            
            result = db.execute(sql, {
                'hospital_id': hospital_id,
                'dimensions': dimensions
            })
            items = result.fetchall()
            
            if not items:
                print(f"  没有找到新的匹配项目")
                continue
            
            print(f"  找到 {len(items)} 个匹配项目:")
            
            # 按类别分组显示
            by_category = {}
            for item in items:
                category = item.item_category or '未分类'
                if category not in by_category:
                    by_category[category] = []
                by_category[category].append(item)
            
            for category, category_items in sorted(by_category.items()):
                print(f"\n  [{category}] - {len(category_items)}个项目")
                for item in category_items[:5]:  # 只显示前5个
                    print(f"    - {item.item_code}: {item.item_name}")
                if len(category_items) > 5:
                    print(f"    ... 还有 {len(category_items) - 5} 个项目")
            
            # 为每个维度创建映射
            created_count = 0
            for dimension_code in dimensions:
                for item in items:
                    insert_sql = text("""
                        INSERT INTO dimension_item_mappings 
                            (item_code, dimension_code, hospital_id, created_at)
                        VALUES 
                            (:item_code, :dimension_code, :hospital_id, NOW())
                        ON CONFLICT (dimension_code, item_code, hospital_id) DO NOTHING
                    """)
                    
                    result = db.execute(insert_sql, {
                        'item_code': item.item_code,
                        'dimension_code': dimension_code,
                        'hospital_id': hospital_id
                    })
                    
                    if result.rowcount > 0:
                        created_count += 1
            
            db.commit()
            total_created += created_count
            print(f"\n  ✓ 创建了 {created_count} 个映射")
        
        print("\n" + "=" * 80)
        print(f"✓ 总计创建了 {total_created} 个新映射")
        print("=" * 80)
        
        # 验证映射效果
        print("\n【当前映射统计】")
        print("-" * 80)
        
        sql = text("""
            SELECT dimension_code, COUNT(*) as mapping_count
            FROM dimension_item_mappings
            WHERE dimension_code LIKE 'dim-doc%'
              AND hospital_id = :hospital_id
            GROUP BY dimension_code
            ORDER BY dimension_code
        """)
        
        result = db.execute(sql, {'hospital_id': hospital_id})
        rows = result.fetchall()
        
        print(f"{'维度代码':<25} {'映射数量':>10}")
        print("-" * 80)
        for row in rows:
            print(f"{row.dimension_code:<25} {row.mapping_count:>10}")
        
        print("\n建议：重新执行任务查看效果")
        
    except Exception as e:
        db.rollback()
        print(f"\n错误: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    create_mappings_from_items()
