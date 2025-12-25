"""
修复charge_details表的year_month字段时区问题

问题：
- 数据库时区是GMT（UTC）
- charge_time存储的是UTC时间
- year_month应该基于中国时间（UTC+8）计算

解决方案：
- 使用 charge_time + INTERVAL '8 hours' 转换为中国时间
- 重新计算year_month字段
"""

from sqlalchemy import create_engine, text
import time

DATABASE_URL = "postgresql://root:root@47.108.227.254:50016/hospital_value"
engine = create_engine(DATABASE_URL)


def analyze_timezone_issue():
    """分析时区问题影响范围"""
    with engine.connect() as conn:
        print("=== 时区问题分析 ===")
        
        # 检查受影响的记录数
        result = conn.execute(text("""
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN year_month != TO_CHAR(charge_time + INTERVAL '8 hours', 'YYYY-MM') THEN 1 ELSE 0 END) as affected
            FROM charge_details
            WHERE year_month IS NOT NULL
        """))
        row = result.fetchone()
        print(f"总记录数: {row[0]:,}")
        print(f"受影响记录数: {row[1]:,}")
        print(f"影响比例: {row[1]/row[0]*100:.2f}%")
        
        # 按月份统计影响
        print("\n=== 按月份统计受影响记录 ===")
        result = conn.execute(text("""
            SELECT 
                year_month as old_month,
                TO_CHAR(charge_time + INTERVAL '8 hours', 'YYYY-MM') as correct_month,
                COUNT(*) as cnt
            FROM charge_details
            WHERE year_month != TO_CHAR(charge_time + INTERVAL '8 hours', 'YYYY-MM')
              AND year_month IS NOT NULL
            GROUP BY year_month, TO_CHAR(charge_time + INTERVAL '8 hours', 'YYYY-MM')
            ORDER BY year_month, correct_month
        """))
        
        print(f"{'原月份':<12} {'正确月份':<12} {'记录数':>10}")
        print("-" * 40)
        for row in result:
            print(f"{row[0]:<12} {row[1]:<12} {row[2]:>10,}")


def fix_year_month_timezone():
    """修复year_month字段的时区问题"""
    with engine.connect() as conn:
        print("=== 修复year_month时区问题 ===")
        
        # 统计需要修复的记录
        result = conn.execute(text("""
            SELECT COUNT(*) FROM charge_details
            WHERE year_month IS NULL 
               OR year_month != TO_CHAR(charge_time + INTERVAL '8 hours', 'YYYY-MM')
        """))
        total = result.fetchone()[0]
        print(f"需要修复的记录数: {total:,}")
        
        if total == 0:
            print("无需修复")
            return
        
        # 分批更新
        batch_size = 500000
        updated = 0
        
        while updated < total:
            start = time.time()
            result = conn.execute(text(f"""
                UPDATE charge_details 
                SET year_month = TO_CHAR(charge_time + INTERVAL '8 hours', 'YYYY-MM')
                WHERE id IN (
                    SELECT id FROM charge_details 
                    WHERE year_month IS NULL 
                       OR year_month != TO_CHAR(charge_time + INTERVAL '8 hours', 'YYYY-MM')
                    LIMIT {batch_size}
                )
            """))
            conn.commit()
            
            batch_updated = result.rowcount
            updated += batch_updated
            print(f"  已更新 {updated:,} / {total:,} ({time.time()-start:.1f}秒)")
            
            if batch_updated < batch_size:
                break
        
        print(f"\n修复完成，共更新 {updated:,} 条记录")


def verify_fix():
    """验证修复结果"""
    with engine.connect() as conn:
        print("\n=== 验证修复结果 ===")
        
        # 检查是否还有不一致的记录
        result = conn.execute(text("""
            SELECT COUNT(*) FROM charge_details
            WHERE year_month != TO_CHAR(charge_time + INTERVAL '8 hours', 'YYYY-MM')
        """))
        remaining = result.fetchone()[0]
        
        if remaining == 0:
            print("验证通过：所有记录的year_month已正确")
        else:
            print(f"警告：还有 {remaining:,} 条记录不一致")
        
        # 显示月份分布
        print("\n=== 修复后月份分布 ===")
        result = conn.execute(text("""
            SELECT year_month, COUNT(*) as cnt 
            FROM charge_details 
            GROUP BY year_month 
            ORDER BY year_month DESC
            LIMIT 15
        """))
        
        for row in result:
            print(f"  {row[0]}: {row[1]:,}")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        action = sys.argv[1]
        if action == "analyze":
            analyze_timezone_issue()
        elif action == "fix":
            fix_year_month_timezone()
            verify_fix()
        elif action == "verify":
            verify_fix()
        else:
            print(f"未知操作: {action}")
    else:
        print("用法: python fix_timezone_year_month.py <action>")
        print("可用操作:")
        print("  analyze - 分析时区问题影响范围")
        print("  fix     - 修复year_month字段")
        print("  verify  - 验证修复结果")
