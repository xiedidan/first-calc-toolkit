"""
为医生维度创建收费项目映射
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

def create_mappings():
    """创建医生维度映射"""
    db = SessionLocal()
    
    try:
        hospital_id = 1  # 医院ID
        
        print("=" * 80)
        print("创建医生维度收费项目映射")
        print("=" * 80)
        
        # 映射规则：基于项目名称关键词
        mapping_rules = [
            # 门诊-诊察类
            {
                'dimension_code': 'dim-doc-out-diag-norm',
                'dimension_name': '普通诊察',
                'keywords': ['门诊诊查费', '挂号', '专家门诊', '特需门诊', '名医门诊']
            },
            # 门诊-检查化验类
            {
                'dimension_code': 'dim-doc-out-eval-exam',
                'dimension_name': '检查化验',
                'keywords': ['OCT', '视网膜厚度检查', '图文报告', '照片', '影像', '检查', '化验', '训练系统']
            },
            # 门诊-药品类（映射到诊断-中草药）
            {
                'dimension_code': 'dim-doc-out-eval-drug',
                'dimension_name': '中草药（药品）',
                'keywords': ['滴眼液', '眼膏', '眼药', '片', '胶囊']
            },
        ]
        
        total_created = 0
        
        for rule in mapping_rules:
            dimension_code = rule['dimension_code']
            dimension_name = rule['dimension_name']
            keywords = rule['keywords']
            
            print(f"\n【{dimension_name}】({dimension_code})")
            print("-" * 80)
            
            # 构建关键词匹配条件
            keyword_conditions = " OR ".join([f"cd.item_name LIKE '%{kw}%'" for kw in keywords])
            
            # 查询匹配的项目
            sql = text(f"""
                SELECT DISTINCT
                    cd.item_code,
                    cd.item_name,
                    COUNT(*) as usage_count,
                    SUM(cd.amount) as total_amount
                FROM charge_details cd
                LEFT JOIN dimension_item_mappings dim 
                    ON cd.item_code = dim.item_code 
                    AND dim.hospital_id = :hospital_id
                    AND dim.dimension_code = :dimension_code
                WHERE cd.business_type = '门诊'
                  AND TO_CHAR(cd.charge_time, 'YYYY-MM') = '2025-10'
                  AND ({keyword_conditions})
                  AND dim.id IS NULL
                GROUP BY cd.item_code, cd.item_name
                ORDER BY total_amount DESC
            """)
            
            result = db.execute(sql, {
                'hospital_id': hospital_id,
                'dimension_code': dimension_code
            })
            items = result.fetchall()
            
            if not items:
                print(f"  没有找到匹配的项目")
                continue
            
            print(f"  找到 {len(items)} 个匹配项目:")
            print(f"  {'项目代码':<15} {'项目名称':<40} {'使用次数':>10} {'总金额':>15}")
            print("  " + "-" * 80)
            
            created_count = 0
            for item in items:
                print(f"  {item.item_code:<15} {item.item_name[:38]:<40} {item.usage_count:>10} {float(item.total_amount):>15,.2f}")
                
                # 创建映射
                insert_sql = text("""
                    INSERT INTO dimension_item_mappings 
                        (item_code, dimension_code, hospital_id, created_at)
                    VALUES 
                        (:item_code, :dimension_code, :hospital_id, NOW())
                    ON CONFLICT (dimension_code, item_code, hospital_id) DO NOTHING
                """)
                
                db.execute(insert_sql, {
                    'item_code': item.item_code,
                    'dimension_code': dimension_code,
                    'hospital_id': hospital_id
                })
                created_count += 1
            
            db.commit()
            total_created += created_count
            print(f"  ✓ 创建了 {created_count} 个映射")
        
        print("\n" + "=" * 80)
        print(f"✓ 总计创建了 {total_created} 个映射")
        print("=" * 80)
        
        # 验证映射效果
        print("\n【验证映射效果】")
        print("-" * 80)
        
        sql = text("""
            SELECT 
                cd.business_type,
                COUNT(*) as total_records,
                SUM(cd.amount) as total_amount,
                COUNT(CASE WHEN dim.id IS NOT NULL THEN 1 END) as mapped_records,
                SUM(CASE WHEN dim.id IS NOT NULL THEN cd.amount ELSE 0 END) as mapped_amount,
                ROUND(COUNT(CASE WHEN dim.id IS NOT NULL THEN 1 END)::numeric / COUNT(*)::numeric * 100, 2) as record_coverage,
                ROUND(SUM(CASE WHEN dim.id IS NOT NULL THEN cd.amount ELSE 0 END)::numeric / SUM(cd.amount)::numeric * 100, 2) as amount_coverage
            FROM charge_details cd
            LEFT JOIN dimension_item_mappings dim 
                ON cd.item_code = dim.item_code 
                AND dim.hospital_id = :hospital_id
                AND dim.dimension_code LIKE 'dim-doc%'
            WHERE TO_CHAR(cd.charge_time, 'YYYY-MM') = '2025-10'
              AND cd.business_type = '门诊'
            GROUP BY cd.business_type
        """)
        
        result = db.execute(sql, {'hospital_id': hospital_id})
        row = result.fetchone()
        
        if row:
            print(f"门诊记录覆盖率: {float(row.record_coverage):.2f}%")
            print(f"门诊金额覆盖率: {float(row.amount_coverage):.2f}%")
            print(f"已映射记录数: {row.mapped_records:,} / {row.total_records:,}")
            print(f"已映射金额: {float(row.mapped_amount):,.2f} / {float(row.total_amount):,.2f}")
        
        print("\n建议：重新执行任务 1e0a6392-e0d7-4932-96f3-c1f1cb00b620 查看效果")
        
    except Exception as e:
        db.rollback()
        print(f"\n错误: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    create_mappings()
