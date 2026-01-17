"""
从 orientation_benchmarks_20251225 表迁移药、耗占比实际值到 orientation_benchmarks 表。

改进：
1. 将HIS科室代码转换为核算单元代码
2. 聚合2024年（2024-01到2024-12）的数据，计算年度基准值
3. 每个科室只生成一条记录，基准值 = sum(target_sum) / sum(total_sum)

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


def migrate_actual_values():
    """迁移导向实际值数据"""
    session = Session()
    
    try:
        # 1. 清空 orientation_benchmarks 表
        print("步骤1: 清空 orientation_benchmarks 表...")
        result = session.execute(text("DELETE FROM orientation_benchmarks"))
        deleted_count = result.rowcount
        print(f"  已删除 {deleted_count} 条记录")
        session.commit()
        
        # 2. 迁移药占比 (rule_id 10 → 74)
        # 聚合2024年全年数据，计算年度基准值 = sum(target_sum) / sum(total_sum)
        print("\n步骤2: 迁移药占比实际值 (rule_id 10 → 74, 2024年度聚合)...")
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
            1.0 as control_intensity,
            '2024-01-01'::timestamp as stat_start_date,
            '2024-12-31'::timestamp as stat_end_date,
            CASE WHEN SUM(ob.total_sum) > 0 
                 THEN SUM(ob.target_sum) / SUM(ob.total_sum)
                 ELSE 0 
            END as benchmark_value,
            NOW() as created_at,
            NOW() as updated_at
        FROM orientation_benchmarks_20251225 ob
        JOIN departments d ON ob.department_code = d.his_code AND ob.hospital_id = d.hospital_id
        WHERE ob.rule_id = 10
          AND d.accounting_unit_code IS NOT NULL
          AND ob.stat_start_date >= '2024-01-01'
          AND ob.stat_end_date <= '2024-12-31'
        GROUP BY ob.hospital_id, d.accounting_unit_code, d.accounting_unit_name
        ORDER BY d.accounting_unit_code
        """
        result = session.execute(text(drug_ratio_sql))
        drug_count = result.rowcount
        print(f"  插入 {drug_count} 条药占比记录")
        session.commit()
        
        # 3. 迁移耗占比到 rule_id 75 (医生手术耗占比)
        print("\n步骤3: 迁移耗占比实际值 (rule_id 12 → 75 医生手术耗占比, 2024年度聚合)...")
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
            1.0 as control_intensity,
            '2024-01-01'::timestamp as stat_start_date,
            '2024-12-31'::timestamp as stat_end_date,
            CASE WHEN SUM(ob.total_sum) > 0 
                 THEN SUM(ob.target_sum) / SUM(ob.total_sum)
                 ELSE 0 
            END as benchmark_value,
            NOW() as created_at,
            NOW() as updated_at
        FROM orientation_benchmarks_20251225 ob
        JOIN departments d ON ob.department_code = d.his_code AND ob.hospital_id = d.hospital_id
        WHERE ob.rule_id = 12
          AND d.accounting_unit_code IS NOT NULL
          AND ob.stat_start_date >= '2024-01-01'
          AND ob.stat_end_date <= '2024-12-31'
        GROUP BY ob.hospital_id, d.accounting_unit_code, d.accounting_unit_name
        ORDER BY d.accounting_unit_code
        """
        result = session.execute(text(consumable_ratio_sql_75))
        consumable_count_75 = result.rowcount
        print(f"  插入 {consumable_count_75} 条医生手术耗占比记录")
        session.commit()
        
        # 4. 迁移耗占比到 rule_id 77 (医生治疗耗占比)
        print("\n步骤4: 迁移耗占比实际值 (rule_id 12 → 77 医生治疗耗占比, 2024年度聚合)...")
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
            1.0 as control_intensity,
            '2024-01-01'::timestamp as stat_start_date,
            '2024-12-31'::timestamp as stat_end_date,
            CASE WHEN SUM(ob.total_sum) > 0 
                 THEN SUM(ob.target_sum) / SUM(ob.total_sum)
                 ELSE 0 
            END as benchmark_value,
            NOW() as created_at,
            NOW() as updated_at
        FROM orientation_benchmarks_20251225 ob
        JOIN departments d ON ob.department_code = d.his_code AND ob.hospital_id = d.hospital_id
        WHERE ob.rule_id = 12
          AND d.accounting_unit_code IS NOT NULL
          AND ob.stat_start_date >= '2024-01-01'
          AND ob.stat_end_date <= '2024-12-31'
        GROUP BY ob.hospital_id, d.accounting_unit_code, d.accounting_unit_name
        ORDER BY d.accounting_unit_code
        """
        result = session.execute(text(consumable_ratio_sql_77))
        consumable_count_77 = result.rowcount
        print(f"  插入 {consumable_count_77} 条医生治疗耗占比记录")
        session.commit()
        
        # 5. 验证结果
        print("\n步骤5: 验证插入结果...")
        verify_sql = """
        SELECT 
            ob.rule_id,
            r.name as rule_name,
            COUNT(*) as record_count,
            COUNT(DISTINCT ob.department_code) as dept_count,
            MIN(ob.stat_start_date) as min_date,
            MAX(ob.stat_end_date) as max_date
        FROM orientation_benchmarks ob
        JOIN orientation_rules r ON ob.rule_id = r.id
        GROUP BY ob.rule_id, r.name
        ORDER BY ob.rule_id
        """
        result = session.execute(text(verify_sql))
        rows = result.fetchall()
        
        print("\n  导向实际值统计:")
        print("  " + "-" * 100)
        print(f"  {'规则ID':<8} {'规则名称':<22} {'记录数':<10} {'科室数':<8} {'开始日期':<12} {'结束日期':<12}")
        print("  " + "-" * 100)
        for row in rows:
            min_date = row[4].strftime('%Y-%m-%d') if row[4] else '-'
            max_date = row[5].strftime('%Y-%m-%d') if row[5] else '-'
            print(f"  {row[0]:<8} {row[1]:<22} {row[2]:<10} {row[3]:<8} {min_date:<12} {max_date:<12}")
        print("  " + "-" * 100)
        
        total_count = drug_count + consumable_count_75 + consumable_count_77
        print(f"\n迁移完成! 共插入 {total_count} 条导向实际值记录")
        
        # 6. 显示部分数据样例
        print("\n数据样例:")
        sample_sql = """
        SELECT department_code, department_name, rule_id, 
               ROUND(benchmark_value::numeric, 4) as benchmark_value
        FROM orientation_benchmarks
        ORDER BY rule_id, department_code
        LIMIT 10
        """
        result = session.execute(text(sample_sql))
        rows = result.fetchall()
        
        print(f"  {'科室代码':<12} {'科室名称':<18} {'规则ID':<8} {'基准值':<10}")
        print("  " + "-" * 50)
        for row in rows:
            print(f"  {row[0]:<12} {row[1]:<18} {row[2]:<8} {row[3]:<10}")
        
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
    print("导向实际值数据迁移脚本")
    print("从 orientation_benchmarks_20251225 迁移到 orientation_benchmarks")
    print("改进：HIS科室代码 → 核算单元代码")
    print("时间范围：聚合2024年数据，每科室一条记录")
    print("=" * 60)
    print()
    
    print("警告: 此操作将清空 orientation_benchmarks 表中的所有数据!")
    print("映射关系:")
    print("  - rule_id 10 (药占比) → rule_id 74")
    print("  - rule_id 12 (耗占比) → rule_id 75, 77")
    print("算法: benchmark_value = sum(target_sum) / sum(total_sum)")
    print()
    
    response = input("确认执行? (y/N): ")
    if response.lower() != 'y':
        print("已取消")
        sys.exit(0)
    
    print()
    migrate_actual_values()
