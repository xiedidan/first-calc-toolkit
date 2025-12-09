"""
复制 orientation_benchmarks 表中 rule_id = 77 的记录，并将 rule_id 改为 75
"""
import os
from sqlalchemy import create_engine, text

# 从环境变量读取数据库连接
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://root:root@47.108.227.254:50016/hospital_value')

engine = create_engine(DATABASE_URL)

with engine.connect() as conn:
    # 开始事务
    trans = conn.begin()
    
    try:
        # 查询 rule_id = 77 的记录
        result = conn.execute(text("""
            SELECT hospital_id, department_code, department_name, 
                   benchmark_type, control_intensity, stat_start_date, 
                   stat_end_date, benchmark_value
            FROM orientation_benchmarks 
            WHERE rule_id = 77
        """))
        
        records = result.fetchall()
        print(f"找到 {len(records)} 条 rule_id = 77 的记录")
        
        # 插入新记录，rule_id 改为 75
        insert_count = 0
        for record in records:
            conn.execute(text("""
                INSERT INTO orientation_benchmarks 
                (hospital_id, rule_id, department_code, department_name, 
                 benchmark_type, control_intensity, stat_start_date, 
                 stat_end_date, benchmark_value, created_at, updated_at)
                VALUES 
                (:hospital_id, 75, :department_code, :department_name,
                 :benchmark_type, :control_intensity, :stat_start_date,
                 :stat_end_date, :benchmark_value, NOW(), NOW())
            """), {
                'hospital_id': record[0],
                'department_code': record[1],
                'department_name': record[2],
                'benchmark_type': record[3],
                'control_intensity': record[4],
                'stat_start_date': record[5],
                'stat_end_date': record[6],
                'benchmark_value': record[7]
            })
            insert_count += 1
            print(f"已复制: {record[2]} ({record[1]})")
        
        # 提交事务
        trans.commit()
        print(f"\n✓ 成功复制 {insert_count} 条记录，rule_id 已改为 75")
        
        # 验证结果
        result = conn.execute(text("""
            SELECT COUNT(*) FROM orientation_benchmarks WHERE rule_id = 75
        """))
        count = result.scalar()
        print(f"✓ 验证: rule_id = 75 的记录总数为 {count}")
        
    except Exception as e:
        trans.rollback()
        print(f"✗ 错误: {e}")
        raise
