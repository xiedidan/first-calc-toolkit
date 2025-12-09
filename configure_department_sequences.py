"""
批量配置科室核算序列的辅助脚本
"""
import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv('backend/.env')
DATABASE_URL = os.getenv('DATABASE_URL')
engine = create_engine(DATABASE_URL)

def configure_sequences():
    """批量配置科室核算序列"""
    
    with engine.connect() as conn:
        # 1. 查看当前配置情况
        print("="*80)
        print("当前科室核算序列配置情况")
        print("="*80)
        
        result = conn.execute(text("""
            SELECT 
                COUNT(*) as total,
                COUNT(CASE WHEN accounting_sequences IS NOT NULL 
                      AND array_length(accounting_sequences, 1) > 0 THEN 1 END) as configured,
                COUNT(CASE WHEN accounting_sequences IS NULL 
                      OR array_length(accounting_sequences, 1) = 0 THEN 1 END) as unconfigured
            FROM departments
            WHERE is_active = TRUE
        """))
        stats = result.fetchone()
        print(f"总科室数: {stats[0]}")
        print(f"已配置: {stats[1]}")
        print(f"未配置: {stats[2]}")
        
        # 2. 显示未配置的科室
        print("\n" + "="*80)
        print("未配置核算序列的科室")
        print("="*80)
        
        result = conn.execute(text("""
            SELECT id, his_code, his_name
            FROM departments
            WHERE (accounting_sequences IS NULL 
                   OR array_length(accounting_sequences, 1) = 0)
              AND is_active = TRUE
            ORDER BY his_code
            LIMIT 20
        """))
        
        unconfigured = result.fetchall()
        if unconfigured:
            for dept in unconfigured:
                print(f"ID: {dept[0]:4d} | 代码: {dept[1]:10s} | 名称: {dept[2]}")
            if len(unconfigured) == 20:
                print("... (仅显示前20条)")
        else:
            print("所有科室都已配置核算序列")
        
        # 3. 提供配置建议
        print("\n" + "="*80)
        print("配置建议")
        print("="*80)
        print("""
根据科室名称特征，建议以下配置规则：

1. 临床科室（内科、外科等）:
   - 核算序列: ['医生', '护理']
   - 示例: 内科、外科、妇产科、儿科等

2. 医技科室（检验、影像等）:
   - 核算序列: ['医技']
   - 示例: 检验科、影像科、超声科、病理科、药剂科等

3. 综合科室（急诊、ICU等）:
   - 核算序列: ['医生', '护理', '医技']
   - 示例: 急诊科、ICU、手术室等

4. 行政后勤科室:
   - 核算序列: [] (空数组，不参与统计)
   - 示例: 院办、财务科、总务科等
        """)
        
        # 4. 询问是否执行自动配置
        print("\n" + "="*80)
        print("自动配置选项")
        print("="*80)
        print("1. 配置临床科室（包含'科'但不包含医技关键词）")
        print("2. 配置医技科室（包含检验、影像、超声、病理、药剂等关键词）")
        print("3. 配置综合科室（急诊、ICU、手术室）")
        print("4. 查看配置预览（不执行）")
        print("0. 退出")
        
        choice = input("\n请选择操作 (0-4): ").strip()
        
        if choice == '1':
            configure_clinical_departments(conn)
        elif choice == '2':
            configure_medical_tech_departments(conn)
        elif choice == '3':
            configure_comprehensive_departments(conn)
        elif choice == '4':
            preview_configuration(conn)
        elif choice == '0':
            print("退出配置")
        else:
            print("无效选择")

def configure_clinical_departments(conn):
    """配置临床科室"""
    print("\n配置临床科室...")
    
    # 预览
    result = conn.execute(text("""
        SELECT id, his_code, his_name
        FROM departments
        WHERE (accounting_sequences IS NULL OR array_length(accounting_sequences, 1) = 0)
          AND is_active = TRUE
          AND his_name LIKE '%科'
          AND his_name NOT LIKE '%检验%'
          AND his_name NOT LIKE '%影像%'
          AND his_name NOT LIKE '%超声%'
          AND his_name NOT LIKE '%病理%'
          AND his_name NOT LIKE '%药剂%'
          AND his_name NOT LIKE '%放射%'
    """))
    
    depts = result.fetchall()
    if not depts:
        print("没有符合条件的科室")
        return
    
    print(f"\n将为以下 {len(depts)} 个科室配置核算序列 ['医生', '护理']:")
    for dept in depts[:10]:
        print(f"  - {dept[2]} ({dept[1]})")
    if len(depts) > 10:
        print(f"  ... 还有 {len(depts) - 10} 个科室")
    
    confirm = input("\n确认执行? (y/n): ").strip().lower()
    if confirm == 'y':
        conn.execute(text("""
            UPDATE departments 
            SET accounting_sequences = ARRAY['医生', '护理']
            WHERE (accounting_sequences IS NULL OR array_length(accounting_sequences, 1) = 0)
              AND is_active = TRUE
              AND his_name LIKE '%科'
              AND his_name NOT LIKE '%检验%'
              AND his_name NOT LIKE '%影像%'
              AND his_name NOT LIKE '%超声%'
              AND his_name NOT LIKE '%病理%'
              AND his_name NOT LIKE '%药剂%'
              AND his_name NOT LIKE '%放射%'
        """))
        conn.commit()
        print(f"✓ 已配置 {len(depts)} 个临床科室")
    else:
        print("已取消")

