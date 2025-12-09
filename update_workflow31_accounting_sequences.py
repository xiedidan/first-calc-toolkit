"""
更新工作流31的医生、护理、医技步骤，添加核算序列过滤
"""
import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv('backend/.env')
DATABASE_URL = os.getenv('DATABASE_URL')
engine = create_engine(DATABASE_URL)

def update_step_sql(step_id, sequence_name):
    """更新步骤SQL，添加核算序列过滤"""
    
    # 读取原SQL
    filename = f"workflow31_step{step_id}_{sequence_name}业务价值计算.sql"
    with open(filename, 'r', encoding='utf-8') as f:
        original_sql = f.read()
    
    # 添加核算序列过滤条件
    # 在每个 "INNER JOIN departments d" 后面添加过滤条件
    updated_sql = original_sql.replace(
        "INNER JOIN departments d ON cd.prescribing_dept_code = d.his_code AND d.hospital_id = {hospital_id}",
        f"INNER JOIN departments d ON cd.prescribing_dept_code = d.his_code AND d.hospital_id = {{hospital_id}} AND '{sequence_name}' = ANY(d.accounting_sequences)"
    )
    
    # 特殊处理：住院病例价值（没有通过item_code关联）
    if step_id == 117:  # 医生步骤
        updated_sql = updated_sql.replace(
            "INNER JOIN departments d ON cd.prescribing_dept_code = d.his_code AND d.hospital_id = {hospital_id}\nWHERE cd.business_type = '住院'\n  AND TO_CHAR(cd.charge_time, 'YYYY-MM') = '{current_year_month}'\n  AND cd.hospital_id = {hospital_id}",
            f"INNER JOIN departments d ON cd.prescribing_dept_code = d.his_code AND d.hospital_id = {{hospital_id}} AND '{sequence_name}' = ANY(d.accounting_sequences)\nWHERE cd.business_type = '住院'\n  AND TO_CHAR(cd.charge_time, 'YYYY-MM') = '{{current_year_month}}'\n  AND cd.hospital_id = {{hospital_id}}"
        )
    
    # 保存更新后的SQL
    updated_filename = f"workflow31_step{step_id}_{sequence_name}业务价值计算_updated.sql"
    with open(updated_filename, 'w', encoding='utf-8') as f:
        f.write(updated_sql)
    
    print(f"✓ 已更新 {sequence_name} 步骤SQL: {updated_filename}")
    
    # 更新数据库
    with engine.connect() as conn:
        conn.execute(text("""
            UPDATE calculation_steps 
            SET code_content = :sql,
                updated_at = NOW()
            WHERE id = :step_id
        """), {"sql": updated_sql, "step_id": step_id})
        conn.commit()
    
    print(f"✓ 已更新数据库中的步骤 {step_id}")
    
    return updated_sql

if __name__ == '__main__':
    print("开始更新工作流31的核算序列过滤...")
    print("="*80)
    
    steps = [
        (117, '医生'),
        (118, '护理'),
        (119, '医技')
    ]
    
    for step_id, sequence_name in steps:
        print(f"\n处理步骤 {step_id}: {sequence_name}业务价值计算")
        try:
            update_step_sql(step_id, sequence_name)
        except Exception as e:
            print(f"✗ 错误: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "="*80)
    print("更新完成！")
    print("\n说明:")
    print("- 已在所有 JOIN departments 处添加核算序列过滤")
    print("- 过滤条件: '{序列名}' = ANY(d.accounting_sequences)")
    print("- 只有科室的accounting_sequences字段包含对应序列时才会统计")
