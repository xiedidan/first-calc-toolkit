"""
测试 dimension_hierarchy CTE 是否产生重复
"""
import os
import sys
sys.path.insert(0, 'backend')
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv('backend/.env')
DATABASE_URL = os.getenv('DATABASE_URL')
engine = create_engine(DATABASE_URL)

def test():
    with engine.connect() as conn:
        print("=" * 80)
        print("测试 dimension_hierarchy CTE")
        print("=" * 80)
        
        # 测试 dimension_hierarchy CTE
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
            )
            SELECT 
                dimension_code,
                dimension_name,
                COUNT(*) as count,
                STRING_AGG(DISTINCT path_names, ' | ') as paths
            FROM dimension_hierarchy
            GROUP BY dimension_code, dimension_name
            HAVING COUNT(*) > 1
            ORDER BY count DESC
            LIMIT 20
        """))
        
        duplicates = list(result)
        if duplicates:
            print("发现重复的维度:")
            for row in duplicates:
                print(f"  {row.dimension_code} ({row.dimension_name}): {row.count} 次")
                print(f"    路径: {row.paths[:200]}...")
        else:
            print("没有发现重复的维度")
        
        # 检查 dimension_mappings CTE
        print("\n" + "=" * 80)
        print("测试 dimension_mappings CTE")
        print("=" * 80)
        
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
            )
            SELECT 
                dimension_id,
                business_type,
                COUNT(DISTINCT item_code) as item_count,
                COUNT(*) as total_count
            FROM dimension_mappings
            GROUP BY dimension_id, business_type
            HAVING COUNT(*) != COUNT(DISTINCT item_code)
            ORDER BY total_count DESC
            LIMIT 10
        """))
        
        duplicates = list(result)
        if duplicates:
            print("发现重复的映射:")
            for row in duplicates:
                print(f"  维度{row.dimension_id} ({row.business_type}): {row.item_count} 个唯一项目, {row.total_count} 条记录")
        else:
            print("没有发现重复的映射")

if __name__ == '__main__':
    test()
