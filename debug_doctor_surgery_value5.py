"""
调试白内障专科医生诊断-治疗手术的金额问题 - 第五部分
确认开单科室为空的问题范围
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

# 1. 统计开单科室为空的收费明细数量和金额
print("=" * 80)
print("开单科室为空的收费明细统计：")
print("=" * 80)
result = db.execute(text("""
    SELECT 
        COUNT(*) as cnt,
        SUM(amount) as total_amount
    FROM charge_details
    WHERE year_month = :period
      AND (prescribing_dept_code IS NULL OR prescribing_dept_code = '')
"""), {"period": period})
row = result.fetchone()
print(f"开单科室为空的记录数: {row.cnt}")
print(f"开单科室为空的总金额: {row.total_amount}")

# 2. 统计所有收费明细数量和金额
result = db.execute(text("""
    SELECT 
        COUNT(*) as cnt,
        SUM(amount) as total_amount
    FROM charge_details
    WHERE year_month = :period
"""), {"period": period})
row2 = result.fetchone()
print(f"\n所有记录数: {row2.cnt}")
print(f"所有总金额: {row2.total_amount}")
print(f"\n开单科室为空的占比: {float(row.cnt)/float(row2.cnt)*100:.2f}%")
print(f"开单科室为空的金额占比: {float(row.total_amount)/float(row2.total_amount)*100:.2f}%")

# 3. 开单科室为空但执行科室不为空的记录
print("\n" + "=" * 80)
print("开单科室为空但执行科室不为空的记录（按执行科室分组）：")
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
      AND (cd.prescribing_dept_code IS NULL OR cd.prescribing_dept_code = '')
      AND cd.executing_dept_code IS NOT NULL AND cd.executing_dept_code != ''
    GROUP BY cd.executing_dept_code, d.his_name, d.accounting_unit_code, d.accounting_unit_name
    ORDER BY total_amount DESC
    LIMIT 20
"""), {"period": period})
rows = list(result)
print(f"找到 {len(rows)} 个执行科室")
for row in rows:
    print(f"  执行科室: {row.executing_dept_code} ({row.his_name})")
    print(f"    核算单元: {row.accounting_unit_code} ({row.accounting_unit_name})")
    print(f"    数量: {row.cnt}, 金额: {row.total_amount}")
    print()

# 4. 开单科室为空的收费项目类型分布
print("\n" + "=" * 80)
print("开单科室为空的收费项目类型分布（按金额排序）：")
print("=" * 80)
result = db.execute(text("""
    SELECT 
        item_code,
        item_name,
        COUNT(*) as cnt,
        SUM(amount) as total_amount
    FROM charge_details
    WHERE year_month = :period
      AND (prescribing_dept_code IS NULL OR prescribing_dept_code = '')
    GROUP BY item_code, item_name
    ORDER BY total_amount DESC
    LIMIT 30
"""), {"period": period})
rows = list(result)
print(f"找到 {len(rows)} 个项目类型")
for row in rows:
    print(f"  {row.item_code} ({row.item_name}): 数量={row.cnt}, 金额={row.total_amount}")

# 5. 检查这些开单科室为空的记录在源表中的情况
print("\n" + "=" * 80)
print("检查源表中开单科室字段的情况：")
print("=" * 80)

# 检查门诊源表
result = db.execute(text("""
    SELECT 
        COUNT(*) as cnt,
        SUM(CAST("MXXMSSJE" AS NUMERIC)) as total_amount
    FROM "TB_MZ_SFMXB"
    WHERE TO_CHAR("FYFSSJ", 'YYYY-MM') = :period
      AND ("KDKSBM" IS NULL OR "KDKSBM" = '')
"""), {"period": period})
row = result.fetchone()
print(f"门诊源表开单科室为空的记录数: {row.cnt}")
print(f"门诊源表开单科室为空的总金额: {row.total_amount}")

# 检查住院源表
result = db.execute(text("""
    SELECT 
        COUNT(*) as cnt,
        SUM(CAST("MXXMSSJE" AS NUMERIC)) as total_amount
    FROM "TB_ZY_SFMXB"
    WHERE TO_CHAR("FYFSSJ", 'YYYY-MM') = :period
      AND ("KDKSBM" IS NULL OR "KDKSBM" = '')
"""), {"period": period})
row = result.fetchone()
print(f"住院源表开单科室为空的记录数: {row.cnt}")
print(f"住院源表开单科室为空的总金额: {row.total_amount}")

# 6. 检查白内障手术在源表中的开单科室情况
print("\n" + "=" * 80)
print("白内障手术在源表中的开单科室情况：")
print("=" * 80)

# 门诊
result = db.execute(text("""
    SELECT 
        "KDKSBM" as prescribing_dept,
        "ZXKSBM" as executing_dept,
        COUNT(*) as cnt,
        SUM(CAST("MXXMSSJE" AS NUMERIC)) as total_amount
    FROM "TB_MZ_SFMXB"
    WHERE TO_CHAR("FYFSSJ", 'YYYY-MM') = :period
      AND "XMMC" LIKE '%白内障%'
    GROUP BY "KDKSBM", "ZXKSBM"
    ORDER BY total_amount DESC
"""), {"period": period})
rows = list(result)
print(f"门诊白内障相关记录: {len(rows)} 组")
for row in rows:
    print(f"  开单: '{row.prescribing_dept}', 执行: '{row.executing_dept}', 数量: {row.cnt}, 金额: {row.total_amount}")

# 住院
result = db.execute(text("""
    SELECT 
        "KDKSBM" as prescribing_dept,
        "ZXKSBM" as executing_dept,
        COUNT(*) as cnt,
        SUM(CAST("MXXMSSJE" AS NUMERIC)) as total_amount
    FROM "TB_ZY_SFMXB"
    WHERE TO_CHAR("FYFSSJ", 'YYYY-MM') = :period
      AND "XMMC" LIKE '%白内障%'
    GROUP BY "KDKSBM", "ZXKSBM"
    ORDER BY total_amount DESC
"""), {"period": period})
rows = list(result)
print(f"\n住院白内障相关记录: {len(rows)} 组")
for row in rows:
    print(f"  开单: '{row.prescribing_dept}', 执行: '{row.executing_dept}', 数量: {row.cnt}, 金额: {row.total_amount}")

db.close()
