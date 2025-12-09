import os
from sqlalchemy import create_engine, text, inspect
from dotenv import load_dotenv

load_dotenv('backend/.env')
DATABASE_URL = os.getenv('DATABASE_URL')
engine = create_engine(DATABASE_URL)

with engine.connect() as conn:
    inspector = inspect(engine)
    columns = inspector.get_columns('dimension_item_mappings')
    
    print("=== dimension_item_mappings 表结构 ===")
    for col in columns:
        print(f"  - {col['name']}: {col['type']}")
