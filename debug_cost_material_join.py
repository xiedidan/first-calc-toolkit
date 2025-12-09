"""
调试成本维度计算的JOIN条件
"""
import psycopg2

conn = psycopg2.connect(
    host="47.108.227.254",
    port=50016,
    user="root",
    password="root",
    database="hospital_value"
)

cursor = conn.cursor()

print("1. 检查 cost_values 中的材料费和折旧费数据...")
cursor.execute("""
    SELECT dimension_code, dimension_name, dept_code, COUNT(*) 
    FROM cost_values 
    WHERE hospital_id = 1 
      AND year_month = '2025-10'
      AND dimension_code IN (
          'dim-doc-cost-mat', 'dim-nur-cost-mat', 'dim-tech-cost-mat',
          'dim-doc-cost-depr', 'dim-nur-cost-depr', 'dim-tech-cost-depr'
      )
    GROUP BY dimension_code, dimension_name, dept_code
    ORDER BY dept_code, dimension_code
    LIMIT 10
""")
print(f"   找到 {cursor.rowcount} 条记录")
for row in cursor.fetchall():
    print(f"   {row[0]:<25} {row[1]:<20} {row[2]:<15} {row[3]}")

print("\n2. 检查 departments 表中的核算单元代码...")
cursor.execute("""
    SELECT his_code, accounting_unit_code, his_name
    FROM departments
    WHERE hospital_id = 1 AND is_active = TRUE
    ORDER BY his_code
    LIMIT 10
""")
print(f"   {'HIS代码':<15} {'核算单元代码':<20} {'科室名称'}")
for row in cursor.fetchall():
    print(f"   {row[0]:<15} {row[1] or 'NULL':<20} {row[2]}")

print("\n3. 检查 cost_values + departments 的匹配...")
cursor.execute("""
    SELECT cv.dept_code, d.his_code, d.accounting_unit_code, d.his_name, COUNT(*)
    FROM cost_values cv
    JOIN departments d ON 
        cv.dept_code = d.accounting_unit_code 
        AND d.hospital_id = 1
        AND d.is_active = TRUE
    WHERE cv.hospital_id = 1
      AND cv.year_month = '2025-10'
      AND cv.dimension_code IN (
          'dim-doc-cost-mat', 'dim-nur-cost-mat', 'dim-tech-cost-mat',
          'dim-doc-cost-depr', 'dim-nur-cost-depr', 'dim-tech-cost-depr'
      )
    GROUP BY cv.dept_code, d.his_code, d.accounting_unit_code, d.his_name
    LIMIT 10
""")
count = cursor.rowcount
print(f"   匹配到 {count} 条")
if count > 0:
    for row in cursor.fetchall():
        print(f"   {row[0]:<15} {row[1]:<15} {row[2]:<20} {row[3]}")

print("\n4. 检查 + department_revenues 的匹配...")
cursor.execute("""
    SELECT cv.dept_code, d.his_code, dr.department_code, COUNT(*)
    FROM cost_values cv
    JOIN departments d ON 
        cv.dept_code = d.accounting_unit_code 
        AND d.hospital_id = 1
        AND d.is_active = TRUE
    JOIN department_revenues dr ON
        dr.hospital_id = 1
        AND dr.year_month = '2025-10'
        AND dr.department_code = d.his_code
    WHERE cv.hospital_id = 1
      AND cv.year_month = '2025-10'
      AND cv.dimension_code IN (
          'dim-doc-cost-mat', 'dim-nur-cost-mat', 'dim-tech-cost-mat',
          'dim-doc-cost-depr', 'dim-nur-cost-depr', 'dim-tech-cost-depr'
      )
    GROUP BY cv.dept_code, d.his_code, dr.department_code
    LIMIT 10
""")
count = cursor.rowcount
print(f"   匹配到 {count} 条")

print("\n5. 检查 cost_benchmarks 中的数据...")
cursor.execute("""
    SELECT department_code, dimension_code, COUNT(*)
    FROM cost_benchmarks
    WHERE hospital_id = 1
      AND version_id = 23
      AND dimension_code IN (
          'dim-doc-cost-mat', 'dim-nur-cost-mat', 'dim-tech-cost-mat',
          'dim-doc-cost-depr', 'dim-nur-cost-depr', 'dim-tech-cost-depr'
      )
    GROUP BY department_code, dimension_code
    ORDER BY department_code, dimension_code
    LIMIT 10
""")
print(f"   找到 {cursor.rowcount} 条记录")
for row in cursor.fetchall():
    print(f"   {row[0]:<20} {row[1]:<25} {row[2]}")

cursor.close()
conn.close()
