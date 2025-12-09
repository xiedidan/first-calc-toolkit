"""
将指定的护理项目移动到医生门诊/住院的乙级治疗维度和护理的医护协同护理维度
"""
import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# 加载环境变量
load_dotenv('backend/.env')

# 数据库连接
DATABASE_URL = os.getenv('DATABASE_URL')
engine = create_engine(DATABASE_URL)

# 配置
VERSION_ID = 12  # 模型版本 ID
HOSPITAL_ID = 1  # 医疗机构 ID

# 需要移动的项目编码
item_codes = [
    '128100404',
    '128100406', 
    '128100407',
    '128100178',
    '128100400',
    '128100401'
]

print("=" * 80)
print("移动护理项目到治疗维度")
print("=" * 80)
print(f"模型版本 ID: {VERSION_ID}")
print(f"医疗机构 ID: {HOSPITAL_ID}")

with engine.connect() as conn:
    # 0. 先查看模型结构
    print("\n步骤0: 查看模型结构...")
    
    structure_query = text("""
        WITH RECURSIVE node_tree AS (
            -- 根节点（序列）
            SELECT id, parent_id, code, name, 0 as level, 
                   CAST(name AS TEXT) as path
            FROM model_nodes
            WHERE version_id = :version_id 
              AND parent_id IS NULL
            
            UNION ALL
            
            -- 递归查找子节点
            SELECT mn.id, mn.parent_id, mn.code, mn.name, nt.level + 1,
                   CAST(nt.path || ' > ' || mn.name AS TEXT)
            FROM model_nodes mn
            INNER JOIN node_tree nt ON mn.parent_id = nt.id
            WHERE mn.version_id = :version_id
        )
        SELECT id, code, name, level, path
        FROM node_tree
        WHERE name LIKE '%治疗%' OR name LIKE '%护理%'
        ORDER BY path;
    """)
    
    structure_results = conn.execute(structure_query, {'version_id': VERSION_ID}).fetchall()
    
    print("\n相关维度结构:")
    for row in structure_results:
        indent = "  " * row[3]
        print(f"{indent}[{row[0]}] {row[2]} (code: {row[1]})")
        print(f"{indent}    路径: {row[4]}")
    
    # 1. 查找目标维度的 node_id
    print("\n步骤1: 查找目标维度...")
    
    # 查找"乙级治疗"维度（门诊和住院）
    treatment_query = text("""
        SELECT mn.id, mn.code, mn.name, mn.version_id
        FROM model_nodes mn
        WHERE mn.version_id = :version_id
          AND mn.name = '乙级治疗'
        ORDER BY mn.id;
    """)
    treatment_results = conn.execute(treatment_query, {'version_id': VERSION_ID}).fetchall()
    
    if not treatment_results:
        print("❌ 未找到'乙级治疗'维度")
        exit(1)
    
    treatment_node_ids = [r[0] for r in treatment_results]
    print(f"✓ 找到 {len(treatment_results)} 个'乙级治疗'维度:")
    for r in treatment_results:
        print(f"  - ID={r[0]}, Code={r[1]}, Name={r[2]}")
    
    # 查找"医护协同治疗"维度
    nursing_query = text("""
        SELECT mn.id, mn.code, mn.name, mn.version_id
        FROM model_nodes mn
        WHERE mn.version_id = :version_id
          AND mn.name LIKE '%医护协同治疗%'
        LIMIT 1;
    """)
    nursing_result = conn.execute(nursing_query, {'version_id': VERSION_ID}).fetchone()
    
    if not nursing_result:
        print("❌ 未找到'医护协同治疗'维度")
        exit(1)
    
    nursing_node_id = nursing_result[0]
    print(f"✓ 找到'医护协同治疗'维度: ID={nursing_node_id}, Code={nursing_result[1]}, Name={nursing_result[2]}")
    
    # 2. 查找这些项目的当前映射
    print(f"\n步骤2: 查找项目当前映射...")
    
    for item_code in item_codes:
        check_query = text("""
            SELECT dim.id, dim.item_code, ci.item_name, mn.name as dimension_name, 
                   dim.dimension_code, dim.hospital_id
            FROM dimension_item_mappings dim
            LEFT JOIN charge_items ci ON dim.item_code = ci.item_code AND dim.hospital_id = ci.hospital_id
            LEFT JOIN model_nodes mn ON dim.dimension_code = mn.code AND mn.version_id = :version_id
            WHERE dim.item_code = :item_code
              AND dim.hospital_id = :hospital_id
            ORDER BY dim.id;
        """)
        
        results = conn.execute(check_query, {
            'item_code': item_code,
            'hospital_id': HOSPITAL_ID,
            'version_id': VERSION_ID
        }).fetchall()
        
        if results:
            print(f"\n  {item_code}:")
            for r in results:
                print(f"    - {r[2]} -> {r[3]} (dimension_code={r[4]}, mapping_id={r[0]})")
        else:
            print(f"\n  {item_code}: ⚠ 未找到映射")
    
    # 3. 确认操作
    print(f"\n步骤3: 准备更新映射...")
    print(f"将为每个项目创建 {len(treatment_node_ids) + 1} 条映射:")
    for i, node_id in enumerate(treatment_node_ids, 1):
        print(f"  {i}. 乙级治疗 (node_id={node_id})")
    print(f"  {len(treatment_node_ids) + 1}. 医护协同治疗 (node_id={nursing_node_id})")
    
    response = input("\n是否继续? (yes/no): ")
    if response.lower() != 'yes':
        print("操作已取消")
        exit(0)
    
    # 4. 删除旧映射
    print(f"\n步骤4: 删除旧映射...")
    
    delete_query = text("""
        DELETE FROM dimension_item_mappings
        WHERE item_code IN :item_codes
          AND hospital_id = :hospital_id;
    """)
    
    delete_result = conn.execute(delete_query, {
        'item_codes': tuple(item_codes),
        'hospital_id': HOSPITAL_ID
    })
    deleted_count = delete_result.rowcount
    print(f"✓ 删除了 {deleted_count} 条旧映射")
    
    # 5. 创建新映射
    print(f"\n步骤5: 创建新映射...")
    
    # 获取维度代码
    treatment_codes = [r[1] for r in treatment_results]
    nursing_code = nursing_result[1]
    
    # 为每个项目创建映射
    insert_count = 0
    
    insert_query = text("""
        INSERT INTO dimension_item_mappings (hospital_id, item_code, dimension_code, created_at)
        VALUES (:hospital_id, :item_code, :dimension_code, NOW());
    """)
    
    for item_code in item_codes:
        item_insert_count = 0
        
        # 映射到所有"乙级治疗"维度
        for treatment_code in treatment_codes:
            result = conn.execute(insert_query, {
                'hospital_id': HOSPITAL_ID,
                'item_code': item_code,
                'dimension_code': treatment_code
            })
            item_insert_count += result.rowcount
        
        # 映射到"医护协同治疗"
        result = conn.execute(insert_query, {
            'hospital_id': HOSPITAL_ID,
            'item_code': item_code,
            'dimension_code': nursing_code
        })
        item_insert_count += result.rowcount
        
        insert_count += item_insert_count
        print(f"  ✓ {item_code}: 创建了 {item_insert_count} 条映射")
    
    # 6. 提交事务
    conn.commit()
    
    print(f"\n✓ 成功创建 {insert_count} 条新映射")
    
    # 7. 验证结果
    print(f"\n步骤6: 验证结果...")
    
    for item_code in item_codes:
        verify_query = text("""
            SELECT dim.item_code, ci.item_name, mn.name as dimension_name
            FROM dimension_item_mappings dim
            LEFT JOIN charge_items ci ON dim.item_code = ci.item_code AND dim.hospital_id = ci.hospital_id
            LEFT JOIN model_nodes mn ON dim.dimension_code = mn.code AND mn.version_id = :version_id
            WHERE dim.item_code = :item_code
              AND dim.hospital_id = :hospital_id
            ORDER BY mn.name;
        """)
        
        results = conn.execute(verify_query, {
            'item_code': item_code,
            'hospital_id': HOSPITAL_ID,
            'version_id': VERSION_ID
        }).fetchall()
        
        if results:
            print(f"\n  {item_code} ({results[0][1]}):")
            for r in results:
                print(f"    -> {r[2]}")
        else:
            print(f"\n  {item_code}: ⚠ 未找到映射")

print("\n" + "=" * 80)
print("操作完成!")
print("=" * 80)
