"""
从 orientation_benchmarks_20251225 表迁移每月实际值到 orientation_values 表。

功能：
1. 将HIS科室代码转换为核算单元代码
2. 迁移所有月份的实际值数据（有多少插入多少）
3. 每个科室每月一条记录

映射关系（与基准迁移一致）：
- orientation_benchmarks_20251225.rule_id 10 (药占比) → orientation_values.orientation_rule_id 74
- orientation_benchmarks_20251225.rule_id 12 (耗占比) → orientation_values.orientation_rule_id 75, 77

执行前会清空 orientation_values 表中的所有数据。
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


def migrate_monthly_values():
    """迁移每月导向实际值数据"""
    session = Session()
    
    try:
        # 1. 清空 orientation_values 表
        print("步骤1: 清空 orientation_values 表...")
        result = session.execute(text("DELETE FROM orientation_values"))
        deleted_count = result.rowcount
        print(f"  已删除 {deleted_count} 条记录")
        session.commit()
        
        # 2. 迁移药占比月度数据 (rule_id 10 → 74)
        print("\n步骤2: 迁移药占比月度实际值 (rule_id 10 → 74)...")
        drug_ratio_sql = """
        INSERT INTO orientation_values (
            hospital_id, year_month, department_code, department_name,
            orientation_rule_id, actual_value, created_at, updated_at
        )
        SELECT 
            ob.hospital_id,
            TO_CHAR(ob.stat_start_date, 'YYYY-MM') as year_month,
            d.accounting_unit_code as department_code,
            d.accounting_unit_name as department_name,
            74 as orientation_rule_id,
            ob.benchmark_value as actual_value,
            NOW() as created_at,
            NOW() as updated_at
        FROM orientation_benchmarks_20251225 ob
        JOIN departments d ON ob.department_code = d.his_code AND ob.hospital_id = d.hospital_id
        WHERE ob.rule_id = 10
          AND d.accounting_unit_code IS NOT NULL
        ORDER BY d.accounting_unit_code, ob.stat_start_date
        """
        result = session.execute(text(drug_ratio_sql))
        drug_count = result.rowcount
        print(f"  插入 {drug_count} 条药占比月度记录")
        session.commit()
        
        # 3. 迁移耗占比月度数据到 rule_id 75 (医生手术耗占比)
        print("\n步骤3: 迁移耗占比月度实际值 (rule_id 12 → 75 医生手术耗占比)...")
        consumable_ratio_sql_75 = """
        INSERT INTO orientation_values (
            hospital_id, year_month, department_code, department_name,
            orientation_rule_id, actual_value, created_at, updated_at
        )
        SELECT 
            ob.hospital_id,
            TO_CHAR(ob.stat_start_date, 'YYYY-MM') as year_month,
            d.accounting_unit_code as department_code,
            d.accounting_unit_name as department_name,
            75 as orientation_rule_id,
            ob.benchmark_value as actual_value,
            NOW() as created_at,
            NOW() as updated_at
        FROM orientation_benchmarks_20251225 ob
        JOIN departments d ON ob.department_code = d.his_code AND ob.hospital_id = d.hospital_id
        WHERE ob.rule_id = 12
          AND d.accounting_unit_code IS NOT NULL
        ORDER BY d.accounting_unit_code, ob.stat_start_date
        """
        result = session.execute(text(consumable_ratio_sql_75))
        consumable_count_75 = result.rowcount
        print(f"  插入 {consumable_count_75} 条医生手术耗占比月度记录")
        session.commit()
        
        # 4. 迁移耗占比月度数据到 rule_id 77 (医生治疗耗占比)
        print("\n步骤4: 迁移耗占比月度实际值 (rule_id 12 → 77 医生治疗耗占比)...")
        consumable_ratio_sql_77 = """
        INSERT INTO orientation_values (
            hospital_id, year_month, department_code, department_name,
            orientation_rule_id, actual_value, created_at, updated_at
        )
        SELECT 
            ob.hospital_id,
            TO_CHAR(ob.stat_start_date, 'YYYY-MM') as year_month,
            d.accounting_unit_code as department_code,
            d.accounting_unit_name as department_name,
            77 as orientation_rule_id,
            ob.benchmark_value as actual_value,
            NOW() as created_at,
            NOW() as updated_at
        FROM orientation_benchmarks_20251225 ob
        JOIN departments d ON ob.department_code = d.his_code AND ob.hospital_id = d.hospital_id
        WHERE ob.rule_id = 12
          AND d.accounting_unit_code IS NOT NULL
        ORDER BY d.accounting_unit_code, ob.stat_start_date
        """
        result = session.execute(text(consumable_ratio_sql_77))
        consumable_count_77 = result.rowcount
        print(f"  插入 {consumable_count_77} 条医生治疗耗占比月度记录")
        session.commit()
        
        # 5. 验证结果
        print("\n步骤5: 验证插入结果...")
        verify_sql = """
        SELECT 
            ov.orientation_rule_id,
            r.name as rule_name,
            COUNT(*) as record_count,
            COUNT(DISTINCT ov.department_code) as dept_count,
            COUNT(DISTINCT ov.year_month) as month_count,
            MIN(ov.year_month) as min_month,
            MAX(ov.year_month) as max_month
        FROM orientation_values ov
        JOIN orientation_rules r ON ov.orientation_rule_id = r.id
        GROUP BY ov.orientation_rule_id, r.name
        ORDER BY ov.orientation_rule_id
        """
        result = session.execute(text(verify_sql))
        rows = result.fetchall()
        
        print("\n  导向月度实际值统计:")
        print("  " + "-" * 110)
        print(f"  {'规则ID':<8} {'规则名称':<22} {'记录数':<10} {'科室数':<8} {'月份数':<8} {'起始月':<10} {'结束月':<10}")
        print("  " + "-" * 110)
        for row in rows:
            print(f"  {row[0]:<8} {row[1]:<22} {row[2]:<10} {row[3]:<8} {row[4]:<8} {row[5]:<10} {row[6]:<10}")
        print("  " + "-" * 110)
        
        total_count = drug_count + consumable_count_75 + consumable_count_77
        print(f"\n迁移完成! 共插入 {total_count} 条月度实际值记录")
        
        # 6. 显示部分数据样例
        print("\n数据样例:")
        sample_sql = """
        SELECT department_code, department_name, year_month, orientation_rule_id,
               ROUND(actual_value::numeric, 4) as actual_value
        FROM orientation_values
        ORDER BY orientation_rule_id, department_code, year_month
        LIMIT 15
        """
        result = session.execute(text(sample_sql))
        rows = result.fetchall()
        
        print(f"  {'科室代码':<12} {'科室名称':<18} {'月份':<10} {'规则ID':<8} {'实际值':<10}")
        print("  " + "-" * 60)
        for row in rows:
            print(f"  {row[0]:<12} {row[1]:<18} {row[2]:<10} {row[3]:<8} {row[4]:<10}")
        
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
    print("导向月度实际值数据迁移脚本")
    print("从 orientation_benchmarks_20251225 迁移到 orientation_values")
    print("改进：HIS科室代码 → 核算单元代码")
    print("时间范围：所有月份数据")
    print("=" * 60)
    print()
    
    print("警告: 此操作将清空 orientation_values 表中的所有数据!")
    print("映射关系:")
    print("  - rule_id 10 (药占比) → orientation_rule_id 74")
    print("  - rule_id 12 (耗占比) → orientation_rule_id 75, 77")
    print()
    
    response = input("确认执行? (y/N): ")
    if response.lower() != 'y':
        print("已取消")
        sys.exit(0)
    
    print()
    migrate_monthly_values()
