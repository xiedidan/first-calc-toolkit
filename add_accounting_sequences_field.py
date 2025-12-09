"""
直接通过SQL添加核算序列字段到科室表
"""
import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# 加载环境变量
load_dotenv('backend/.env')

# 获取数据库连接
DATABASE_URL = os.getenv('DATABASE_URL')
engine = create_engine(DATABASE_URL)

def add_accounting_sequences_field():
    """添加核算序列字段"""
    with engine.connect() as conn:
        # 检查字段是否已存在
        check_sql = """
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = 'departments' 
        AND column_name = 'accounting_sequences'
        """
        result = conn.execute(text(check_sql))
        exists = result.fetchone() is not None
        
        if exists:
            print("字段 accounting_sequences 已存在，跳过添加")
            return
        
        # 添加字段
        print("正在添加 accounting_sequences 字段...")
        add_column_sql = """
        ALTER TABLE departments 
        ADD COLUMN accounting_sequences VARCHAR(20)[]
        """
        conn.execute(text(add_column_sql))
        
        # 添加注释
        comment_sql = """
        COMMENT ON COLUMN departments.accounting_sequences 
        IS '核算序列（可多选：医生、护理、医技）'
        """
        conn.execute(text(comment_sql))
        
        # 创建GIN索引
        print("正在创建索引...")
        index_sql = """
        CREATE INDEX IF NOT EXISTS ix_departments_accounting_sequences 
        ON departments USING gin(accounting_sequences)
        """
        conn.execute(text(index_sql))
        
        # 提交事务
        conn.commit()
        
        print("✓ 成功添加 accounting_sequences 字段")
        print("✓ 成功添加字段注释")
        print("✓ 成功创建GIN索引")

if __name__ == '__main__':
    try:
        add_accounting_sequences_field()
        print("\n字段添加完成！")
    except Exception as e:
        print(f"\n错误: {e}")
        import traceback
        traceback.print_exc()
