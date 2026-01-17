"""
调试白内障专科医生诊断-治疗手术的金额问题 - 第四部分
检查白内障专科开单的收费明细中是否有白内障手术项目
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

# 1. 检查白内障专科开单的收费明细中是否有白内障手术项目
print("=" * 80)
print("白内障专科开单的收费明细中是否有白内障手术项目：")
print("=" * 80)
result = db.execute(text("""
    SELECT 
        cd.item_code,
        cd.item_name,
        cd.prescribing_dept_code,
        cd.executing_dept_code,
        COUNT(*) as cnt,
        SUM(cd.amount) as total_amount
    FROM charge_details cd
    WHERE cd.year_month = :period
      AND cd.item_name LIKE '%白内障%'
    GROUP BY cd.item_code, cd.item_name, cd.prescribing_dept_code, cd.executing_dept_code
    ORDER BY total_amount DESC
"""), {"period": period})
rows = list(result)
print(f"找到 {len(rows)} 条白内障相关收费记录")
for row in rows:
    print(f"  {row.item_code} ({row.item_name})")
    print(f"    开单: {row.prescribing_dept_code}, 执行: {row.executing_dept_code}")
    print(f"    数量: {row.cnt}, 金额: {row.total_amount}")
    print()

# 2. 检查白内障手术项目的开单科室分布
print("\n" + "=" * 80)
print("白内障手术项目的开单科室分布：")
print("=" * 80)
result = db.execute(text("""
    SELECT 
        cd.prescribing_dept_code,
        d.his_name,
        d.accounting_unit_code,
        d.accounting_unit_name,
        COUNT(*) as cnt,
        SUM(cd.amount) as total_amount
    FROM charge_details cd
    LEFT JOIN departments d ON d.his_code = cd.prescribing_dept_code AND d.hospital_id = 1
    WHERE cd.year_month = :period
      AND cd.item_name LIKE '%白内障%手术%'
    GROUP BY cd.prescribing_dept_code, d.his_name, d.accounting_unit_code, d.accounting_unit_name
    ORDER BY total_amount DESC
"""), {"period": period})
rows = list(result)
print(f"找到 {len(rows)} 个开单科室")
for row in rows:
    print(f"  开单科室: {row.prescribing_dept_code} ({row.his_name})")
    print(f"    核算单元: {row.accounting_unit_code} ({row.accounting_unit_name})")
    print(f"    数量: {row.cnt}, 金额: {row.total_amount}")
    print()

# 3. 检查白内障专科(YS01/134)开单的所有收费项目中是否有手术
print("\n" + "=" * 80)
print("白内障专科(YS01/134)开单的所有收费项目中是否有手术：")
print("=" * 80)
result = db.execute(text("""
    SELECT 
        cd.item_code,
        cd.item_name,
        COUNT(*) as cnt,
        SUM(cd.amount) as total_amount
    FROM charge_details cd
    WHERE cd.year_month = :period
      AND cd.prescribing_dept_code IN ('YS01', '134')
      AND cd.item_name LIKE '%手术%'
    GROUP BY cd.item_code, cd.item_name
    ORDER BY total_amount DESC
"""), {"period": period})
rows = list(result)
print(f"找到 {len(rows)} 个手术相关项目")
total = 0
for row in rows:
    print(f"  {row.item_code} ({row.item_name}): 数量={row.cnt}, 金额={row.total_amount}")
    total += float(row.total_amount)
print(f"\n手术项目总金额: {total}")

# 4. 检查白内障专科(YS01/134)开单的所有收费项目中是否有白内障相关
print("\n" + "=" * 80)
print("白内障专科(YS01/134)开单的所有收费项目中是否有白内障相关：")
print("=" * 80)
result = db.execute(text("""
    SELECT 
        cd.item_code,
        cd.item_name,
        COUNT(*) as cnt,
        SUM(cd.amount) as total_amount
    FROM charge_details cd
    WHERE cd.year_month = :period
      AND cd.prescribing_dept_code IN ('YS01', '134')
      AND cd.item_name LIKE '%白内障%'
    GROUP BY cd.item_code, cd.item_name
    ORDER BY total_amount DESC
"""), {"period": period})
rows = list(result)
print(f"找到 {len(rows)} 个白内障相关项目")
for row in rows:
    print(f"  {row.item_code} ({row.item_name}): 数量={row.cnt}, 金额={row.total_amount}")

# 5. 检查白内障手术项目的执行科室分布
print("\n" + "=" * 80)
print("白内障手术项目的执行科室分布：")
print("=" * 80)
result = db.execute(text("""
    SELECT 
        cd.executing_dept_code,
        d.his_name,
        d.accounting_unit_code,
        d.accounting_unit_name,
        COUNT(*) as cnt,
        SUM(cd.amount) as total_amount
    FROM charge_details cd
    LEFT JOIN departments d ON d.his_code = cd.executing_dept_code AND d.hospital_id = 1
    WHERE cd.year_month = :period
      AND cd.item_name LIKE '%白内障%手术%'
    GROUP BY cd.executing_dept_code, d.his_name, d.accounting_unit_code, d.accounting_unit_name
    ORDER BY total_amount DESC
"""), {"period": period})
rows = list(result)
print(f"找到 {len(rows)} 个执行科室")
for row in rows:
    print(f"  执行科室: {row.executing_dept_code} ({row.his_name})")
    print(f"    核算单元: {row.accounting_unit_code} ({row.accounting_unit_name})")
    print(f"    数量: {row.cnt}, 金额: {row.total_amount}")
    print()

# 6. 检查白内障专科(YS01/134)作为执行科室的收费项目
print("\n" + "=" * 80)
print("白内障专科(YS01/134)作为执行科室的收费项目：")
print("=" * 80)
result = db.execute(text("""
    SELECT 
        cd.item_code,
        cd.item_name,
        cd.prescribing_dept_code,
        COUNT(*) as cnt,
        SUM(cd.amount) as total_amount
    FROM charge_details cd
    WHERE cd.year_month = :period
      AND cd.executing_dept_code IN ('YS01', '134')
    GROUP BY cd.item_code, cd.item_name, cd.prescribing_dept_code
    ORDER BY total_amount DESC
    LIMIT 30
"""), {"period": period})
rows = list(result)
print(f"找到 {len(rows)} 个项目")
for row in rows:
    print(f"  {row.item_code} ({row.item_name})")
    print(f"    开单科室: {row.prescribing_dept_code}, 数量: {row.cnt}, 金额: {row.total_amount}")

db.close()
