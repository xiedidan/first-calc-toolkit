from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os

load_dotenv('backend/.env')
engine = create_engine(os.getenv('DATABASE_URL'))

with engine.connect() as conn:
    result = conn.execute(text("""
        SELECT accounting_unit_code, accounting_unit_name, his_code, his_name
        FROM departments 
        WHERE hospital_id = 1 
          AND (accounting_unit_name LIKE '%验光%' OR his_name LIKE '%验光%')
    """))
    print('医学验光相关科室:')
    for row in result:
        print(f'  核算单元代码: {row[0]}, 核算单元名称: {row[1]}, HIS代码: {row[2]}, HIS名称: {row[3]}')
