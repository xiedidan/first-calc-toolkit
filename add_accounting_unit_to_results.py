"""
为calculation_results表添加核算单元字段，并更新工作流31的SQL
"""
import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv('backend/.env')
DATABASE_URL = os.getenv('DATABASE_URL')
engine = create_engine(DATABASE_URL)

def add_accounting_unit_fields():
    """添加核算单元字段到calculation_results表"""
    print("="*80)
    print("步骤1: 添加核算单元字段到calculation_results表")
    print("="*80)
    
    with engine.connect() as conn:
        # 检查字段是否已存在
        result = conn.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'calculation_results' 
            AND column_name IN ('accounting_unit_code', 'accounting_unit_name')
        """))
        existing_fields = [row[0] for row in result.fetchall()]
        
        if 'accounting_unit_code' in existing_fields and 'accounting_unit_name' in existing_fields:
            print("✓ 字段已存在，跳过添加")
            return True
        
        # 添加字段
        if 'accounting_unit_code' not in existing_fields:
            print("添加 accounting_unit_code 字段...")
            conn.execute(text("""
                ALTER TABLE calculation_results 
                ADD COLUMN accounting_unit_code VARCHAR(50)
            """))
            conn.execute(text("""
                COMMENT ON COLUMN calculation_results.accounting_unit_code 
                IS '核算单元代码'
            """))
            print("✓ 已添加 accounting_unit_code")
        
        if 'accounting_unit_name' not in existing_fields:
            print("添加 accounting_unit_name 字段...")
            conn.execute(text("""
                ALTER TABLE calculation_results 
                ADD COLUMN accounting_unit_name VARCHAR(100)
            """))
            conn.execute(text("""
                COMMENT ON COLUMN calculation_results.accounting_unit_name 
                IS '核算单元名称'
            """))
            print("✓ 已添加 accounting_unit_name")
        
        # 创建索引
        print("创建索引...")
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS ix_calculation_results_accounting_unit 
            ON calculation_results(accounting_unit_code)
        """))
        
        conn.commit()
        print("✓ 字段添加完成")
        return True

def update_workflow_sql(step_id, sequence_name):
    """更新工作流步骤SQL，添加核算单元分组"""
    print(f"\n{'='*80}")
    print(f"步骤2.{step_id-116}: 更新{sequence_name}业务价值计算SQL")
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
    
    # 修改SQL
    updated_sql = original_sql
    
    # 1. 在SELECT中添加核算单元字段（在department_id后面）
    updated_sql = updated_sql.replace(
        "d.id as department_id,",
        "d.id as department_id,\n    d.accounting_unit_code,\n    d.accounting_unit_name,"
    )
    
    # 2. 在GROUP BY中添加核算单元字段
    # 查找所有的 "GROUP BY mn.id, d.id," 并替换
    updated_sql = updated_sql.replace(
        "GROUP BY mn.id, d.id,",
        "GROUP BY mn.id, d.id, d.accounting_unit_code, d.accounting_unit_name,"
    )
    
    # 统计变更
    changes_count = updated_sql.count('accounting_unit_code')
    print(f"✓ 添加核算单元字段 {changes_count} 处")
    
    # 保存到文件
    filename = f"workflow31_step{step_id}_{sequence_name}_with_unit.sql"
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(updated_sql)
    print(f"✓ 已保存到: {filename}")
    
    # 显示示例变更
    print("\n变更示例:")
    print("-" * 80)
    lines = updated_sql.split('\n')
    for i, line in enumerate(lines):
        if 'accounting_unit_code' in line and 'SELECT' in '\n'.join(lines[max(0,i-10):i]):
            start = max(0, i - 3)
            end = min(len(lines), i + 4)
            for j in range(start, end):
                prefix = ">>> " if j == i or j == i+1 else "    "
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
    print("工作流31 - 添加核算单元分组统计")
    print("="*80)
    print("\n功能说明:")
    print("1. 为calculation_results表添加accounting_unit_code和accounting_unit_name字段")
    print("2. 更新医生、护理、医技步骤的SQL，在GROUP BY中添加核算单元")
    print("3. 这样可以按科室+核算单元的组合分别统计业务价值")
    print("\n业务场景:")
    print("- 同一个科室可能有多个核算单元")
    print("- 每个核算单元需要单独统计业务价值")
    print("- 例如：内科可能分为内科一病区、内科二病区等")
    print("\n" + "="*80)
    
    try:
        # 步骤1: 添加字段
        if not add_accounting_unit_fields():
            print("\n✗ 字段添加失败，终止升级")
            exit(1)
        
        # 步骤2: 更新SQL
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
        print(f"✓ 已添加核算单元字段到calculation_results表")
        print(f"✓ 已更新 {updated_count}/3 个工作流步骤")
        
        if updated_count < 3:
            print(f"\n⚠️  有 {3-updated_count} 个步骤未更新，请手动检查")
        
        print("\n后续操作:")
        print("1. 确保科室表中的accounting_unit_code和accounting_unit_name字段已填写")
        print("2. 执行计算任务测试新的分组逻辑")
        print("3. 验证结果中每个科室按核算单元分别统计")
        
    except Exception as e:
        print(f"\n✗ 错误: {e}")
        import traceback
        traceback.print_exc()
