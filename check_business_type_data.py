"""
诊断脚本：检查门诊/住院数据区分是否正确
"""
import os
import sys
sys.path.insert(0, 'backend')

from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv('backend/.env')

DATABASE_URL = os.getenv('DATABASE_URL')
engine = create_engine(DATABASE_URL)

def check_data():
    with engine.connect().execution_options(isolation_level="AUTOCOMMIT") as conn:
        print("=" * 80)
        print("1. 检查 charge_details 表中的业务类别分布")
        print("=" * 80)
        result = conn.execute(text("""
            SELECT 
                business_type,
                COUNT(*) as record_count,
                SUM(amount) as total_amount
            FROM charge_details
            GROUP BY business_type
            ORDER BY business_type
        """))
        for row in result:
            print(f"  {row.business_type}: {row.record_count} 条记录, 金额: {row.total_amount}")
        
        print("\n" + "=" * 80)
        print("2. 检查源表数据量")
        print("=" * 80)
        
        # 检查门诊源表
        try:
            result = conn.execute(text('SELECT COUNT(*) as cnt FROM "TB_MZ_SFMXB"'))
            row = result.fetchone()
            print(f"  TB_MZ_SFMXB (门诊): {row.cnt} 条记录")
        except Exception as e:
            print(f"  TB_MZ_SFMXB (门诊): 表不存在或查询失败 - {e}")
        
        # 检查住院源表
        try:
            result = conn.execute(text('SELECT COUNT(*) as cnt FROM "TB_ZY_SFMXB"'))
            row = result.fetchone()
            print(f"  TB_ZY_SFMXB (住院): {row.cnt} 条记录")
        except Exception as e:
            print(f"  TB_ZY_SFMXB (住院): 表不存在或查询失败 - {e}")
        
        print("\n" + "=" * 80)
        print("3. 检查模型结构中的门诊/住院维度")
        print("=" * 80)
        result = conn.execute(text("""
            SELECT 
                mn.id,
                mn.name,
                mn.code,
                mn.node_type,
                pn.name as parent_name
            FROM model_nodes mn
            INNER JOIN model_versions mv ON mn.version_id = mv.id
            LEFT JOIN model_nodes pn ON mn.parent_id = pn.id
            WHERE mv.is_active = TRUE
              AND (mn.name LIKE '%门诊%' OR mn.name LIKE '%住院%' OR mn.node_type = 'sequence')
            ORDER BY mn.node_type DESC, mn.name
            LIMIT 30
        """))
        for row in result:
            print(f"  [{row.node_type}] {row.name} (code: {row.code}, parent: {row.parent_name})")
        
        print("\n" + "=" * 80)
        print("4. 检查计算结果中门诊/住院维度的工作量")
        print("=" * 80)
        result = conn.execute(text("""
            SELECT 
                cr.node_name,
                COUNT(DISTINCT cr.department_id) as dept_count,
                SUM(cr.workload) as total_workload
            FROM calculation_results cr
            WHERE cr.node_name IN ('门诊', '住院', '手术')
              OR cr.node_name LIKE '%门诊%'
              OR cr.node_name LIKE '%住院%'
            GROUP BY cr.node_name
            ORDER BY cr.node_name
            LIMIT 20
        """))
        rows = list(result)
        if rows:
            for row in rows:
                print(f"  {row.node_name}: {row.dept_count} 个科室, 工作量: {row.total_workload}")
        else:
            print("  没有找到门诊/住院相关的计算结果")
        
        print("\n" + "=" * 80)
        print("5. 检查最新任务的维度统计详情")
        print("=" * 80)
        result = conn.execute(text("""
            WITH latest_task AS (
                SELECT task_id FROM calculation_tasks 
                WHERE status = 'completed' 
                ORDER BY completed_at DESC 
                LIMIT 1
            )
            SELECT 
                cr.node_name,
                d.his_name as department_name,
                cr.workload
            FROM calculation_results cr
            INNER JOIN latest_task lt ON cr.task_id = lt.task_id
            LEFT JOIN departments d ON cr.department_id = d.id
            WHERE cr.node_name IN ('门诊', '住院')
            ORDER BY cr.node_name, d.his_name
            LIMIT 30
        """))
        rows = list(result)
        if rows:
            for row in rows:
                print(f"  {row.node_name} - {row.department_name}: {row.workload}")
        else:
            print("  没有找到门诊/住院维度的计算结果")
        
        print("\n" + "=" * 80)
        print("6. 检查维度-收费项目映射")
        print("=" * 80)
        result = conn.execute(text("""
            SELECT 
                dim.dimension_code,
                mn.name as dimension_name,
                COUNT(DISTINCT dim.item_code) as item_count
            FROM dimension_item_mappings dim
            LEFT JOIN model_nodes mn ON dim.dimension_code = mn.code
            GROUP BY dim.dimension_code, mn.name
            ORDER BY item_count DESC
            LIMIT 20
        """))
        for row in result:
            print(f"  {row.dimension_code} ({row.dimension_name}): {row.item_count} 个项目")
        
        print("\n" + "=" * 80)
        print("7. 检查有工作量的维度")
        print("=" * 80)
        result = conn.execute(text("""
            SELECT 
                cr.node_name,
                cr.node_code,
                SUM(cr.workload) as total_workload,
                COUNT(DISTINCT cr.department_id) as dept_count
            FROM calculation_results cr
            WHERE cr.workload > 0
            GROUP BY cr.node_name, cr.node_code
            ORDER BY total_workload DESC
            LIMIT 20
        """))
        for row in result:
            print(f"  {row.node_name} ({row.node_code}): 工作量={row.total_workload}, {row.dept_count}个科室")

        print("\n" + "=" * 80)
        print("8. 检查维度层级路径")
        print("=" * 80)
        result = conn.execute(text("""
            WITH RECURSIVE dimension_hierarchy AS (
                SELECT 
                    mn.id as dimension_id,
                    mn.code as dimension_code,
                    mn.name as dimension_name,
                    mn.parent_id,
                    CAST(mn.name AS TEXT) as path_names,
                    1 as level
                FROM model_nodes mn
                INNER JOIN model_versions mv ON mn.version_id = mv.id
                WHERE mv.is_active = TRUE
                  AND mn.node_type = 'sequence'
                
                UNION ALL
                
                SELECT 
                    mn.id,
                    mn.code,
                    mn.name,
                    mn.parent_id,
                    dh.path_names || '/' || mn.name,
                    dh.level + 1
                FROM model_nodes mn
                INNER JOIN dimension_hierarchy dh ON mn.parent_id = dh.dimension_id
                WHERE mn.node_type = 'dimension'
            )
            SELECT dimension_code, dimension_name, path_names, level
            FROM dimension_hierarchy
            WHERE dimension_code LIKE 'dim-doc%'
            ORDER BY path_names
            LIMIT 30
        """))
        for row in result:
            print(f"  [{row.level}] {row.path_names} ({row.dimension_code})")

if __name__ == '__main__':
    check_data()
