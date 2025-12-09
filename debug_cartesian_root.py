"""
深入调试笛卡尔积的根本原因
"""
import os
import sys
sys.path.insert(0, 'backend')
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv('backend/.env')
DATABASE_URL = os.getenv('DATABASE_URL')
engine = create_engine(DATABASE_URL)

def debug_cartesian():
    with engine.connect() as conn:
        # 检查版本26的模型节点
        print("=" * 80)
        print("检查版本26的模型节点")
        print("=" * 80)
        
        result = conn.execute(text("""
            SELECT 
                node_type,
                COUNT(*) as count,
                COUNT(DISTINCT code) as unique_codes
            FROM model_nodes
            WHERE version_id = 26
            GROUP BY node_type
        """))
        
        for row in result:
            print(f"  {row.node_type}: {row.count} 个节点, {row.unique_codes} 个唯一代码")
        
        # 检查是否有重复的节点代码
        print("\n检查是否有重复的节点代码:")
        result = conn.execute(text("""
            SELECT 
                code,
                name,
                COUNT(*) as count
            FROM model_nodes
            WHERE version_id = 26
            GROUP BY code, name
            HAVING COUNT(*) > 1
            ORDER BY count DESC
            LIMIT 10
        """))
        
        duplicates = list(result)
        if duplicates:
            print("发现重复的节点代码:")
            for row in duplicates:
                print(f"  {row.code} ({row.name}): {row.count} 次")
        else:
            print("没有发现重复的节点代码")
        
        # 检查 dimension_hierarchy CTE 的结果
        print("\n" + "=" * 80)
        print("检查 dimension_hierarchy CTE 的结果")
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
            )
            SELECT 
                dimension_code,
                dimension_name,
                COUNT(*) as count
            FROM dimension_hierarchy
            GROUP BY dimension_code, dimension_name
            HAVING COUNT(*) > 1
            ORDER BY count DESC
            LIMIT 10
        """))
        
        duplicates = list(result)
        if duplicates:
            print("发现重复的维度层级:")
            for row in duplicates:
                print(f"  {row.dimension_code} ({row.dimension_name}): {row.count} 次")
        else:
            print("没有发现重复的维度层级")
        
        # 检查 dimension_mappings CTE 的结果
        print("\n" + "=" * 80)
        print("检查 dimension_mappings 的重复情况")
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
            )
            SELECT 
                dbt.dimension_id,
                dbt.dimension_code,
                dbt.business_type,
                dim.item_code,
                COUNT(*) as count
            FROM dimension_item_mappings dim
            INNER JOIN dimension_business_type dbt ON dim.dimension_code = dbt.dimension_code
            WHERE dim.hospital_id = 1
            GROUP BY dbt.dimension_id, dbt.dimension_code, dbt.business_type, dim.item_code
            HAVING COUNT(*) > 1
            ORDER BY count DESC
            LIMIT 10
        """))
        
        duplicates = list(result)
        if duplicates:
            print("发现重复的维度映射:")
            for row in duplicates:
                print(f"  维度{row.dimension_id} ({row.dimension_code}) - 项目{row.item_code}: {row.count} 次")
        else:
            print("没有发现重复的维度映射")
        
        # 检查序列节点数量
        print("\n" + "=" * 80)
        print("检查序列节点")
        print("=" * 80)
        
        result = conn.execute(text("""
            SELECT id, code, name
            FROM model_nodes
            WHERE version_id = 26
              AND node_type = 'sequence'
        """))
        
        sequences = list(result)
        print(f"版本26有 {len(sequences)} 个序列节点:")
        for seq in sequences:
            print(f"  ID={seq.id}: {seq.code} ({seq.name})")

if __name__ == '__main__':
    debug_cartesian()
