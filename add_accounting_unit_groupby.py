"""
为工作流31的医生、护理、医技步骤添加核算单元分组
"""
import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv('backend/.env')
DATABASE_URL = os.getenv('DATABASE_URL')
engine = create_engine(DATABASE_URL)

def add_accounting_unit_groupby(step_id, sequence_name):
    """为步骤添加核算单元分组"""
    
    # 读取当前SQL
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT code_content FROM calculation_steps WHERE id = :step_id
        """), {"step_id": step_id})
        row = result.fetchone()
        if not row:
            print(f"✗ 步骤 {step_id} 不存在")
            return
        
        original_sql = row[0]
    
    print(f"\n处理步骤 {step_id}: {sequence_name}业务价值计算")
    print("="*80)
    
    # 修改SQL：
    # 1. 在SELECT中添加 d.accounting_unit_code, d.accounting_unit_name
    # 2. 在GROUP BY中添加 d.accounting_unit_code, d.accounting_unit_name
    
    updated_sql = original_sql
    
    # 查找所有的INSERT INTO calculation_results语句
    # 需要在每个INSERT的SELECT部分添加核算单元字段
    
    # 方法：在每个 "d.id as department_id," 后面添加核算单元字段
    updated_sql = updated_sql.replace(
        "d.id as department_id,",
        "d.id as department_id,\n    d.accounting_unit_code as accounting_unit_code,\n    d.accounting_unit_name as accounting_unit_name,"
    )
    
    # 在每个 GROUP BY 中添加核算单元字段
    # 查找 "GROUP BY mn.id, d.id" 并替换为 "GROUP BY mn.id, d.id, d.accounting_unit_code, d.accounting_unit_name"
    updated_sql = updated_sql.replace(
        "GROUP BY mn.id, d.id,",
        "GROUP BY mn.id, d.id, d.accounting_unit_code, d.accounting_unit_name,"
    )
    
    # 保存更新后的SQL
    filename = f"workflow31_step{step_id}_{sequence_name}_with_accounting_unit.sql"
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(updated_sql)
    
    print(f"✓ 已生成更新后的SQL: {filename}")
    
    # 统计变更
    original_lines = original_sql.count('\n')
    updated_lines = updated_sql.count('\n')
    accounting_unit_count = updated_sql.count('accounting_unit_code')
    
    print(f"  - 原始行数: {original_lines}")
    print(f"  - 更新行数: {updated_lines}")
    print(f"  - 添加核算单元字段次数: {accounting_unit_count}")
    
    # 询问是否更新数据库
    print("\n预览变更:")
    print("-" * 80)
    
    # 显示第一处变更
    lines = updated_sql.split('\n')
    for i, line in enumerate(lines):
        if 'accounting_unit_code' in line and i < 100:
            start = max(0, i - 2)
            end = min(len(lines), i + 3)
            print('\n'.join(lines[start:end]))
            print("...")
            break
    
    print("-" * 80)
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
    else:
        print("已取消数据库更新")
    
    return updated_sql

if __name__ == '__main__':
    print("="*80)
    print("工作流31 - 添加核算单元分组")
    print("="*80)
    print("\n说明:")
    print("- 在SELECT中添加 accounting_unit_code 和 accounting_unit_name")
    print("- 在GROUP BY中添加这两个字段")
    print("- 这样可以按核算单元分别统计业务价值")
    print("\n" + "="*80)
    
    steps = [
        (117, '医生'),
        (118, '护理'),
        (119, '医技')
    ]
    
    for step_id, sequence_name in steps:
        try:
            add_accounting_unit_groupby(step_id, sequence_name)
        except Exception as e:
            print(f"\n✗ 错误: {e}")
            import traceback
            traceback.print_exc()
        
        print("\n" + "="*80)
    
    print("\n升级完成！")
    print("\n注意事项:")
    print("1. calculation_results表需要有accounting_unit_code和accounting_unit_name字段")
    print("2. 如果字段不存在，需要先添加这两个字段")
    print("3. 更新后，每个科室会按核算单元分别生成统计记录")
