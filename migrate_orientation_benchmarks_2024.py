"""
从 orientation_benchmarks_20251225 表统计2024年全年平均药、耗占比，
写入 orientation_benchmarks 表作为导向基准。

改进：将HIS科室代码转换为核算单元代码

映射关系：
- orientation_benchmarks_20251225.rule_id 10 (药占比) → orientation_benchmarks.rule_id 74
- orientation_benchmarks_20251225.rule_id 12 (耗占比) → orientation_benchmarks.rule_id 75, 77

执行前会清空 orientation_benchmarks 表中的所有数据。
"""
import os
import sys

# 添加backend路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# 加载环境变量
load_dotenv(os.path.join(os.path.dirname(__file__), 'backend', '.env'))

DATABASE_URL = os.getenv('DATABASE_URL')
if not DATABASE_URL:
    print("错误: 未找到 DATABASE_URL 环境变量")
    sys.exit(1)

engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)


def migrate_benchmarks():
    """迁移导向基准数据"""
    session = Session()
    
    try:
        # 1. 清空 orientation_benchmarks 表
        print("步骤1: 清空 orientation_benchmarks 表...")
        result = session.execute(text("DELETE FROM orientation_benchmarks"))
        deleted_count = result.rowcount
        print(f"  已删除 {deleted_count} 条记录")
        session.commit()
        
        # 2. 统计2024年全年平均药占比 (rule_id 10 → 74)
        # 通过JOIN departments表将HIS科室代码转换为核算单元代码
        print("\n步骤2: 统计2024年药占比平均值 (rule_id 10 → 74)...")
        drug_ratio_sql = """
        INSERT INTO orientation_benchmarks (
            hospital_id, rule_id, department_code, department_name,
            benchmark_type, control_intensity, stat_start_date, stat_end_date,
            benchmark_value, created_at, updated_at
        )
        SELECT 
            ob.hospital_id,
            74 as rule_id,
            d.accounting_unit_code as department_code,
            d.accounting_unit_name as department_name,
            'average' as benchmark_type,
            1.0000 as control_intensity,
            '2024-01-01'::timestamp as stat_start_date,
            '2024-12-31'::timestamp as stat_end_date,
            ROUND(AVG(ob.benchmark_value), 4) as benchmark_value,
            NOW() as created_at,
            NOW() as updated_at
        FROM orientation_benchmarks_20251225 ob
        JOIN departments d ON ob.department_code = d.his_code AND ob.hospital_id = d.hospital_id
        WHERE ob.rule_id = 10
          AND ob.stat_start_date >= '2024-01-01'
          AND ob.stat_start_date < '2025-01-01'
          AND d.accounting_unit_code IS NOT NULL
        GROUP BY ob.hospital_id, d.accounting_unit_code, d.accounting_unit_name
        ORDER BY d.accounting_unit_code
        """
        result = session.execute(text(drug_ratio_sql))
        drug_count = result.rowcount
        print(f"  插入 {drug_count} 条药占比基准记录")
        session.commit()
        
        # 3. 统计2024年全年平均耗占比 (rule_id 12 → 75 医生手术耗占比)
        print("\n步骤3: 统计2024年耗占比平均值 (rule_id 12 → 75 医生手术耗占比)...")
        consumable_ratio_sql_75 = """
        INSERT INTO orientation_benchmarks (
            hospital_id, rule_id, department_code, department_name,
            benchmark_type, control_intensity, stat_start_date, stat_end_date,
            benchmark_value, created_at, updated_at
        )
        SELECT 
            ob.hospital_id,
            75 as rule_id,
            d.accounting_unit_code as department_code,
            d.accounting_unit_name as department_name,
            'average' as benchmark_type,
            1.0000 as control_intensity,
            '2024-01-01'::timestamp as stat_start_date,
            '2024-12-31'::timestamp as stat_end_date,
            ROUND(AVG(ob.benchmark_value), 4) as benchmark_value,
            NOW() as created_at,
            NOW() as updated_at
        FROM orientation_benchmarks_20251225 ob
        JOIN departments d ON ob.department_code = d.his_code AND ob.hospital_id = d.hospital_id
        WHERE ob.rule_id = 12
          AND ob.stat_start_date >= '2024-01-01'
          AND ob.stat_start_date < '2025-01-01'
          AND d.accounting_unit_code IS NOT NULL
        GROUP BY ob.hospital_id, d.accounting_unit_code, d.accounting_unit_name
        ORDER BY d.accounting_unit_code
        """
        result = session.execute(text(consumable_ratio_sql_75))
        consumable_count_75 = result.rowcount
        print(f"  插入 {consumable_count_75} 条医生手术耗占比基准记录")
        session.commit()
        
        # 4. 统计2024年全年平均耗占比 (rule_id 12 → 77 医生治疗耗占比)
        print("\n步骤4: 统计2024年耗占比平均值 (rule_id 12 → 77 医生治疗耗占比)...")
        consumable_ratio_sql_77 = """
        INSERT INTO orientation_benchmarks (
            hospital_id, rule_id, department_code, department_name,
            benchmark_type, control_intensity, stat_start_date, stat_end_date,
            benchmark_value, created_at, updated_at
        )
        SELECT 
            ob.hospital_id,
            77 as rule_id,
            d.accounting_unit_code as department_code,
            d.accounting_unit_name as department_name,
            'average' as benchmark_type,
            1.0000 as control_intensity,
            '2024-01-01'::timestamp as stat_start_date,
            '2024-12-31'::timestamp as stat_end_date,
            ROUND(AVG(ob.benchmark_value), 4) as benchmark_value,
            NOW() as created_at,
            NOW() as updated_at
        FROM orientation_benchmarks_20251225 ob
        JOIN departments d ON ob.department_code = d.his_code AND ob.hospital_id = d.hospital_id
        WHERE ob.rule_id = 12
          AND ob.stat_start_date >= '2024-01-01'
          AND ob.stat_start_date < '2025-01-01'
          AND d.accounting_unit_code IS NOT NULL
        GROUP BY ob.hospital_id, d.accounting_unit_code, d.accounting_unit_name
        ORDER BY d.accounting_unit_code
        """
        result = session.execute(text(consumable_ratio_sql_77))
        consumable_count_77 = result.rowcount
        print(f"  插入 {consumable_count_77} 条医生治疗耗占比基准记录")
        session.commit()
        
        # 5. 验证结果
        print("\n步骤5: 验证插入结果...")
        verify_sql = """
        SELECT 
            ob.rule_id,
            r.name as rule_name,
            COUNT(*) as record_count,
            ROUND(AVG(ob.benchmark_value), 4) as avg_benchmark
        FROM orientation_benchmarks ob
        JOIN orientation_rules r ON ob.rule_id = r.id
        GROUP BY ob.rule_id, r.name
        ORDER BY ob.rule_id
        """
        result = session.execute(text(verify_sql))
        rows = result.fetchall()
        
        print("\n  导向基准统计:")
        print("  " + "-" * 70)
        print(f"  {'规则ID':<10} {'规则名称':<25} {'记录数':<10} {'平均基准值':<15}")
        print("  " + "-" * 70)
        for row in rows:
            print(f"  {row[0]:<10} {row[1]:<25} {row[2]:<10} {row[3]:<15}")
        print("  " + "-" * 70)
        
        total_count = drug_count + consumable_count_75 + consumable_count_77
        print(f"\n迁移完成! 共插入 {total_count} 条导向基准记录")
        
        # 6. 显示详细数据
        print("\n详细数据预览:")
        detail_sql = """
        SELECT 
            ob.rule_id,
            r.name as rule_name,
            ob.department_code,
            ob.department_name,
            ob.benchmark_value
        FROM orientation_benchmarks ob
        JOIN orientation_rules r ON ob.rule_id = r.id
        ORDER BY ob.rule_id, ob.department_code
        """
        result = session.execute(text(detail_sql))
        rows = result.fetchall()
        
        print(f"  {'规则ID':<8} {'规则名称':<20} {'核算单元代码':<14} {'核算单元名称':<20} {'基准值':<10}")
        print("  " + "-" * 85)
        for row in rows:
            print(f"  {row[0]:<8} {row[1]:<20} {row[2]:<14} {row[3]:<20} {row[4]:<10}")
        
    except Exception as e:
        session.rollback()
        print(f"\n错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        session.close()


if __name__ == "__main__":
    print("=" * 60)
    print("导向基准数据迁移脚本")
    print("从 orientation_benchmarks_20251225 统计2024年平均值")
    print("写入 orientation_benchmarks 表")
    print("改进：HIS科室代码 → 核算单元代码")
    print("=" * 60)
    print()
    
    # 确认执行
    print("警告: 此操作将清空 orientation_benchmarks 表中的所有数据!")
    print("映射关系:")
    print("  - rule_id 10 (药占比) → rule_id 74 (药占比导向)")
    print("  - rule_id 12 (耗占比) → rule_id 75 (医生手术耗占比导向)")
    print("  - rule_id 12 (耗占比) → rule_id 77 (医生治疗耗占比导向)")
    print()
    
    response = input("确认执行? (y/N): ")
    if response.lower() != 'y':
        print("已取消")
        sys.exit(0)
    
    print()
    migrate_benchmarks()