def configure_medical_tech_departments(conn):
    """配置医技科室"""
    print("\n配置医技科室...")
    
    # 预览
    result = conn.execute(text("""
        SELECT id, his_code, his_name
        FROM departments
        WHERE (accounting_sequences IS NULL OR array_length(accounting_sequences, 1) = 0)
          AND is_active = TRUE
          AND (his_name LIKE '%检验%'
               OR his_name LIKE '%影像%'
               OR his_name LIKE '%超声%'
               OR his_name LIKE '%病理%'
               OR his_name LIKE '%药剂%'
               OR his_name LIKE '%放射%'
               OR his_name LIKE '%CT%'
               OR his_name LIKE '%MRI%'
               OR his_name LIKE '%X光%')
    """))
    
    depts = result.fetchall()
    if not depts:
        print("没有符合条件的科室")
        return
    
    print(f"\n将为以下 {len(depts)} 个科室配置核算序列 ['医技']:")
    for dept in depts:
        print(f"  - {dept[2]} ({dept[1]})")
    
    confirm = input("\n确认执行? (y/n): ").strip().lower()
    if confirm == 'y':
        conn.execute(text("""
            UPDATE departments 
            SET accounting_sequences = ARRAY['医技']
            WHERE (accounting_sequences IS NULL OR array_length(accounting_sequences, 1) = 0)
              AND is_active = TRUE
              AND (his_name LIKE '%检验%'
                   OR his_name LIKE '%影像%'
                   OR his_name LIKE '%超声%'
                   OR his_name LIKE '%病理%'
                   OR his_name LIKE '%药剂%'
                   OR his_name LIKE '%放射%'
                   OR his_name LIKE '%CT%'
                   OR his_name LIKE '%MRI%'
                   OR his_name LIKE '%X光%')
        """))
        conn.commit()
        print(f"✓ 已配置 {len(depts)} 个医技科室")
    else:
        print("已取消")

def configure_comprehensive_departments(conn):
    """配置综合科室"""
    print("\n配置综合科室...")
    
    # 预览
    result = conn.execute(text("""
        SELECT id, his_code, his_name
        FROM departments
        WHERE (accounting_sequences IS NULL OR array_length(accounting_sequences, 1) = 0)
          AND is_active = TRUE
          AND (his_name LIKE '%急诊%'
               OR his_name LIKE '%ICU%'
               OR his_name LIKE '%重症%'
               OR his_name LIKE '%手术室%')
    """))
    
    depts = result.fetchall()
    if not depts:
        print("没有符合条件的科室")
        return
    
    print(f"\n将为以下 {len(depts)} 个科室配置核算序列 ['医生', '护理', '医技']:")
    for dept in depts:
        print(f"  - {dept[2]} ({dept[1]})")
    
    confirm = input("\n确认执行? (y/n): ").strip().lower()
    if confirm == 'y':
        conn.execute(text("""
            UPDATE departments 
            SET accounting_sequences = ARRAY['医生', '护理', '医技']
            WHERE (accounting_sequences IS NULL OR array_length(accounting_sequences, 1) = 0)
              AND is_active = TRUE
              AND (his_name LIKE '%急诊%'
                   OR his_name LIKE '%ICU%'
                   OR his_name LIKE '%重症%'
                   OR his_name LIKE '%手术室%')
        """))
        conn.commit()
        print(f"✓ 已配置 {len(depts)} 个综合科室")
    else:
        print("已取消")

def preview_configuration(conn):
    """预览配置情况"""
    print("\n" + "="*80)
    print("配置预览")
    print("="*80)
    
    # 按序列统计
    result = conn.execute(text("""
        SELECT 
            unnest(accounting_sequences) as sequence,
            COUNT(*) as dept_count
        FROM departments
        WHERE accounting_sequences IS NOT NULL
          AND is_active = TRUE
        GROUP BY sequence
        ORDER BY sequence
    """))
    
    print("\n各序列的科室数量:")
    for row in result:
        print(f"  {row[0]}: {row[1]} 个科室")
    
    # 显示部分已配置科室
    print("\n已配置科室示例:")
    result = conn.execute(text("""
        SELECT his_name, accounting_sequences
        FROM departments
        WHERE accounting_sequences IS NOT NULL
          AND array_length(accounting_sequences, 1) > 0
          AND is_active = TRUE
        ORDER BY his_name
        LIMIT 10
    """))
    
    for row in result:
        sequences = ', '.join(row[1]) if row[1] else '无'
        print(f"  {row[0]}: [{sequences}]")

if __name__ == '__main__':
    print("科室核算序列配置工具")
    print("="*80)
    try:
        configure_sequences()
    except Exception as e:
        print(f"\n错误: {e}")
        import traceback
        traceback.print_exc()
