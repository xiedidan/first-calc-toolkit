"""
调试白内障专科医生诊断-治疗手术的金额问题 - 第三部分
检查白内障手术项目的映射情况
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

period = '2025-10'

# 1. 检查白内障相关的收费项目
print("=" * 80)
print("白内障相关的收费项目：")
print("=" * 80)
result = db.execute(text("""
    SELECT ci.item_code, ci.item_name
    FROM charge_items ci
    WHERE ci.hospital_id = 1
      AND ci.item_name LIKE '%白内障%'
    ORDER BY ci.item_name
"""))
rows = list(result)
print(f"找到 {len(rows)} 个白内障相关项目")
for row in rows:
    print(f"  {row.item_code} ({row.item_name})")

# 2. 检查这些白内障项目的映射情况
print("\n" + "=" * 80)
print("白内障项目的映射情况：")
print("=" * 80)
result = db.execute(text("""
    SELECT ci.item_code, ci.item_name, dim.dimension_code, mn.name as node_name
    FROM charge_items ci
    LEFT JOIN dimension_item_mappings dim ON dim.item_code = ci.item_code AND dim.hospital_id = ci.hospital_id
    LEFT JOIN model_nodes mn ON mn.code = dim.dimension_code
    WHERE ci.hospital_id = 1
      AND ci.item_name LIKE '%白内障%'
    ORDER BY ci.item_name
"""))
rows = list(result)
for row in rows:
    mapped = f"-> {row.dimension_code} ({row.node_name})" if row.dimension_code else "【未映射】"
    print(f"  {row.item_code} ({row.item_name}) {mapped}")

# 3. 检查白内障专科开单的高金额项目的映射
print("\n" + "=" * 80)
print("白内障专科开单的高金额项目及其映射：")
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
    GROUP BY cd.item_code, cd.item_name, dim.dimension_code, mn.name
    ORDER BY total_amount DESC
    LIMIT 50
"""), {"period": period})
rows = list(result)
for row in rows:
    mapped = f"-> {row.dimension_code} ({row.node_name})" if row.dimension_code else "【未映射】"
    print(f"  {row.item_code} ({row.item_name}): 金额={row.total_amount} {mapped}")

# 4. 检查医生诊断-治疗手术维度是否包含白内障相关项目
print("\n" + "=" * 80)
print("医生诊断-治疗手术维度的映射项目中是否有白内障相关：")
print("=" * 80)
result = db.execute(text("""
    SELECT dim.item_code, ci.item_name, dim.dimension_code
    FROM dimension_item_mappings dim
    JOIN charge_items ci ON ci.item_code = dim.item_code AND ci.hospital_id = dim.hospital_id
    JOIN model_nodes mn ON mn.code = dim.dimension_code
    WHERE mn.name = '治疗手术' AND dim.dimension_code LIKE 'dim-doc%'
      AND dim.hospital_id = 1
      AND ci.item_name LIKE '%白内障%'
"""))
rows = list(result)
print(f"找到 {len(rows)} 个白内障相关映射")
for row in rows:
    print(f"  {row.item_code} ({row.item_name}) -> {row.dimension_code}")

# 5. 检查白内障手术项目映射到了哪个维度
print("\n" + "=" * 80)
print("白内障手术项目映射到的维度：")
print("=" * 80)
result = db.execute(text("""
    SELECT ci.item_code, ci.item_name, dim.dimension_code, mn.name as node_name,
           mn.node_type, p.name as parent_name
    FROM charge_items ci
    JOIN dimension_item_mappings dim ON dim.item_code = ci.item_code AND dim.hospital_id = ci.hospital_id
    JOIN model_nodes mn ON mn.code = dim.dimension_code
    LEFT JOIN model_nodes p ON p.id = mn.parent_id
    WHERE ci.hospital_id = 1
      AND (ci.item_name LIKE '%白内障%' OR ci.item_name LIKE '%晶体%' OR ci.item_name LIKE '%人工晶体%')
    ORDER BY ci.item_name
"""))
rows = list(result)
print(f"找到 {len(rows)} 个映射")
for row in rows:
    print(f"  {row.item_code} ({row.item_name})")
    print(f"    -> {row.dimension_code} ({row.node_name}) [父: {row.parent_name}]")

# 6. 检查白内障专科开单的手术项目
print("\n" + "=" * 80)
print("白内障专科开单的手术项目（名称含'术'）：")
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
      AND cd.item_name LIKE '%术%'
    GROUP BY cd.item_code, cd.item_name, dim.dimension_code, mn.name
    ORDER BY total_amount DESC
    LIMIT 30
"""), {"period": period})
rows = list(result)
for row in rows:
    mapped = f"-> {row.dimension_code} ({row.node_name})" if row.dimension_code else "【未映射】"
    print(f"  {row.item_code} ({row.item_name}): 金额={row.total_amount} {mapped}")

db.close()
