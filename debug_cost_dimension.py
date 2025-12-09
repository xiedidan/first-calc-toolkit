"""
调试成本维度计算
检查为什么没有插入数据
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

print("1. 检查 cost_values 表中的数据...")
cursor.execute("""
    SELECT dimension_code, dimension_name, COUNT(*) as count
    FROM cost_values
    WHERE hospital_id = 1
      AND year_month = '2025-10'
    GROUP BY dimension_code, dimension_name
    ORDER BY dimension_code
""")

print("   cost_values 中的维度：")
for row in cursor.fetchall():
    print(f"   {row[0]:<25} {row[1]:<20} {row[2]} 条")

print("\n2. 检查 model_nodes 表中的成本维度...")
cursor.execute("""
    SELECT mn.code, mn.name, mn.weight, mv.id as version_id, mv.is_active
    FROM model_nodes mn
    JOIN model_versions mv ON mn.version_id = mv.id
    WHERE mv.hospital_id = 1
      AND mn.node_type = 'dimension'
      AND mn.code IN (
          'dim-doc-cost-hr', 'dim-nur-cost-hr', 'dim-tech-cost-hr',
          'dim-doc-cost-other', 'dim-nur-cost-other', 'dim-tech-cost-other'
      )
    ORDER BY mn.code
""")

print("   model_nodes 中的成本维度：")
for row in cursor.fetchall():
    print(f"   {row[0]:<25} {row[1]:<20} 权重:{row[2]} 版本:{row[3]} 激活:{row[4]}")

print("\n3. 检查激活的模型版本...")
cursor.execute("""
    SELECT id, name, is_active
    FROM model_versions
    WHERE hospital_id = 1
    ORDER BY id DESC
    LIMIT 5
""")

print("   模型版本：")
for row in cursor.fetchall():
    print(f"   ID:{row[0]:<5} {row[1]:<40} 激活:{row[2]}")

print("\n4. 测试 JOIN 条件...")
cursor.execute("""
    SELECT 
        cv.dimension_code,
        cv.dimension_name,
        cv.dept_code,
        d.id as dept_id,
        mn.id as node_id,
        mn.name as node_name,
        mv.id as version_id,
        mv.is_active
    FROM cost_values cv
    JOIN departments d ON 
        cv.dept_code = d.his_code 
        AND d.hospital_id = 1
        AND d.is_active = TRUE
    JOIN model_nodes mn ON 
        cv.dimension_code = mn.code 
        AND mn.node_type = 'dimension'
    JOIN model_versions mv ON 
        mn.version_id = mv.id
        AND mv.hospital_id = 1
        AND mv.is_active = TRUE
    WHERE cv.hospital_id = 1
        AND cv.year_month = '2025-10'
        AND cv.dimension_code IN (
            'dim-doc-cost-hr', 'dim-nur-cost-hr', 'dim-tech-cost-hr',
            'dim-doc-cost-other', 'dim-nur-cost-other', 'dim-tech-cost-other'
        )
    LIMIT 5
""")

results = cursor.fetchall()
print(f"   JOIN 结果：{len(results)} 条")
if results:
    print(f"   {'维度代码':<25} {'维度名称':<20} {'科室代码':<15} {'节点ID':<10} {'版本ID':<10}")
    for row in results:
        print(f"   {row[0]:<25} {row[1]:<20} {row[2]:<15} {row[4]:<10} {row[6]:<10}")
else:
    print("   ⚠ 没有匹配的数据！")
    
    # 分步检查
    print("\n   分步检查：")
    
    # 检查 cost_values + departments
    cursor.execute("""
        SELECT COUNT(*)
        FROM cost_values cv
        JOIN departments d ON 
            cv.dept_code = d.his_code 
            AND d.hospital_id = 1
            AND d.is_active = TRUE
        WHERE cv.hospital_id = 1
            AND cv.year_month = '2025-10'
            AND cv.dimension_code IN (
                'dim-doc-cost-hr', 'dim-nur-cost-hr', 'dim-tech-cost-hr',
                'dim-doc-cost-other', 'dim-nur-cost-other', 'dim-tech-cost-other'
            )
    """)
    count1 = cursor.fetchone()[0]
    print(f"   cost_values + departments: {count1} 条")
    
    # 检查 + model_nodes
    cursor.execute("""
        SELECT COUNT(*)
        FROM cost_values cv
        JOIN departments d ON 
            cv.dept_code = d.his_code 
            AND d.hospital_id = 1
            AND d.is_active = TRUE
        JOIN model_nodes mn ON 
            cv.dimension_code = mn.code 
            AND mn.node_type = 'dimension'
        WHERE cv.hospital_id = 1
            AND cv.year_month = '2025-10'
            AND cv.dimension_code IN (
                'dim-doc-cost-hr', 'dim-nur-cost-hr', 'dim-tech-cost-hr',
                'dim-doc-cost-other', 'dim-nur-cost-other', 'dim-tech-cost-other'
            )
    """)
    count2 = cursor.fetchone()[0]
    print(f"   + model_nodes: {count2} 条")
    
    # 检查 + model_versions (is_active = TRUE)
    cursor.execute("""
        SELECT COUNT(*)
        FROM cost_values cv
        JOIN departments d ON 
            cv.dept_code = d.his_code 
            AND d.hospital_id = 1
            AND d.is_active = TRUE
        JOIN model_nodes mn ON 
            cv.dimension_code = mn.code 
            AND mn.node_type = 'dimension'
        JOIN model_versions mv ON 
            mn.version_id = mv.id
            AND mv.hospital_id = 1
            AND mv.is_active = TRUE
        WHERE cv.hospital_id = 1
            AND cv.year_month = '2025-10'
            AND cv.dimension_code IN (
                'dim-doc-cost-hr', 'dim-nur-cost-hr', 'dim-tech-cost-hr',
                'dim-doc-cost-other', 'dim-nur-cost-other', 'dim-tech-cost-other'
            )
    """)
    count3 = cursor.fetchone()[0]
    print(f"   + model_versions (is_active=TRUE): {count3} 条")

cursor.close()
conn.close()
