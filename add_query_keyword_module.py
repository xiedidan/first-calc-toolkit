"""
手动添加指标关键字提取模块到数据库
"""
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

os.environ.setdefault('DATABASE_URL', 'postgresql://postgres:ssPgSql123@47.108.227.254:50016/hospital_value')

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

DATABASE_URL = os.environ.get('DATABASE_URL')
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

def main():
    session = Session()
    
    try:
        # 检查模块是否已存在
        result = session.execute(text("""
            SELECT id, hospital_id FROM ai_prompt_modules 
            WHERE module_code = 'query_keyword'
        """))
        existing = result.fetchall()
        
        if existing:
            print(f"模块已存在: {existing}")
            return
        
        # 获取所有医疗机构ID
        result = session.execute(text("""
            SELECT DISTINCT hospital_id FROM ai_prompt_modules
        """))
        hospital_ids = [row[0] for row in result.fetchall()]
        
        print(f"找到 {len(hospital_ids)} 个医疗机构: {hospital_ids}")
        
        # 为每个医疗机构创建模块
        for hospital_id in hospital_ids:
            session.execute(text("""
                INSERT INTO ai_prompt_modules (
                    hospital_id, module_code, module_name, description,
                    temperature, placeholders, system_prompt, user_prompt,
                    created_at, updated_at
                ) VALUES (
                    :hospital_id, 'query_keyword', '智能问数-指标关键字提取',
                    '用于从用户自然语言查询中提取指标搜索关键词，提高指标口径查询的准确性',
                    0.1,
                    '[{"name": "user_query", "description": "用户查询内容"}]'::jsonb,
                    '你是一个关键词提取专家。你的任务是从用户的自然语言查询中提取用于搜索指标的关键词。

要求：
1. 提取与指标名称相关的核心词汇
2. 去除无关的修饰词（如"相关"、"有哪些"、"是什么"等）
3. 保留专业术语和业务词汇
4. 返回1-3个最相关的关键词
5. 必须返回JSON格式',
                    '请从以下用户查询中提取指标搜索关键词：

用户查询：{user_query}

请返回JSON格式：
{"keywords": ["关键词1", "关键词2"]}

注意：
- 只提取与指标名称相关的核心词汇
- 去除"相关"、"有哪些"、"是什么"、"指标"等无关词
- 如果查询本身就是关键词，直接返回
- 最多返回3个关键词',
                    NOW(), NOW()
                )
            """), {"hospital_id": hospital_id})
            print(f"为医疗机构 {hospital_id} 创建模块成功")
        
        session.commit()
        print("完成！")
        
    except Exception as e:
        session.rollback()
        print(f"错误: {e}")
        raise
    finally:
        session.close()

if __name__ == "__main__":
    main()
