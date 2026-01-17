"""
调试白内障专科医生诊断-治疗手术的金额问题 - 第二部分
"""
import os
import sys
sys.path.insert(0, 'backend')

from dotenv import load_dotenv
load_dotenv('backend/.env')

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

DATABASE_URL = os.getenv('DATABASE_URL')
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
db = Session()

task_id = '0795b9cf-3b58-44b2-8bf1-0be573a0ac2f'
period = '2025-10'
dept_id = 4  # 白内障专科

# 1. 检查医生诊断-治疗手术维度的映射
print("=" * 80)
print("dimension_item_mappings - 医生诊断-治疗手术维度的映射：")
print("=" * 80)
result = db.execute(text("""
    SELECT dim.item_code, ci.item_name, dim.dimension_code, mn.name as node_name
    FROM dimension_item_mappings dim
    JOIN charge_items ci ON ci.item_code = dim.item_code AND ci.hospital_id = dim.hospital_id
    JOIN model_nodes mn ON mn.code = dim.dimension_code
    WHERE mn.name = '治疗手术' AND dim.dimension_code LIKE 'dim-doc%'
      AND dim.hospital_id = 1
    LIMIT 30
"""))
rows = list(result)
print(f"找到 {len(rows)} 个映射")
for row in rows:
    print(f"  {row.item_code} ({row.item_name}) -> {row.dimension_code} ({row.node_name})")

# 2. 检查白内障专科开单项目与治疗手术映射的交集
print("\n" + "=" * 80)
print("白内障专科开单项目与医生诊断-治疗手术映射的交集：")
print("=" * 80)
result = db.execute(text("""
    SELECT 
        cd.item_code,
        cd.item_name,
        dim.dimension_code,
        mn.name as node_name,
        COUNT(*) as cnt,
        SUM(cd.amount) as total_amount
    FROM charge_details cd
    JOIN dimension_item_mappings dim ON dim.item_code = cd.item_code AND dim.hospital_id = 1
    JOIN model_nodes mn ON mn.code = dim.dimension_code
    WHERE cd.year_month = :period
      AND cd.prescribing_dept_code IN ('YS01', '134')
      AND mn.name = '治疗手术'
      AND dim.dimension_code LIKE 'dim-doc%'
    GROUP BY cd.item_code, cd.item_name, dim.dimension_code, mn.name
    ORDER BY total_amount DESC
"""), {"period": period})
rows = list(result)
print(f"找到 {len(rows)} 个匹配")
total = 0
for row in rows:
    print(f"  {row.item_code} ({row.item_name})")
    print(f"    -> {row.dimension_code} ({row.node_name}): 数量={row.cnt}, 金额={row.total_amount}")
    total += float(row.total_amount)
print(f"\n总金额: {total}")

# 3. 对比：检查执行维度的数据
print("\n" + "=" * 80)
print("对比：白内障专科执行科室的治疗手术数据（执行维度）：")
print("=" * 80)
result = db.execute(text("""
    SELECT 
        cd.executing_dept_code,
        dim.dimension_code,
        mn.name as node_name,
        COUNT(*) as cnt,
        SUM(cd.amount) as total_amount
    FROM charge_details cd
    JOIN dimension_item_mappings dim ON dim.item_code = cd.item_code AND dim.hospital_id = 1
    JOIN model_nodes mn ON mn.code = dim.dimension_code
    WHERE cd.year_month = :period
      AND cd.executing_dept_code IN ('YS01', '134')
      AND mn.name LIKE '%治疗手术%'
    GROUP BY cd.executing_dept_code, dim.dimension_code, mn.name
    ORDER BY total_amount DESC
"""), {"period": period})
rows = list(result)
print(f"找到 {len(rows)} 个匹配")
total = 0
for row in rows:
    print(f"  执行科室: {row.executing_dept_code}")
    print(f"    -> {row.dimension_code} ({row.node_name}): 数量={row.cnt}, 金额={row.total_amount}")
    total += float(row.total_amount)
print(f"\n总金额: {total}")

