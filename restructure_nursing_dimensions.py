"""
重构护理维度结构：
1. 删除一级维度（病区、非病区）
2. 二级维度提升为一级维度
3. 三级维度变为二级维度
4. 更新所有 code
"""
import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv('backend/.env')
DATABASE_URL = os.getenv('DATABASE_URL')
engine = create_engine(DATABASE_URL)

def main():
    # 查询所有维度节点
    with engine.connect() as conn:
        result = conn.execute(text("""
        SELECT id, name, code, parent_id, sort_order
        FROM model_nodes
        WHERE version_id = 12 AND node_type = 'dimension'
        ORDER BY id;
    """))
    
    all_dims = {row.id: dict(row._mapping) for row in result}
    
    nursing_seq_id = 711
    
    # 找出要删除的一级维度
    level1_to_delete = [d for d in all_dims.values() if d['parent_id'] == nursing_seq_id]
    
    print("=== 将要删除的一级维度 ===")
    for dim in level1_to_delete:
        print(f"  - {dim['name']} (ID: {dim['id']}, Code: {dim['code']})")
    
    # 找出要提升的二级维度
    level2_to_promote = []
    for l1 in level1_to_delete:
        children = [d for d in all_dims.values() if d['parent_id'] == l1['id']]
        level2_to_promote.extend(children)
    
    print(f"\n=== 将要提升为一级的二级维度 ({len(level2_to_promote)}个) ===")
    for dim in sorted(level2_to_promote, key=lambda x: x['id']):
        print(f"  - {dim['name']} (ID: {dim['id']}, Code: {dim['code']})")
    
    # 找出要降级的三级维度
    level3_to_demote = []
    for l2 in level2_to_promote:
        children = [d for d in all_dims.values() if d['parent_id'] == l2['id']]
        level3_to_demote.extend(children)
    
    print(f"\n=== 将要降级为二级的三级维度 ({len(level3_to_demote)}个) ===")
    for dim in sorted(level3_to_demote, key=lambda x: x['id']):
        print(f"  - {dim['name']} (ID: {dim['id']}, Code: {dim['code']})")
    
    print("\n开始执行重构...")
    
    # 使用新连接执行事务
    with engine.begin() as trans:
        try:
            # 步骤1: 更新三级维度的code（去掉一层前缀）
            print("\n=== 步骤1: 更新三级维度 ===")
            for dim in level3_to_demote:
                old_code = dim['code']
                # dim-nur-ward-bed-1 -> dim-nur-bed-1
                # dim-nur-proc-or-large -> dim-nur-or-large
                parts = old_code.split('-')
                if len(parts) >= 4:
                    # 去掉第三部分（ward或proc）
                    new_code = f"{parts[0]}-{parts[1]}-{'-'.join(parts[3:])}"
                else:
                    new_code = old_code
                
                print(f"  更新 {dim['name']}: {old_code} -> {new_code}")
                
                # 更新 model_nodes
                trans.execute(text("""
                    UPDATE model_nodes
                    SET code = :new_code
                    WHERE id = :node_id AND version_id = 12
                """), {'new_code': new_code, 'node_id': dim['id']})
                
                # 更新 dimension_item_mappings (没有version_id字段)
                result = trans.execute(text("""
                    UPDATE dimension_item_mappings
                    SET dimension_code = :new_code
                    WHERE dimension_code = :old_code
                """), {'new_code': new_code, 'old_code': old_code})
                print(f"    更新了 {result.rowcount} 条映射记录")
            
            # 步骤2: 更新二级维度（提升为一级）
            print("\n=== 步骤2: 提升二级维度为一级 ===")
            for dim in level2_to_promote:
                old_code = dim['code']
                # dim-nur-ward-bed -> dim-nur-bed
                # dim-nur-proc-or -> dim-nur-or
                parts = old_code.split('-')
                if len(parts) >= 4:
                    # 去掉第三部分
                    new_code = f"{parts[0]}-{parts[1]}-{'-'.join(parts[3:])}"
                else:
                    new_code = old_code
                
                print(f"  提升 {dim['name']}: {old_code} -> {new_code}, parent: {dim['parent_id']} -> {nursing_seq_id}")
                
                # 更新 model_nodes
                trans.execute(text("""
                    UPDATE model_nodes
                    SET parent_id = :new_parent_id,
                        code = :new_code
                    WHERE id = :node_id AND version_id = 12
                """), {
                    'new_parent_id': nursing_seq_id,
                    'new_code': new_code,
                    'node_id': dim['id']
                })
                
                # 更新 dimension_item_mappings (没有version_id字段)
                result = trans.execute(text("""
                    UPDATE dimension_item_mappings
                    SET dimension_code = :new_code
                    WHERE dimension_code = :old_code
                """), {'new_code': new_code, 'old_code': old_code})
                print(f"    更新了 {result.rowcount} 条映射记录")
            
            # 步骤3: 删除原一级维度
            print("\n=== 步骤3: 删除原一级维度 ===")
            for dim in level1_to_delete:
                print(f"  删除 {dim['name']} (ID: {dim['id']})")
                
                # 删除映射 (没有version_id字段)
                result = trans.execute(text("""
                    DELETE FROM dimension_item_mappings
                    WHERE dimension_code = :code
                """), {'code': dim['code']})
                print(f"    删除了 {result.rowcount} 条映射记录")
                
                # 删除节点
                trans.execute(text("""
                    DELETE FROM model_nodes
                    WHERE id = :node_id AND version_id = 12
                """), {'node_id': dim['id']})
            
            print("\n=== 重构完成 ===")
            
        except Exception as e:
            print(f"\n错误：{e}")
            import traceback
            traceback.print_exc()
            raise
    
    # 验证结果
    print("\n=== 验证结果 ===")
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT id, name, code, parent_id, sort_order
            FROM model_nodes
            WHERE version_id = 12 
            AND node_type = 'dimension'
            AND (code LIKE 'dim-nur-%')
            ORDER BY parent_id, sort_order, id;
        """))
        
        print("\n更新后的护理维度结构:")
        current_parent = None
        for row in result:
            if row.parent_id != current_parent:
                current_parent = row.parent_id
                if row.parent_id == nursing_seq_id:
                    print(f"\n一级维度（parent={nursing_seq_id}）:")
                else:
                    print(f"\n二级维度（parent={row.parent_id}）:")
            print(f"  - {row.name} (ID: {row.id}, Code: {row.code})")

if __name__ == '__main__':
    main()
