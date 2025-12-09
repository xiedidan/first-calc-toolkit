"""
分析医生维度映射缺口
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

def analyze_mapping_gap():
    """分析医生维度映射缺口"""
    db = SessionLocal()
    
    try:
        print("=" * 80)
        print("医生维度映射缺口分析")
        print("=" * 80)
        
        # 1. 查询未映射的高频门诊项目
        print("\n【1. 未映射的高频门诊项目（2025-10）】")
        print("-" * 80)
        
        sql = text("""
            SELECT 
                cd.item_code,
                cd.item_name,
                COUNT(*) as usage_count,
                SUM(cd.amount) as total_amount,
                ROUND(SUM(cd.amount) / COUNT(*), 2) as avg_amount
            FROM charge_details cd
            LEFT JOIN dimension_item_mappings dim 
                ON cd.item_code = dim.item_code AND dim.hospital_id = 1
            WHERE cd.business_type = '门诊'
              AND TO_CHAR(cd.charge_time, 'YYYY-MM') = '2025-10'
              AND dim.id IS NULL
            GROUP BY cd.item_code, cd.item_name
            HAVING COUNT(*) > 100
            ORDER BY total_amount DESC
            LIMIT 30
        """)
        
        result = db.execute(sql)
        rows = result.fetchall()
        
        print(f"{'项目代码':<15} {'项目名称':<30} {'使用次数':>10} {'总金额':>15} {'平均金额':>10}")
        print("-" * 80)
        
        total_unmapped_amount = 0
        for row in rows:
            print(f"{row.item_code:<15} {row.item_name[:28]:<30} {row.usage_count:>10} {float(row.total_amount):>15,.2f} {float(row.avg_amount):>10,.2f}")
            total_unmapped_amount += float(row.total_amount)
        
        print("-" * 80)
        print(f"{'合计':<45} {'':<10} {total_unmapped_amount:>15,.2f}")
        
        # 2. 查询未映射的高频住院项目
        print("\n【2. 未映射的高频住院项目（2025-10）】")
        print("-" * 80)
        
        sql = text("""
            SELECT 
                cd.item_code,
                cd.item_name,
                COUNT(*) as usage_count,
                SUM(cd.amount) as total_amount,
                ROUND(SUM(cd.amount) / COUNT(*), 2) as avg_amount
            FROM charge_details cd
            LEFT JOIN dimension_item_mappings dim 
                ON cd.item_code = dim.item_code AND dim.hospital_id = 1
            WHERE cd.business_type = '住院'
              AND TO_CHAR(cd.charge_time, 'YYYY-MM') = '2025-10'
              AND dim.id IS NULL
            GROUP BY cd.item_code, cd.item_name
            HAVING COUNT(*) > 1
            ORDER BY total_amount DESC
            LIMIT 20
        """)
        
        result = db.execute(sql)
        rows = result.fetchall()
        
        if rows:
            print(f"{'项目代码':<15} {'项目名称':<30} {'使用次数':>10} {'总金额':>15} {'平均金额':>10}")
            print("-" * 80)
            
            for row in rows:
                print(f"{row.item_code:<15} {row.item_name[:28]:<30} {row.usage_count:>10} {float(row.total_amount):>15,.2f} {float(row.avg_amount):>10,.2f}")
        else:
            print("住院项目映射完整")
        
        # 3. 建议的映射规则
        print("\n【3. 建议的映射规则】")
        print("-" * 80)
        
        suggestions = [
            ("门诊诊查费", "dim-doc-out-diag-norm", "普通诊察"),
            ("专家门诊诊查费", "dim-doc-out-diag-norm", "普通诊察"),
            ("挂号", "dim-doc-out-diag-norm", "普通诊察"),
            ("OCT", "dim-doc-out-eval-exam", "检查化验"),
            ("视网膜厚度检查", "dim-doc-out-eval-exam", "检查化验"),
            ("图文报告", "dim-doc-out-eval-exam", "检查化验"),
            ("照片", "dim-doc-out-eval-exam", "检查化验"),
            ("滴眼液", "dim-doc-out-eval-drug", "中草药（药品）"),
            ("眼药", "dim-doc-out-eval-drug", "中草药（药品）"),
        ]
        
        print("根据项目名称关键词建议映射：")
        print()
        for keyword, dimension_code, dimension_name in suggestions:
            print(f"  关键词: {keyword:<20} → {dimension_code:<25} ({dimension_name})")
        
        # 4. 统计映射覆盖率
        print("\n【4. 映射覆盖率统计（2025-10）】")
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
                AND dim.hospital_id = 1
                AND dim.dimension_code LIKE 'dim-doc%'
            WHERE TO_CHAR(cd.charge_time, 'YYYY-MM') = '2025-10'
            GROUP BY cd.business_type
        """)
        
        result = db.execute(sql)
        rows = result.fetchall()
        
        print(f"{'业务类型':<10} {'总记录数':>12} {'总金额':>15} {'已映射记录':>12} {'已映射金额':>15} {'记录覆盖率':>12} {'金额覆盖率':>12}")
        print("-" * 80)
        
        for row in rows:
            print(f"{row.business_type:<10} {row.total_records:>12,} {float(row.total_amount):>15,.2f} {row.mapped_records:>12,} {float(row.mapped_amount):>15,.2f} {float(row.record_coverage):>11.2f}% {float(row.amount_coverage):>11.2f}%")
        
        print("\n" + "=" * 80)
        print("分析完成")
        print("=" * 80)
        
        print("\n【建议】")
        print("1. 需要为门诊诊察、检查、药品等项目建立映射关系")
        print("2. 可以通过项目名称关键词批量创建映射")
        print("3. 或者在前端「维度项目映射」功能中手动添加映射")
        
    except Exception as e:
        print(f"\n错误: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    analyze_mapping_gap()