# 4. 检查白内障专科的手术相关收费项目的映射情况
print("\n" + "=" * 80)
print("白内障专科手术项目的映射情况：")
print("=" * 80)
result = db.execute(text("""
    SELECT 
        cd.item_code,
        cd.item_name,
        dim.dimension_code,
        mn.name as node_name,
        SUM(cd.amount) as total_amount
    FROM charge_details cd
    LEFT JOIN dimension_item_mappings dim ON dim.item_code = cd.item_code AND dim.hospital_id = 1
    LEFT JOIN model_nodes mn ON mn.code = dim.dimension_code
    WHERE cd.year_month = :period
      AND cd.prescribing_dept_code IN ('YS01', '134')
      AND (cd.item_name LIKE '%手术%' OR cd.item_name LIKE '%白内障%')
    GROUP BY cd.item_code, cd.item_name, dim.dimension_code, mn.name
    ORDER BY total_amount DESC
    LIMIT 30
"""), {"period": period})
rows = list(result)
for row in rows:
    mapped = f"-> {row.dimension_code} ({row.node_name})" if row.dimension_code else "【未映射】"
    print(f"  {row.item_code} ({row.item_name}): 金额={row.total_amount} {mapped}")

# 5. 检查医生诊断-治疗手术维度的所有映射项目
print("\n" + "=" * 80)
print("医生诊断-治疗手术维度的所有映射项目：")
print("=" * 80)
result = db.execute(text("""
    SELECT dim.item_code, ci.item_name, dim.dimension_code
    FROM dimension_item_mappings dim
    JOIN charge_items ci ON ci.item_code = dim.item_code AND ci.hospital_id = dim.hospital_id
    JOIN model_nodes mn ON mn.code = dim.dimension_code
    WHERE mn.name = '治疗手术' AND dim.dimension_code LIKE 'dim-doc%'
      AND dim.hospital_id = 1
    ORDER BY ci.item_name
"""))
rows = list(result)
print(f"共 {len(rows)} 个映射项目")
for row in rows:
    print(f"  {row.item_code} ({row.item_name}) -> {row.dimension_code}")

# 6. 检查白内障专科开单的所有项目中有多少被映射
print("\n" + "=" * 80)
print("白内障专科开单项目的映射覆盖率：")
print("=" * 80)
result = db.execute(text("""
    WITH dept_items AS (
        SELECT DISTINCT cd.item_code, cd.item_name
        FROM charge_details cd
        WHERE cd.year_month = :period
          AND cd.prescribing_dept_code IN ('YS01', '134')
    )
    SELECT 
        COUNT(*) as total_items,
        COUNT(dim.item_code) as mapped_items
    FROM dept_items di
    LEFT JOIN dimension_item_mappings dim ON dim.item_code = di.item_code AND dim.hospital_id = 1
"""), {"period": period})
row = result.fetchone()
print(f"  总项目数: {row.total_items}")
print(f"  已映射项目数: {row.mapped_items}")
print(f"  覆盖率: {row.mapped_items / row.total_items * 100:.1f}%")

# 7. 检查未映射的高金额项目
print("\n" + "=" * 80)
print("白内障专科未映射的高金额项目 TOP 20：")
print("=" * 80)
result = db.execute(text("""
    SELECT 
        cd.item_code,
        cd.item_name,
        COUNT(*) as cnt,
        SUM(cd.amount) as total_amount
    FROM charge_details cd
    LEFT JOIN dimension_item_mappings dim ON dim.item_code = cd.item_code AND dim.hospital_id = 1
    WHERE cd.year_month = :period
      AND cd.prescribing_dept_code IN ('YS01', '134')
      AND dim.item_code IS NULL
    GROUP BY cd.item_code, cd.item_name
    ORDER BY total_amount DESC
    LIMIT 20
"""), {"period": period})
rows = list(result)
total_unmapped = 0
for row in rows:
    print(f"  {row.item_code} ({row.item_name}): 数量={row.cnt}, 金额={row.total_amount}")
    total_unmapped += float(row.total_amount)
print(f"\n未映射项目总金额: {total_unmapped}")

db.close()
