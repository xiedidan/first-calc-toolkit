"""
生成成本值数据
为"人员经费"和"其他费用"两个维度生成成本数据
"""
import random
from decimal import Decimal
from sqlalchemy import create_engine, text
from datetime import datetime

# 数据库连接
DATABASE_URL = "postgresql://root:root@47.108.227.254:50016/hospital_value"
engine = create_engine(DATABASE_URL)

HOSPITAL_ID = 1
YEAR_MONTH = "2025-10"

# 成本维度映射（从 model_nodes 获取）
COST_DIMENSIONS = {
    'dim-doc-cost-hr': '人员经费',
    'dim-nur-cost-hr': '人员经费',
    'dim-tech-cost-hr': '人员经费',
    'dim-doc-cost-other': '其他费用',
    'dim-nur-cost-other': '其他费用',
    'dim-tech-cost-other': '其他费用',
}

def generate_cost_values():
    """生成成本值数据"""
    with engine.connect() as conn:
        # 获取所有科室
        result = conn.execute(text("""
            SELECT his_code, his_name 
            FROM departments 
            WHERE hospital_id = :hospital_id 
              AND is_active = TRUE
            ORDER BY his_code
        """), {"hospital_id": HOSPITAL_ID})
        
        departments = result.fetchall()
        print(f"找到 {len(departments)} 个科室")
        
        # 为每个科室和维度生成成本值
        records = []
        for dept in departments:
            dept_code = dept[0]
            dept_name = dept[1]
            
            for dim_code, dim_name in COST_DIMENSIONS.items():
                # 生成成本值（10000-100000之间）
                cost_value = random.uniform(10000, 100000)
                
                records.append({
                    "hospital_id": HOSPITAL_ID,
                    "year_month": YEAR_MONTH,
                    "dept_code": dept_code,
                    "dept_name": dept_name,
                    "dimension_code": dim_code,
                    "dimension_name": dim_name,
                    "cost_value": round(Decimal(str(cost_value)), 2)
                })
        
        print(f"生成 {len(records)} 条成本值记录")
        
        # 插入数据（使用 ON CONFLICT 处理重复）
        insert_sql = text("""
            INSERT INTO cost_values 
            (hospital_id, year_month, dept_code, dept_name, 
             dimension_code, dimension_name, cost_value, created_at, updated_at)
            VALUES 
            (:hospital_id, :year_month, :dept_code, :dept_name,
             :dimension_code, :dimension_name, :cost_value, NOW(), NOW())
            ON CONFLICT (hospital_id, year_month, dept_code, dimension_code)
            DO UPDATE SET
                dept_name = EXCLUDED.dept_name,
                dimension_name = EXCLUDED.dimension_name,
                cost_value = EXCLUDED.cost_value,
                updated_at = NOW()
        """)
        
        conn.execute(insert_sql, records)
        conn.commit()
        
        print("✓ 成本值数据插入成功")
        
        # 验证插入结果
        verify_sql = text("""
            SELECT dimension_name, COUNT(*) as count, 
                   MIN(cost_value) as min_val, 
                   MAX(cost_value) as max_val,
                   AVG(cost_value) as avg_val
            FROM cost_values
            WHERE hospital_id = :hospital_id
              AND year_month = :year_month
              AND dimension_name IN ('人员经费', '其他费用')
            GROUP BY dimension_name
        """)
        
        result = conn.execute(verify_sql, {
            "hospital_id": HOSPITAL_ID,
            "year_month": YEAR_MONTH
        })
        
        print("\n验证结果：")
        for row in result:
            print(f"  {row[0]}: {row[1]}条记录, 范围 {float(row[2]):.2f} - {float(row[3]):.2f}, 平均 {float(row[4]):.2f}")

if __name__ == "__main__":
    try:
        generate_cost_values()
    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()
