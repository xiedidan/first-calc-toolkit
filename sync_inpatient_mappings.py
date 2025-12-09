"""
同步门诊映射到住院维度
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

def sync_mappings():
    """同步门诊映射到住院"""
    db = SessionLocal()
    
    try:
        hospital_id = 1
        
        print("=" * 80)
        print("同步门诊映射到住院维度")
        print("=" * 80)
        
        # 映射关系：门诊维度 -> 住院维度
        dimension_mapping = {
            'dim-doc-out-diag-norm': 'dim-doc-in-diag-norm',  # 普通诊察
            'dim-doc-out-eval-exam': 'dim-doc-in-eval-exam',  # 检查化验
            'dim-doc-out-eval-drug': 'dim-doc-in-eval-drug',  # 中草药
            'dim-doc-out-eval-tr': 'dim-doc-in-eval-tr',      # 治疗手术
            'dim-doc-out-tr-1': 'dim-doc-in-tr-1',            # 甲级治疗
            'dim-doc-out-tr-2': 'dim-doc-in-tr-2',            # 乙级治疗
            'dim-doc-out-tr-3': 'dim-doc-in-tr-3',            # 丙级治疗
            'dim-doc-out-tr-other': 'dim-doc-in-tr-other',    # 其他治疗
        }
        
        total_created = 0
        
        for out_code, in_code in dimension_mapping.items():
            print(f"\n【{out_code} → {in_code}】")
            print("-" * 80)
            
            # 查询门诊维度的映射
            sql = text("""
                SELECT DISTINCT item_code
                FROM dimension_item_mappings
                WHERE dimension_code = :out_code
                  AND hospital_id = :hospital_id
            """)
            
            result = db.execute(sql, {
                'out_code': out_code,
                'hospital_id': hospital_id
            })
            item_codes = [row.item_code for row in result.fetchall()]
            
            if not item_codes:
                print(f"  门诊维度 {out_code} 没有映射")
                continue
            
            print(f"  找到 {len(item_codes)} 个门诊映射项目")
            
            # 为每个item_code创建住院映射
            created_count = 0
            for item_code in item_codes:
                insert_sql = text("""
                    INSERT INTO dimension_item_mappings 
                        (item_code, dimension_code, hospital_id, created_at)
                    VALUES 
                        (:item_code, :in_code, :hospital_id, NOW())
                    ON CONFLICT (dimension_code, item_code, hospital_id) DO NOTHING
                """)
                
                result = db.execute(insert_sql, {
                    'item_code': item_code,
                    'in_code': in_code,
                    'hospital_id': hospital_id
                })
                
                if result.rowcount > 0:
                    created_count += 1
            
            db.commit()
            total_created += created_count
            print(f"  ✓ 创建了 {created_count} 个住院映射")
        
        print("\n" + "=" * 80)
        print(f"✓ 总计创建了 {total_created} 个住院映射")
        print("=" * 80)
        
        # 验证映射效果
        print("\n【验证映射效果】")
        print("-" * 80)
        
        # 统计住院映射数量
        sql = text("""
            SELECT dimension_code, COUNT(*) as mapping_count
            FROM dimension_item_mappings
            WHERE dimension_code LIKE 'dim-doc-in%'
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
        
        # 检查2023-10的住院数据覆盖率
        print("\n【住院数据覆盖率（2023-10）】")
        print("-" * 80)
        
        sql = text("""
            SELECT 
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
                AND dim.dimension_code LIKE 'dim-doc-in%'
            WHERE TO_CHAR(cd.charge_time, 'YYYY-MM') = '2023-10'
              AND cd.business_type = '住院'
        """)
        
        result = db.execute(sql, {'hospital_id': hospital_id})
        row = result.fetchone()
        
        if row and row.total_records > 0:
            print(f"总记录数: {row.total_records:,}")
            print(f"总金额: {float(row.total_amount):,.2f}")
            print(f"已映射记录数: {row.mapped_records:,}")
            print(f"已映射金额: {float(row.mapped_amount):,.2f}")
            print(f"记录覆盖率: {float(row.record_coverage):.2f}%")
            print(f"金额覆盖率: {float(row.amount_coverage):.2f}%")
        else:
            print("2023-10没有住院数据")
        
        print("\n建议：重新执行任务查看效果")
        
    except Exception as e:
        db.rollback()
        print(f"\n错误: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    sync_mappings()
