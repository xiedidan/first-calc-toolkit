"""检查步骤SQL"""
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), 'backend', '.env'))

DATABASE_URL = os.getenv('DATABASE_URL')
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()

result = session.execute(text("SELECT code_content FROM calculation_steps WHERE id = 160"))
row = result.fetchone()
if row:
    sql = row[0]
    print("步骤160的SQL内容:")
    print("=" * 60)
    print(sql)
    print("=" * 60)
    
    # 检查关键字
    print("\n关键字检查:")
    print(f"  包含 'accounting_unit_code': {'accounting_unit_code' in sql}")
    print(f"  包含 'his_code': {'his_code' in sql}")

session.close()
