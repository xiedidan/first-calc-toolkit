"""
更新工作流31的医生、护理、医技步骤，在GROUP BY中添加核算单元
"""
import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv('backend/.env')
DATABASE_URL = os.getenv('DATABASE_URL')
engine = create_engine(DATABASE_URL)

def update_workflow_sql(step_id, sequence_name):
    """更新工作流步骤SQL，在GROUP BY中添加核算单元"""
    print(f"\n{'='*80}")
    print(f"更新步骤 {step_id}: {sequence_name}业务价值计算")
    print("="*80)
    
    with engine.connect() as conn:
        # 读取当前SQL
        result = conn.execute(text("""
            SELECT code_content FROM calculation_steps WHERE id = :step_id
        """), {"step_id": step_id})
        row = result.fetchone()
        if not row:
            print(f"✗ 步骤 {step_id} 不存在")
            return False
        
        original_sql = row[0]
    
    # 修改SQL：在GROUP BY中添加核算单元字段
    # 原来: GROUP BY mn.id, d.id, mn.name, mn.code, mn.parent_id, mn.weight
    # 修改为: GROUP BY mn.id, d.id, d.accounting_unit_code, mn.name, mn.code, mn.parent_id, mn.weight
    
    updated_sql = original_sql.replace(
        "GROUP BY mn.id, d.id,",
        "GROUP BY mn.id, d.id, d.accounting_unit_code,"
    )
    
    # 统计变更
    original_groupby_count = original_sql.count('GROUP BY')
    changes_count = updated_sql.count('d.accounting_unit_code')
    
    print(f"✓ 找到 {original_groupby_count} 个 GROUP BY 语句")
    print(f"✓ 添加核算单元分组 {changes_count} 处")
    
    if changes_count == 0:
        print("⚠️  未找到需要修改的GROUP BY语句")
        return False
    
    # 保存到文件
    filename = f"workflow31_step{step_id}_{sequence_name}_unit_groupby.sql"
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(updated_sql)
    print(f"✓ 已保存到: {filename}")
    
    # 显示示例变更
    print("\n变更示例:")
    print("-" * 80)
    lines = updated_sql.split('\n')
    for i, line in enumerate(lines):
        if 'd.accounting_unit_code' in line and 'GROUP BY' in line:
            start = max(0, i - 2)
            end = min(len(lines), i + 3)
            for j in range(start, end):
                prefix = ">>> " if j == i else "    "
                print(f"{prefix}{lines[j]}")
            print("    ...")
            break
    print("-" * 80)
    
    # 更新数据库
    confirm = input(f"\n确认更新步骤 {step_id} 到数据库? (y/n): ").strip().lower()
    if confirm == 'y':
        with engine.connect() as conn:
            conn.execute(text("""
                UPDATE calculation_steps 
                SET code_content = :sql,
                    updated_at = NOW()
                WHERE id = :step_id
            """), {"sql": updated_sql, "step_id": step_id})
            conn.commit()
        print(f"✓ 已更新数据库中的步骤 {step_id}")
        return True
    else:
        print("✗ 已取消数据库更新")
        return False

if __name__ == '__main__':
    print("\n" + "="*80)
    print("工作流31 - 添加核算单元分组")
    print("="*80)
    print("\n功能说明:")
    print("- 在GROUP BY中添加 d.accounting_unit_code")
    print("- 这样同一个科室的不同核算单元会分别统计")
    print("- calculation_results表中的department_id就代表核算单元")
    print("\n业务场景:")
    print("- 科室表中，同一个科室名称可能有多条记录")
    print("- 通过accounting_unit_code区分不同的核算单元")
    print("- 例如：内科一病区、内科二病区等")
    print("\n" + "="*80)
    
    try:
        steps = [
            (117, '医生'),
            (118, '护理'),
            (119, '医技')
        ]
        
        updated_count = 0
        for step_id, sequence_name in steps:
            if update_workflow_sql(step_id, sequence_name):
                updated_count += 1
        
        print("\n" + "="*80)
        print("升级完成！")
        print("="*80)
        print(f"✓ 已更新 {updated_count}/3 个工作流步骤")
        
        if updated_count < 3:
            print(f"\n⚠️  有 {3-updated_count} 个步骤未更新")
        
        print("\n说明:")
        print("- 现在统计时会按 (维度, 科室, 核算单元) 分组")
        print("- 同一个科室的不同核算单元会生成不同的记录")
        print("- department_id字段就代表具体的核算单元")
        
    except Exception as e:
        print(f"\n✗ 错误: {e}")
        import traceback
        traceback.print_exc()
