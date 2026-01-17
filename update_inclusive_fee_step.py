"""
更新内含式收费成本计算步骤的SQL

修改：将内含式收费成本累加到 cost_reports.material_cost，
而不是 cost_values 表
"""
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os

load_dotenv('backend/.env')
engine = create_engine(os.getenv('DATABASE_URL'))

# 新的SQL模板 - 更新 cost_reports 表
INCLUSIVE_FEE_COST_SQL = """-- =============================================================================
-- 内含式收费成本计算
-- =============================================================================
-- 功能: 将内含式收费项目的成本写入科室的"不收费卫生材料费"
-- 算法: 
--   1. 先清空当期所有科室的 material_cost
--   2. 从 dim_inclusive_fees 获取内含式收费项目及其单位成本
--   3. 关联 charge_details 中的收费记录，每条记录对应一次手术
--   4. 按科室汇总后写入 cost_reports.material_cost
-- 注意: 
--   - 此步骤必须在"成本直接扣减"步骤之前执行
--   - 成本按收费记录条数计算，不乘以quantity（quantity是收费数量，不是手术次数）
-- =============================================================================

-- 第一步：清空当期所有科室的材料费
UPDATE cost_reports
SET material_cost = 0,
    updated_at = NOW()
WHERE hospital_id = {hospital_id}
    AND period = '{period}';

-- 第二步：计算并写入内含式收费成本（每条记录计一次成本）
WITH inclusive_cost_summary AS (
    SELECT 
        d.accounting_unit_code as dept_code,
        SUM(dif.cost) as inclusive_cost
    FROM charge_details cd
    JOIN dim_inclusive_fees dif ON cd.item_code = dif.item_code
    JOIN departments d ON cd.prescribing_dept_code = d.his_code 
        AND d.hospital_id = {hospital_id}
    WHERE cd.year_month = '{period}'
        AND d.is_active = true
        AND d.accounting_unit_code IS NOT NULL
        AND cd.quantity > 0
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
     WHERE cd.year_month = '{period}' AND cd.quantity > 0) as matched_charges,
    (SELECT SUM(dif.cost) FROM charge_details cd 
     JOIN dim_inclusive_fees dif ON cd.item_code = dif.item_code 
     JOIN departments d ON cd.prescribing_dept_code = d.his_code AND d.hospital_id = {hospital_id}
     WHERE cd.year_month = '{period}' AND d.is_active = true AND cd.quantity > 0) as total_inclusive_cost;
"""

def update_step():
    """更新步骤SQL"""
    with engine.begin() as conn:
        conn.execute(text("""
            UPDATE calculation_steps 
            SET code_content = :sql, 
                description = '将内含式收费项目的成本累加到cost_reports的material_cost字段',
                updated_at = NOW()
            WHERE id = 182
        """), {"sql": INCLUSIVE_FEE_COST_SQL})
        print("已更新步骤182的SQL")
        
        # 验证
        result = conn.execute(text("SELECT LEFT(code_content, 200) FROM calculation_steps WHERE id = 182"))
        print("\nSQL预览:")
        print(result.fetchone()[0])

if __name__ == "__main__":
    update_step()
