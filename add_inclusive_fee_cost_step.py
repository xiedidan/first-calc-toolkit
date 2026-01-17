"""
添加内含式收费成本计算步骤到工作流39

功能：
1. 从 dim_inclusive_fees 获取内含式收费项目及其成本
2. 关联 charge_details 中的收费记录
3. 按科室汇总内含式收费金额
4. 累加到 cost_values 表的"不收费卫生材料费"维度（dim-*-cost-mat）

执行位置：在"成本直接扣减"步骤之前（sort_order = 3.50）
"""
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os

load_dotenv('backend/.env')
engine = create_engine(os.getenv('DATABASE_URL'))

# 新步骤的SQL模板
INCLUSIVE_FEE_COST_SQL = """-- =============================================================================
-- 内含式收费成本计算
-- =============================================================================
-- 功能: 将内含式收费项目的成本写入科室的"不收费卫生材料费"
-- 算法: 
--   1. 先清空当期所有科室的 material_cost
--   2. 从 dim_inclusive_fees 获取内含式收费项目及其单位成本
--   3. 关联 charge_details 中的收费记录，计算每笔收费的内含成本
--   4. 按科室汇总后写入 cost_reports.material_cost
-- 注意: 此步骤必须在"成本直接扣减"步骤之前执行
-- =============================================================================

-- 第一步：清空当期所有科室的材料费
UPDATE cost_reports
SET material_cost = 0,
    updated_at = NOW()
WHERE hospital_id = {hospital_id}
    AND period = '{period}';

-- 第二步：计算并写入内含式收费成本
WITH inclusive_cost_summary AS (
    SELECT 
        d.accounting_unit_code as dept_code,
        SUM(cd.quantity * dif.cost) as inclusive_cost
    FROM charge_details cd
    JOIN dim_inclusive_fees dif ON cd.item_code = dif.item_code
    JOIN departments d ON cd.prescribing_dept_code = d.his_code 
        AND d.hospital_id = {hospital_id}
    WHERE cd.year_month = '{period}'
        AND d.is_active = true
        AND d.accounting_unit_code IS NOT NULL
    GROUP BY d.accounting_unit_code
)
UPDATE cost_reports cr
SET material_cost = ics.inclusive_cost,
    updated_at = NOW()
FROM inclusive_cost_summary ics
WHERE cr.hospital_id = {hospital_id}
    AND cr.period = '{period}'
    AND cr.department_code = ics.dept_code;

-- 返回更新统计
SELECT 
    (SELECT COUNT(*) FROM dim_inclusive_fees) as inclusive_fee_items,
    (SELECT COUNT(*) FROM charge_details cd 
     JOIN dim_inclusive_fees dif ON cd.item_code = dif.item_code 
     WHERE cd.year_month = '{period}') as matched_charges,
    (SELECT SUM(cd.quantity * dif.cost) FROM charge_details cd 
     JOIN dim_inclusive_fees dif ON cd.item_code = dif.item_code 
     JOIN departments d ON cd.prescribing_dept_code = d.his_code AND d.hospital_id = {hospital_id}
     WHERE cd.year_month = '{period}' AND d.is_active = true) as total_inclusive_cost;
"""

def add_inclusive_fee_cost_step():
    """添加内含式收费成本计算步骤"""
    with engine.begin() as conn:
        # 1. 检查步骤是否已存在
        result = conn.execute(text("""
            SELECT id, sort_order, name FROM calculation_steps 
            WHERE workflow_id = 39 AND name = '内含式收费成本计算'
        """))
        existing = result.fetchone()
        
        if existing:
            print(f"步骤已存在: ID={existing[0]}, sort_order={existing[1]}")
            # 更新SQL
            conn.execute(text("""
                UPDATE calculation_steps 
                SET code_content = :sql, updated_at = NOW()
                WHERE id = :step_id
            """), {"sql": INCLUSIVE_FEE_COST_SQL, "step_id": existing[0]})
            print("已更新SQL内容")
            return existing[0]
        
        # 2. 获取当前最大步骤ID
        result = conn.execute(text("SELECT MAX(id) FROM calculation_steps"))
        max_id = result.fetchone()[0] or 0
        new_id = max_id + 1
        
        # 3. 插入新步骤（sort_order = 3.50，在成本直接扣减之前）
        conn.execute(text("""
            INSERT INTO calculation_steps (
                id, workflow_id, sort_order, name, description, 
                code_type, code_content, is_enabled, created_at, updated_at
            ) VALUES (
                :id, 39, 3.50, '内含式收费成本计算', 
                '将内含式收费项目的成本累加到科室的不收费卫生材料费维度',
                'sql', :sql, true, NOW(), NOW()
            )
        """), {"id": new_id, "sql": INCLUSIVE_FEE_COST_SQL})
        
        print(f"已添加新步骤: ID={new_id}, sort_order=3.50")
        
        # 4. 显示更新后的步骤列表
        print("\n工作流39当前步骤:")
        result = conn.execute(text("""
            SELECT id, sort_order, name FROM calculation_steps 
            WHERE workflow_id = 39 ORDER BY sort_order
        """))
        for row in result:
            print(f"  {row[1]:>5.2f} | ID={row[0]:>3} | {row[2]}")
        
        return new_id

def verify_data_structure():
    """验证数据结构和关联关系"""
    with engine.connect() as conn:
        print("\n" + "=" * 60)
        print("数据结构验证")
        print("=" * 60)
        
        # 1. dim_inclusive_fees 表数据
        result = conn.execute(text("SELECT COUNT(*) FROM dim_inclusive_fees"))
        count = result.fetchone()[0]
        print(f"\n1. dim_inclusive_fees 表: {count} 条记录")
        
        if count > 0:
            result = conn.execute(text("""
                SELECT item_code, item_name, cost FROM dim_inclusive_fees LIMIT 5
            """))
            print("   示例数据:")
            for row in result:
                print(f"     {row[0]} | {row[1]} | {row[2]}")
        
        # 2. 检查 charge_details 中匹配的记录
        result = conn.execute(text("""
            SELECT COUNT(*) FROM charge_details cd
            JOIN dim_inclusive_fees dif ON cd.item_code = dif.item_code
            WHERE cd.year_month = '2025-01'
        """))
        matched = result.fetchone()[0]
        print(f"\n2. charge_details 中匹配内含式收费的记录 (2025-01): {matched} 条")
        
        # 3. 检查 cost_values 中的材料费维度
        result = conn.execute(text("""
            SELECT dimension_code, COUNT(*), SUM(cost_value)
            FROM cost_values 
            WHERE hospital_id = 1 AND year_month = '2025-01'
            AND dimension_code LIKE '%-cost-mat'
            GROUP BY dimension_code
        """))
        print("\n3. cost_values 中的材料费维度 (2025-01):")
        for row in result:
            print(f"     {row[0]}: {row[1]} 条, 总计 {float(row[2]):,.2f}")

if __name__ == "__main__":
    print("=" * 60)
    print("添加内含式收费成本计算步骤")
    print("=" * 60)
    
    # 验证数据结构
    verify_data_structure()
    
    # 添加步骤
    print("\n" + "=" * 60)
    print("添加计算步骤")
    print("=" * 60)
    step_id = add_inclusive_fee_cost_step()
    
    print("\n完成！")
