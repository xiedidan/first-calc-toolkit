"""
生成成本基准值数据
为模型版本23生成"不收费卫生材料费"和"折旧（风险）费"两个维度的基准值
"""
import random
from decimal import Decimal
from sqlalchemy import create_engine, text
from datetime import datetime

# 数据库连接
DATABASE_URL = "postgresql://root:root@47.108.227.254:50016/hospital_value"
engine = create_engine(DATABASE_URL)

VERSION_ID = 23
VERSION_NAME = "2025年迭代版-宁波眼科v1.4"
HOSPITAL_ID = 1

def generate_benchmarks():
    """生成基准值数据"""
    with engine.connect() as conn:
        # 从 model_nodes 获取目标维度（材料费和折旧费）
        dim_result = conn.execute(text("""
            SELECT DISTINCT code, name 
            FROM model_nodes 
            WHERE version_id = :version_id 
              AND node_type = 'dimension' 
              AND (name LIKE '%材料%' OR name LIKE '%折旧%')
            ORDER BY code
        """), {"version_id": VERSION_ID})
        
        dimensions = [{"code": row[0], "name": row[1]} for row in dim_result.fetchall()]
        print(f"找到 {len(dimensions)} 个目标维度:")
        for dim in dimensions:
            print(f"  - {dim['code']}: {dim['name']}")
        
        # 获取所有科室
        result = conn.execute(text("""
            SELECT DISTINCT dept_code, dept_name 
            FROM cost_values 
            WHERE hospital_id = :hospital_id
            ORDER BY dept_code
        """), {"hospital_id": HOSPITAL_ID})
        
        departments = result.fetchall()
        print(f"\n找到 {len(departments)} 个科室")
        
        # 删除已有的基准值数据
        delete_sql = text("""
            DELETE FROM cost_benchmarks 
            WHERE version_id = :version_id 
              AND dimension_code IN (
                  SELECT code FROM model_nodes 
                  WHERE version_id = :version_id 
                    AND node_type = 'dimension' 
                    AND (name LIKE '%材料%' OR name LIKE '%折旧%')
              )
        """)
        result = conn.execute(delete_sql, {"version_id": VERSION_ID})
        deleted_count = result.rowcount
        conn.commit()
        print(f"删除了 {deleted_count} 条已有基准值记录\n")
        
        # 为每个科室和维度生成基准值
        records = []
        for dept in departments:
            dept_code = dept[0]
            dept_name = dept[1]
            
            for dim in dimensions:
                # 生成一个基础成本值（5000-50000之间）
                base_cost = random.uniform(5000, 50000)
                
                # 基准值在成本值基础上随机上下浮动15%以内
                fluctuation = random.uniform(-0.15, 0.15)
                benchmark_value = base_cost * (1 + fluctuation)
                
                records.append({
                    "hospital_id": HOSPITAL_ID,
                    "department_code": dept_code,
                    "department_name": dept_name,
                    "version_id": VERSION_ID,
                    "version_name": VERSION_NAME,
                    "dimension_code": dim["code"],
                    "dimension_name": dim["name"],
                    "benchmark_value": round(Decimal(str(benchmark_value)), 2)
                })
        
        print(f"生成 {len(records)} 条基准值记录")
        
        # 插入数据（使用 ON CONFLICT 更新已存在的记录）
        insert_sql = text("""
            INSERT INTO cost_benchmarks 
            (hospital_id, department_code, department_name, version_id, version_name, 
             dimension_code, dimension_name, benchmark_value, created_at, updated_at)
            VALUES 
            (:hospital_id, :department_code, :department_name, :version_id, :version_name,
             :dimension_code, :dimension_name, :benchmark_value, NOW(), NOW())
            ON CONFLICT (hospital_id, department_code, version_id, dimension_code)
            DO UPDATE SET
                department_name = EXCLUDED.department_name,
                version_name = EXCLUDED.version_name,
                dimension_name = EXCLUDED.dimension_name,
                benchmark_value = EXCLUDED.benchmark_value,
                updated_at = NOW()
        """)
        
        conn.execute(insert_sql, records)
        conn.commit()
        
        print("✓ 基准值数据插入成功")
        
        # 验证插入结果
        verify_sql = text("""
            SELECT dimension_name, COUNT(*) as count, 
                   MIN(benchmark_value) as min_val, 
                   MAX(benchmark_value) as max_val,
                   AVG(benchmark_value) as avg_val
            FROM cost_benchmarks
            WHERE version_id = :version_id
            GROUP BY dimension_name
        """)
        
        result = conn.execute(verify_sql, {"version_id": VERSION_ID})
        print("\n验证结果：")
        for row in result:
            print(f"  {row[0]}: {row[1]}条记录, 范围 {float(row[2]):.2f} - {float(row[3]):.2f}, 平均 {float(row[4]):.2f}")

if __name__ == "__main__":
    try:
        generate_benchmarks()
    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()
