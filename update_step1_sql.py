#!/usr/bin/env python3
"""
更新步骤1的SQL代码到数据库
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session

# 数据库连接
DATABASE_URL = "postgresql://admin:admin123@localhost:5432/hospital_value"
engine = create_engine(DATABASE_URL)

# 读取SQL文件
with open('backend/standard_workflow_templates/step1_dimension_catalog.sql', 'r', encoding='utf-8') as f:
    sql_content = f.read()

# 更新数据库
with Session(engine) as session:
    try:
        # 更新步骤1的SQL代码
        result = session.execute(
            text("UPDATE calculation_steps SET code_content = :sql, updated_at = NOW() WHERE id = 65"),
            {"sql": sql_content}
        )
        session.commit()
        print(f"✅ 步骤1 SQL更新成功，影响行数: {result.rowcount}")
        
        # 验证更新
        result = session.execute(
            text("SELECT id, name, LENGTH(code_content) as sql_length FROM calculation_steps WHERE id = 65")
        )
        row = result.fetchone()
        if row:
            print(f"✅ 验证: ID={row[0]}, 名称={row[1]}, SQL长度={row[2]}")
        else:
            print("❌ 验证失败: 未找到步骤记录")
        
    except Exception as e:
        session.rollback()
        print(f"❌ 更新失败: {e}")
        sys.exit(1)

print("\n✅ 步骤1 SQL代码已更新到数据库")
