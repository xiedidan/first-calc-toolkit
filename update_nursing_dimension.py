"""
更新模板版本12的护理维度结构
将二级维度提升为一级维度，删除原一级维度
"""
import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# 加载环境变量
load_dotenv('backend/.env')

DATABASE_URL = os.getenv('DATABASE_URL')
engine = create_engine(DATABASE_URL)

def main():
    with engine.connect() as conn:
        # 1. 查看当前护理相关的维度结构
        print("=== 当前护理维度结构 ===")
        result = conn.execute(text("""
            SELECT id, name, code, parent_id, node_type, sort_order
            FROM model_nodes
            WHERE version_id = 12 
            AND node_type = 'dimension'
            AND (name LIKE '%护理%' OR code LIKE '%nursing%' OR code LIKE '%HL%')
            ORDER BY parent_id NULLS FIRST, sort_order, id;
        """))
        
        nodes = []
        for row in result:
            nodes.append(dict(row._mapping))
            print(f"ID: {row.id}, Name: {row.name}, Code: {row.code}, Parent: {row.parent_id}, Sort: {row.sort_order}")
        
        if not nodes:
            print("未找到护理相关维度")
            return
        
        # 找出一级维度（parent_id为序列节点）
        print("\n=== 查找序列节点 ===")
        sequence_result = conn.execute(text("""
            SELECT id, name, code
            FROM model_nodes
            WHERE version_id = 12 AND node_type = 'sequence'
            ORDER BY id;
        """))
        
        sequence_nodes = {row.id: dict(row._mapping) for row in sequence_result}
        for seq_id, seq_node in sequence_nodes.items():
            print(f"序列 ID: {seq_id}, Name: {seq_node['name']}, Code: {seq_node['code']}")
        
        # 识别一级和二级维度
        level1_dims = [n for n in nodes if n['parent_id'] in sequence_nodes]
        level2_dims = [n for n in nodes if n['parent_id'] not in sequence_nodes and n['parent_id'] is not None]
        
        print(f"\n=== 识别结果 ===")
        print(f"一级维度（将被删除）: {len(level1_dims)} 个")
        for dim in level1_dims:
            print(f"  - ID: {dim['id']}, Name: {dim['name']}, Code: {dim['code']}")
        
        print(f"\n二级维度（将提升为一级）: {len(level2_dims)} 个")
        for dim in level2_dims:
            print(f"  - ID: {dim['id']}, Name: {dim['name']}, Code: {dim['code']}, 当前Parent: {dim['parent_id']}")
        
        # 查看一级维度的详细信息
        if level1_dims:
            print(f"\n=== 一级维度详情 ===")
            for dim in level1_dims:
                result = conn.execute(text("""
                    SELECT COUNT(*) as child_count
                    FROM model_nodes
                    WHERE parent_id = :parent_id AND version_id = 12
                """), {'parent_id': dim['id']})
                child_count = result.scalar()
                print(f"维度 {dim['name']} (ID: {dim['id']}) 有 {child_count} 个子节点")
        
        if not level1_dims:
            print("\n错误：未找到一级维度（parent_id为序列节点的维度）")
            print("让我查看所有护理相关的维度层级...")
            
            # 查看所有维度节点
            result = conn.execute(text("""
                SELECT id, name, code, parent_id
                FROM model_nodes
                WHERE version_id = 12 AND node_type = 'dimension'
                ORDER BY id;
            """))
            
            all_dims = {row.id: dict(row._mapping) for row in result}
            
            # 找出护理序列下的直接子节点
            nursing_seq_id = 711  # 从上面的输出可以看到
            direct_children = [d for d in all_dims.values() if d['parent_id'] == nursing_seq_id]
            
            print(f"\n护理序列 (ID: {nursing_seq_id}) 的直接子节点:")
            for child in direct_children:
                print(f"  - ID: {child['id']}, Name: {child['name']}, Code: {child['code']}")
                
                # 查看这个节点的子节点
                grandchildren = [d for d in all_dims.values() if d['parent_id'] == child['id']]
                if grandchildren:
                    print(f"    它有 {len(grandchildren)} 个子节点:")
                    for gc in grandchildren[:3]:  # 只显示前3个
                        print(f"      - {gc['name']} (Code: {gc['code']})")
                    if len(grandchildren) > 3:
                        print(f"      ... 还有 {len(grandchildren) - 3} 个")
            
            return
        
        # 确认操作
        print("\n=== 将执行以下操作 ===")
        print("1. 将二级维度的 parent_id 改为序列节点ID")
        print("2. 更新二级维度的 code（去掉二级前缀）")
        print("3. 删除原一级维度")
        print("4. 更新 dimension_item_mappings 中的维度 code")
        
        confirm = input("\n确认执行？(yes/no): ")
        if confirm.lower() != 'yes':
            print("操作已取消")
            return
        
        # 获取序列节点ID（假设二级维度的parent_id就是一级维度的ID）
        if level1_dims:
            old_level1_id = level1_dims[0]['id']
            new_parent_id = level1_dims[0]['parent_id']  # 这是序列节点ID
            
            print(f"\n序列节点ID: {new_parent_id}")
            print(f"旧一级维度ID: {old_level1_id}")
        
        # 开始事务
        trans = conn.begin()
        try:
            # 2. 更新二级维度
            for dim in level2_dims:
                old_code = dim['code']
                # 假设code格式是 HL-XXX，去掉前缀变成 XXX
                # 或者如果是 HL-HL-XXX，去掉一个 HL- 变成 HL-XXX
                if old_code.count('-') >= 2:
                    # HL-HL-XXX -> HL-XXX
                    parts = old_code.split('-', 2)
                    new_code = f"{parts[1]}-{parts[2]}"
                elif old_code.count('-') == 1:
                    # HL-XXX -> XXX (但这可能不对，需要保持HL前缀)
                    # 实际上应该保持原样或根据实际情况调整
                    new_code = old_code
                else:
                    new_code = old_code
                
                print(f"\n更新维度 ID {dim['id']}: {dim['name']}")
                print(f"  Code: {old_code} -> {new_code}")
                print(f"  Parent: {dim['parent_id']} -> {new_parent_id}")
                
                # 更新 model_nodes
                conn.execute(text("""
                    UPDATE model_nodes
                    SET parent_id = :new_parent_id,
                        code = :new_code
                    WHERE id = :node_id AND version_id = 12
                """), {
                    'new_parent_id': new_parent_id,
                    'new_code': new_code,
                    'node_id': dim['id']
                })
                
                # 更新 dimension_item_mappings
                result = conn.execute(text("""
                    UPDATE dimension_item_mappings
                    SET dimension_code = :new_code
                    WHERE dimension_code = :old_code
                    AND version_id = 12
                """), {
                    'new_code': new_code,
                    'old_code': old_code
                })
                print(f"  更新了 {result.rowcount} 条映射记录")
            
            # 3. 删除原一级维度
            for dim in level1_dims:
                print(f"\n删除一级维度 ID {dim['id']}: {dim['name']}")
                
                # 先删除相关的映射
                result = conn.execute(text("""
                    DELETE FROM dimension_item_mappings
                    WHERE dimension_code = :code AND version_id = 12
                """), {'code': dim['code']})
                print(f"  删除了 {result.rowcount} 条映射记录")
                
                # 删除节点
                conn.execute(text("""
                    DELETE FROM model_nodes
                    WHERE id = :node_id AND version_id = 12
                """), {'node_id': dim['id']})
                print(f"  已删除维度节点")
            
            # 提交事务
            trans.commit()
            print("\n=== 操作完成 ===")
            
            # 验证结果
            print("\n=== 验证结果 ===")
            result = conn.execute(text("""
                SELECT id, name, code, parent_id, node_type
                FROM model_nodes
                WHERE version_id = 12 
                AND node_type = 'dimension'
                AND (name LIKE '%护理%' OR code LIKE '%nursing%' OR code LIKE '%HL%')
                ORDER BY parent_id NULLS FIRST, id;
            """))
            
            print("更新后的护理维度结构:")
            for row in result:
                print(f"ID: {row.id}, Name: {row.name}, Code: {row.code}, Parent: {row.parent_id}")
            
        except Exception as e:
            trans.rollback()
            print(f"\n错误：{e}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    main()
