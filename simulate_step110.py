"""
模拟执行步骤110的SQL，看看会产生多少条记录
"""
import os
import sys
sys.path.insert(0, 'backend')
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv('backend/.env')
DATABASE_URL = os.getenv('DATABASE_URL')
engine = create_engine(DATABASE_URL)

def simulate():
    with engine.connect() as conn:
        print("=" * 80)
        print("模拟执行步骤110的SQL（不实际插入）")
        print("=" * 80)
        
        # 模拟步骤110的SQL，但用SELECT代替INSERT
        result = conn.execute(text("""
            WITH RECURSIVE dimension_hierarchy AS (
                SELECT 
                    mn.id as dimension_id,
                    mn.code as dimension_code,
                    mn.name as dimension_name,
                    mn.parent_id,
                    mn.version_id,
                    CAST(mn.name AS TEXT) as path_names,
                    1 as level
                FROM model_nodes mn
                WHERE mn.version_id = 26
                  AND mn.node_type = 'sequence'
                
                UNION ALL
                
                SELECT 
                    mn.id,
                    mn.code,
                    mn.name,
                    mn.parent_id,
                    mn.version_id,
                    dh.path_names || '/' || mn.name,
                    dh.level + 1
                FROM model_nodes mn
                INNER JOIN dimension_hierarchy dh ON mn.parent_id = dh.dimension_id
                WHERE mn.node_type = 'dimension'
                  AND mn.version_id = 26
            ),
            dimension_business_type AS (
                SELECT 
                    dimension_id,
                    dimension_code,
                    dimension_name,
                    path_names,
                    CASE
                        WHEN path_names LIKE '医生/门诊%' OR path_names LIKE '医生序列/门诊%' THEN '门诊'
                        WHEN path_names LIKE '医生/住院%' OR path_names LIKE '医生序列/住院%' THEN '住院'
                        WHEN path_names LIKE '医生/手术/门诊%' OR path_names LIKE '医生序列/手术/门诊%' THEN '门诊'
                        WHEN path_names LIKE '医生/手术/住院%' OR path_names LIKE '医生序列/手术/住院%' THEN '住院'
                        WHEN path_names LIKE '护理/病区%' OR path_names LIKE '护理序列/病区%' THEN '住院'
                        WHEN path_names LIKE '护理/非病区%' OR path_names LIKE '护理序列/非病区%' THEN '门诊'
                        ELSE NULL
                    END as business_type
                FROM dimension_hierarchy
            ),
            dimension_mappings AS (
                SELECT DISTINCT
                    dbt.dimension_id,
                    dbt.business_type,
                    dim.item_code
                FROM dimension_item_mappings dim
                INNER JOIN dimension_business_type dbt ON dim.dimension_code = dbt.dimension_code
                WHERE dim.hospital_id = 1
            ),
            charge_data AS (
                SELECT 
                    cd.prescribing_dept_code,
                    cd.item_code,
                    cd.business_type,
                    SUM(cd.amount) as total_amount,
                    SUM(cd.quantity) as total_quantity,
                    COUNT(DISTINCT cd.patient_id) as patient_count
                FROM charge_details cd
                WHERE cd.charge_time >= '2025-10-01'
                  AND cd.charge_time < DATE '2025-10-31' + INTERVAL '1 day'
                  AND cd.prescribing_dept_code IN (
                      SELECT his_code 
                      FROM departments 
                      WHERE hospital_id = 1 
                        AND is_active = TRUE
                  )
                GROUP BY cd.prescribing_dept_code, cd.item_code, cd.business_type
            )
            SELECT 
                dm.dimension_id as node_id,
                d.id as department_id,
                mn.name as node_name,
                mn.code as node_code,
                COALESCE(SUM(cd.total_amount), 0) as workload
            FROM dimension_mappings dm
            LEFT JOIN charge_data cd ON dm.item_code = cd.item_code
                AND (
                    dm.business_type IS NULL
                    OR dm.business_type = cd.business_type
                )
            LEFT JOIN departments d ON cd.prescribing_dept_code = d.his_code
            INNER JOIN model_nodes mn ON dm.dimension_id = mn.id
            WHERE d.hospital_id = 1
              AND d.is_active = TRUE
            GROUP BY dm.dimension_id, d.id, mn.name, mn.code, mn.parent_id, mn.weight
            HAVING SUM(cd.total_amount) > 0
        """))
        
        rows = list(result)
        print(f"模拟执行结果: {len(rows)} 条记录")
        
        # 检查是否有重复
        seen = set()
        duplicates = []
        for row in rows:
            key = (row.node_code, row.department_id)
            if key in seen:
                duplicates.append(row)
            else:
                seen.add(key)
        
        if duplicates:
            print(f"\n发现 {len(duplicates)} 条重复记录:")
            for row in duplicates[:10]:
                print(f"  {row.node_code} - 科室{row.department_id}: workload={row.workload}")
        else:
            print("\n没有发现重复记录")

if __name__ == '__main__':
    simulate()
