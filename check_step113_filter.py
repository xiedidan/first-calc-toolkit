"""
检查步骤113的过滤条件是否正确
"""
import os
import sys
sys.path.insert(0, 'backend')
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv('backend/.env')
DATABASE_URL = os.getenv('DATABASE_URL')
engine = create_engine(DATABASE_URL)

def check_filter():
    with engine.connect() as conn:
        # 检查步骤113实际插入的维度是否符合过滤条件
        print("=" * 80)
        print("检查步骤113应该插入的维度（根据SQL过滤条件）")
        print("=" * 80)
        
        # 步骤113的过滤条件是:
        # mn.code LIKE 'dim-nur-bed%'
        # OR mn.code LIKE 'dim-nur-trans%'
        # OR mn.code LIKE 'dim-nur-op%'
        # OR mn.code LIKE 'dim-nur-or%'
        
        result = conn.execute(text("""
            SELECT code, name
            FROM model_nodes
            WHERE version_id = 26
              AND node_type = 'dimension'
              AND (
                code LIKE 'dim-nur-bed%'
                OR code LIKE 'dim-nur-trans%'
                OR code LIKE 'dim-nur-op%'
                OR code LIKE 'dim-nur-or%'
              )
            ORDER BY code
        """))
        
        expected = list(result)
        print(f"根据过滤条件，步骤113应该只插入以下维度 ({len(expected)} 个):")
        for rec in expected:
            print(f"  {rec.code} ({rec.name})")
        
        # 检查步骤113实际插入的维度
        print("\n" + "=" * 80)
        print("步骤113实际插入的维度（不符合过滤条件的）")
        print("=" * 80)
        
        task_uuid = '83289d5f-df1f-4739-afdb-5aa76934eb2a'
        step113_start = '2025-12-05 13:17:25.293'
        step113_end = '2025-12-05 13:17:25.976'
        
        result = conn.execute(text("""
            SELECT DISTINCT node_code, node_name
            FROM calculation_results
            WHERE task_id = :task_id
              AND created_at >= :start_time
              AND created_at < :end_time
              AND NOT (
                node_code LIKE 'dim-nur-bed%'
                OR node_code LIKE 'dim-nur-trans%'
                OR node_code LIKE 'dim-nur-op%'
                OR node_code LIKE 'dim-nur-or%'
              )
            ORDER BY node_code
        """), {
            "task_id": task_uuid,
            "start_time": step113_start,
            "end_time": step113_end
        })
        
        unexpected = list(result)
        print(f"不符合过滤条件但被插入的维度 ({len(unexpected)} 个):")
        for rec in unexpected:
            print(f"  {rec.node_code} ({rec.node_name})")

if __name__ == '__main__':
    check_filter()
