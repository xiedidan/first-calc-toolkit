"""
测试下钻修复：验证手术维度使用执行科室
"""
import os
import sys
sys.path.insert(0, 'backend')

from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv('backend/.env')

DATABASE_URL = os.getenv('DATABASE_URL')
engine = create_engine(DATABASE_URL)

# 测试参数
dimension_code = 'dim-doc-sur-in-1'  # 丁级手术（住院）
period = '2025-10'

# 导入判断函数
from app.api.analysis_reports import is_diagnosis_dimension, get_business_type_from_dimension_code

print("=" * 60)
print("测试下钻修复")
print("=" * 60)

# 1. 测试判断函数
print("\n1. 测试判断函数")
print("-" * 40)

test_codes = [
    'dim-doc-sur-in-1',      # 住院手术 -> 执行科室
    'dim-doc-sur-out-2',     # 门诊手术 -> 执行科室
    'dim-doc-in-eval-exam',  # 诊断(检查化验) -> 开单科室
    'dim-doc-out-eval-drug', # 诊断(中草药) -> 开单科室
    'dim-doc-in-diag-norm',  # 诊察 -> 执行科室
    'dim-tech-lab',          # 医技 -> 执行科室
    'dim-nur-base',          # 护理 -> 执行科室
]

for code in test_codes:
    is_diag = is_diagnosis_dimension(code)
    dept_field = "prescribing_dept_code" if is_diag else "executing_dept_code"
    business_type = get_business_type_from_dimension_code(code)
    print(f"  {code:30} -> {dept_field:25} | 业务类型: {business_type or '不区分'}")

# 2. 模拟下钻查询
print("\n2. 模拟下钻查询（住院手术维度）")
print("-" * 40)

with engine.connect() as conn:
    # 获取维度映射
    result = conn.execute(text("""
        SELECT item_code FROM dimension_item_mappings
        WHERE dimension_code = :dimension_code
    """), {"dimension_code": dimension_code})
    item_codes = [row[0] for row in result]
    print(f"  维度: {dimension_code}")
    print(f"  映射项目数: {len(item_codes)}")
    
    # 判断使用哪个科室字段
    use_prescribing = is_diagnosis_dimension(dimension_code)
    dept_field = "prescribing_dept_code" if use_prescribing else "executing_dept_code"
    business_type = get_business_type_from_dimension_code(dimension_code)
    print(f"  使用科室字段: {dept_field}")
    print(f"  业务类型: {business_type}")
    
    # 获取有数据的科室
    result = conn.execute(text(f"""
        SELECT {dept_field}, COUNT(*) as count, SUM(amount) as total
        FROM charge_details
        WHERE TO_CHAR(charge_time, 'YYYY-MM') = :period
        AND item_code = ANY(:item_codes)
        AND business_type = :business_type
        AND {dept_field} IS NOT NULL
        AND {dept_field} != ''
        GROUP BY {dept_field}
        ORDER BY total DESC
        LIMIT 5
    """), {"period": period, "item_codes": item_codes, "business_type": business_type})
    
    rows = result.fetchall()
    print(f"\n  有数据的科室 (Top 5):")
    for row in rows:
        print(f"    {row[0]}: {row[1]} 条, 金额 {row[2]}")
    
    if rows:
        # 使用第一个科室测试下钻
        test_dept_code = rows[0][0]
        print(f"\n  测试科室: {test_dept_code}")
        
        result = conn.execute(text(f"""
            SELECT 
                item_code,
                item_name,
                SUM(amount) as total_amount,
                SUM(quantity) as total_quantity
            FROM charge_details
            WHERE {dept_field} = :dept_code
            AND TO_CHAR(charge_time, 'YYYY-MM') = :period
            AND item_code = ANY(:item_codes)
            AND business_type = :business_type
            GROUP BY item_code, item_name
            ORDER BY total_amount DESC
        """), {
            "dept_code": test_dept_code,
            "period": period,
            "item_codes": item_codes,
            "business_type": business_type
        })
        
        drilldown_rows = result.fetchall()
        print(f"\n  下钻结果: {len(drilldown_rows)} 条")
        for row in drilldown_rows[:5]:
            print(f"    {row[0]} {row[1]}: 金额 {row[2]}, 数量 {row[3]}")

# 3. 对比测试：诊断维度
print("\n3. 对比测试（诊断维度）")
print("-" * 40)

diag_dimension_code = 'dim-doc-in-eval-exam'  # 检查化验

with engine.connect() as conn:
    result = conn.execute(text("""
        SELECT item_code FROM dimension_item_mappings
        WHERE dimension_code = :dimension_code
    """), {"dimension_code": diag_dimension_code})
    diag_item_codes = [row[0] for row in result]
    
    use_prescribing = is_diagnosis_dimension(diag_dimension_code)
    dept_field = "prescribing_dept_code" if use_prescribing else "executing_dept_code"
    business_type = get_business_type_from_dimension_code(diag_dimension_code)
    
    print(f"  维度: {diag_dimension_code}")
    print(f"  映射项目数: {len(diag_item_codes)}")
    print(f"  使用科室字段: {dept_field}")
    print(f"  业务类型: {business_type}")
    
    if diag_item_codes:
        result = conn.execute(text(f"""
            SELECT {dept_field}, COUNT(*) as count, SUM(amount) as total
            FROM charge_details
            WHERE TO_CHAR(charge_time, 'YYYY-MM') = :period
            AND item_code = ANY(:item_codes)
            AND business_type = :business_type
            AND {dept_field} IS NOT NULL
            AND {dept_field} != ''
            GROUP BY {dept_field}
            ORDER BY total DESC
            LIMIT 5
        """), {"period": period, "item_codes": diag_item_codes, "business_type": business_type})
        
        rows = result.fetchall()
        print(f"\n  有数据的科室 (Top 5):")
        for row in rows:
            print(f"    {row[0]}: {row[1]} 条, 金额 {row[2]}")

print("\n" + "=" * 60)
print("测试完成")
print("=" * 60)
