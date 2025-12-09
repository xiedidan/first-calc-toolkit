"""验证计算流程32的科室代码更新"""
import os
import re
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv('backend/.env')
DATABASE_URL = os.getenv('DATABASE_URL')
engine = create_engine(DATABASE_URL)

def verify_step(step_id, step_name):
    with engine.connect() as conn:
        result = conn.execute(text('SELECT code_content FROM calculation_steps WHERE id = :id'), {"id": step_id})
        sql = result.fetchone()[0]
        
        # 分割INSERT块
        blocks = sql.split('INSERT INTO calculation_results')
        
        print(f"\n{step_name} (Step {step_id}):")
        print("=" * 70)
        
        for block in blocks[1:]:
            # 找维度代码
            dim_match = re.search(r"mn\.code\s*(LIKE|=)\s*'([^']+)'", block)
            # 找科室代码
            dept_match = re.search(r'cd\.(executing_dept_code|prescribing_dept_code)', block)
            if dim_match and dept_match:
                dim_code = dim_match.group(2)
                dept_code = dept_match.group(1)
                marker = "<<< 开单科室" if dept_code == "prescribing_dept_code" else ""
                print(f"  {dim_code:35} -> {dept_code:25} {marker}")

if __name__ == "__main__":
    print("计算流程32 科室代码使用验证")
    print("=" * 70)
    print("规则: 医生诊断维度(eval)用开单科室, 其他用执行科室")
    
    verify_step(123, "医生业务价值计算")
    verify_step(124, "护理业务价值计算")
    verify_step(125, "医技业务价值计算")
