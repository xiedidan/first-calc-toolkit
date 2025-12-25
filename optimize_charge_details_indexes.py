"""
优化charge_details表索引

问题分析：
1. 表有1250万条记录，3GB大小
2. 查询使用 TO_CHAR(charge_time, 'YYYY-MM') 无法利用索引
3. 缺少复合索引覆盖常用查询模式

优化方案：
1. 添加year_month字段（预计算），避免函数转换
2. 创建复合索引覆盖常用查询模式
3. 或者使用表达式索引
"""

from sqlalchemy import create_engine, text
import time

DATABASE_URL = "postgresql://root:root@47.108.227.254:50016/hospital_value"
engine = create_engine(DATABASE_URL)


def analyze_query_performance():
    """分析当前查询性能"""
    with engine.connect() as conn:
        # 测试典型查询的执行计划
        print("=== 当前查询执行计划 ===")
        result = conn.execute(text("""
            EXPLAIN ANALYZE
            SELECT COUNT(*), SUM(amount)
            FROM charge_details
            WHERE business_type = '门诊'
              AND TO_CHAR(charge_time, 'YYYY-MM') = '2025-10'
              AND item_code IN (SELECT item_code FROM dimension_item_mappings WHERE hospital_id = 1 LIMIT 10)
        """))
        for row in result:
            print(row[0])


def add_year_month_column():
    """添加year_month预计算字段"""
    with engine.connect() as conn:
        # 检查字段是否已存在
        result = conn.execute(text("""
            SELECT column_name FROM information_schema.columns 
            WHERE table_name = 'charge_details' AND column_name = 'year_month'
        """))
        if result.fetchone():
            print("year_month字段已存在")
            return False
        
        print("添加year_month字段...")
        start = time.time()
        
        # 添加字段
        conn.execute(text("""
            ALTER TABLE charge_details 
            ADD COLUMN year_month VARCHAR(7)
        """))
        conn.commit()
        print(f"  字段添加完成: {time.time()-start:.1f}秒")
        
        # 更新数据（分批处理避免锁表太久）
        print("更新year_month数据（分批处理）...")
        batch_size = 500000
        total_updated = 0
        
        while True:
            start_batch = time.time()
            result = conn.execute(text(f"""
                UPDATE charge_details 
                SET year_month = TO_CHAR(charge_time, 'YYYY-MM')
                WHERE year_month IS NULL
                AND id IN (
                    SELECT id FROM charge_details 
                    WHERE year_month IS NULL 
                    LIMIT {batch_size}
                )
            """))
            conn.commit()
            
            updated = result.rowcount
            total_updated += updated
            print(f"  已更新 {total_updated} 条记录 ({time.time()-start_batch:.1f}秒)")
            
            if updated < batch_size:
                break
        
        print(f"数据更新完成，共 {total_updated} 条")
        return True


def create_optimized_indexes():
    """创建优化索引"""
    with engine.connect() as conn:
        indexes = [
            # 复合索引：业务类型 + 年月 + 项目代码
            ("idx_cd_type_month_item", 
             "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_cd_type_month_item ON charge_details (business_type, year_month, item_code)"),
            
            # 复合索引：年月 + 执行科室
            ("idx_cd_month_exec_dept",
             "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_cd_month_exec_dept ON charge_details (year_month, executing_dept_code)"),
            
            # 复合索引：年月 + 开单科室  
            ("idx_cd_month_presc_dept",
             "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_cd_month_presc_dept ON charge_details (year_month, prescribing_dept_code)"),
            
            # 执行科室索引（原来没有）
            ("idx_cd_exec_dept",
             "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_cd_exec_dept ON charge_details (executing_dept_code)"),
        ]
        
        for idx_name, idx_sql in indexes:
            print(f"创建索引 {idx_name}...")
            start = time.time()
            try:
                # CONCURRENTLY需要autocommit
                conn.execute(text("COMMIT"))
                conn.execute(text(idx_sql))
                print(f"  完成: {time.time()-start:.1f}秒")
            except Exception as e:
                if "already exists" in str(e):
                    print(f"  索引已存在")
                else:
                    print(f"  错误: {e}")


def create_expression_index():
    """创建表达式索引（备选方案，不需要添加字段）"""
    with engine.connect() as conn:
        print("创建表达式索引...")
        try:
            conn.execute(text("COMMIT"))
            conn.execute(text("""
                CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_cd_charge_time_month 
                ON charge_details (TO_CHAR(charge_time, 'YYYY-MM'))
            """))
            print("  表达式索引创建完成")
        except Exception as e:
            print(f"  错误: {e}")


def verify_optimization():
    """验证优化效果"""
    with engine.connect() as conn:
        print("\n=== 优化后查询执行计划 ===")
        result = conn.execute(text("""
            EXPLAIN ANALYZE
            SELECT COUNT(*), SUM(amount)
            FROM charge_details
            WHERE business_type = '门诊'
              AND year_month = '2025-10'
              AND item_code IN (SELECT item_code FROM dimension_item_mappings WHERE hospital_id = 1 LIMIT 10)
        """))
        for row in result:
            print(row[0])


def show_index_status():
    """显示索引状态"""
    with engine.connect() as conn:
        print("\n=== 当前索引列表 ===")
        result = conn.execute(text("""
            SELECT indexname, pg_size_pretty(pg_relation_size(indexname::regclass)) as size
            FROM pg_indexes 
            WHERE tablename = 'charge_details'
            ORDER BY indexname
        """))
        for row in result:
            print(f"  {row[0]}: {row[1]}")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        action = sys.argv[1]
        if action == "analyze":
            analyze_query_performance()
        elif action == "add_column":
            add_year_month_column()
        elif action == "create_indexes":
            create_optimized_indexes()
        elif action == "expression_index":
            create_expression_index()
        elif action == "verify":
            verify_optimization()
        elif action == "status":
            show_index_status()
        else:
            print(f"未知操作: {action}")
    else:
        print("用法: python optimize_charge_details_indexes.py <action>")
        print("可用操作:")
        print("  analyze          - 分析当前查询性能")
        print("  add_column       - 添加year_month预计算字段")
        print("  create_indexes   - 创建优化索引")
        print("  expression_index - 创建表达式索引（备选）")
        print("  verify           - 验证优化效果")
        print("  status           - 显示索引状态")
        print()
        print("推荐执行顺序:")
        print("  1. python optimize_charge_details_indexes.py analyze")
        print("  2. python optimize_charge_details_indexes.py add_column")
        print("  3. python optimize_charge_details_indexes.py create_indexes")
        print("  4. python optimize_charge_details_indexes.py verify")
