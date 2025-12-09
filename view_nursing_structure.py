"""
查看护理维度的完整三级结构
"""
import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv('backend/.env')
DATABASE_URL = os.getenv('DATABASE_URL')
engine = create_engine(DATABASE_URL)

with engine.connect() as conn:
    # 查询所有维度节点
    result = conn.execute(text("""
        SELECT id, name, code, parent_id, sort_order
        FROM model_nodes
        WHERE version_id = 12 AND node_type = 'dimension'
        ORDER BY id;
    """))
    
    all_dims = {row.id: dict(row._mapping) for row in result}
    
    # 护理序列ID
    nursing_seq_id = 711
    
    # 一级维度（护理序列的直接子节点）
    level1 = [d for d in all_dims.values() if d['parent_id'] == nursing_seq_id]
    
    print("=== 护理维度完整结构 ===\n")
    print(f"序列: 护理 (ID: {nursing_seq_id})")
    
    for l1 in sorted(level1, key=lambda x: x['sort_order'] or 0):
        print(f"\n  一级维度: {l1['name']} (ID: {l1['id']}, Code: {l1['code']})")
        
        # 二级维度
        level2 = [d for d in all_dims.values() if d['parent_id'] == l1['id']]
        for l2 in sorted(level2, key=lambda x: x['sort_order'] or 0):
            print(f"    二级维度: {l2['name']} (ID: {l2['id']}, Code: {l2['code']})")
            
            # 三级维度
            level3 = [d for d in all_dims.values() if d['parent_id'] == l2['id']]
            for l3 in sorted(level3, key=lambda x: x['sort_order'] or 0):
                print(f"      三级维度: {l3['name']} (ID: {l3['id']}, Code: {l3['code']})")
    
    print("\n=== 需要执行的操作 ===")
    print("1. 删除一级维度: 病区、非病区")
    print("2. 将二级维度提升为一级维度（直接挂在护理序列下）")
    print("3. 三级维度变为二级维度")
    print("4. 更新所有相关的 code")
