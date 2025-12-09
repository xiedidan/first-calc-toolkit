"""验证权重调整是否正确应用"""
import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
from decimal import Decimal

load_dotenv('backend/.env')

DATABASE_URL = os.getenv('DATABASE_URL')
engine = create_engine(DATABASE_URL)

def verify_task(task_id: str):
    """验证指定任务的权重调整"""
    print(f"\n验证任务: {task_id}")
    print("=" * 80)
    
    with engine.connect() as conn:
        # 1. 检查叶子节点的权重
        print("\n1. 叶子维度节点（应该有original_weight）:")
        result = conn.execute(text("""
            SELECT 
                node_name,
                node_type,
                weight,
                original_weight,
                CASE 
                    WHEN original_weight IS NULL THEN '❌ 缺失'
                    WHEN original_weight = weight THEN '⚠️  未调整'
                    ELSE '✓ 已调整'
                END as status,
                CASE 
                    WHEN original_weight IS NOT NULL AND original_weight != weight 
                    THEN ROUND((weight / original_weight - 1) * 100, 2)
                    ELSE 0
                END as adjustment_pct
            FROM calculation_results
            WHERE task_id = :task_id
                AND node_type = 'dimension'
                AND workload > 0  -- 叶子节点
            ORDER BY node_name
            LIMIT 10
        """), {"task_id": task_id})
        
        rows = result.fetchall()
        if rows:
            for row in rows:
                print(f"  {row.node_name[:30]:30} | "
                      f"weight={float(row.weight):8.2f} | "
                      f"original={float(row.original_weight) if row.original_weight else 'NULL':8} | "
                      f"{row.status} {row.adjustment_pct:+.1f}%")
        else:
            print("  未找到叶子节点")
        
        # 2. 检查非叶子节点
        print("\n2. 非叶子节点（original_weight应该为NULL）:")
        result = conn.execute(text("""
            SELECT 
                node_name,
                node_type,
                weight,
                original_weight,
                CASE 
                    WHEN original_weight IS NULL THEN '✓ 正确'
                    ELSE '❌ 不应有值'
                END as status
            FROM calculation_results
            WHERE task_id = :task_id
                AND node_type IN ('sequence', 'dimension')
                AND workload = 0  -- 非叶子节点
            ORDER BY node_type, node_name
            LIMIT 10
        """), {"task_id": task_id})
        
        rows = result.fetchall()
        if rows:
            for row in rows:
                print(f"  {row.node_type:10} | {row.node_name[:30]:30} | "
                      f"original={str(row.original_weight) if row.original_weight else 'NULL':8} | "
                      f"{row.status}")
        else:
            print("  未找到非叶子节点")
        
        # 3. 统计调整情况
        print("\n3. 调整统计:")
        result = conn.execute(text("""
            SELECT 
                COUNT(*) as total_dimensions,
                COUNT(CASE WHEN original_weight IS NOT NULL THEN 1 END) as has_original,
                COUNT(CASE WHEN original_weight IS NOT NULL AND original_weight != weight THEN 1 END) as adjusted,
                COUNT(CASE WHEN original_weight IS NOT NULL AND original_weight = weight THEN 1 END) as not_adjusted
            FROM calculation_results
            WHERE task_id = :task_id
                AND node_type = 'dimension'
                AND workload > 0
        """), {"task_id": task_id})
        
        stats = result.fetchone()
        if stats:
            print(f"  总维度数: {stats.total_dimensions}")
            print(f"  有original_weight: {stats.has_original}")
            print(f"  已调整: {stats.adjusted}")
            print(f"  未调整: {stats.not_adjusted}")
            
            if stats.adjusted == 0 and stats.total_dimensions > 0:
                print("\n  ⚠️  警告: 没有维度被调整！可能原因:")
                print("     - 没有配置导向规则")
                print("     - 没有导向实际值数据")
                print("     - 导向比例未匹配到阶梯")
        
        # 4. 检查导向调整明细
        print("\n4. 导向调整明细:")
        result = conn.execute(text("""
            SELECT 
                COUNT(*) as total_records,
                COUNT(CASE WHEN is_adjusted = TRUE THEN 1 END) as adjusted_count,
                COUNT(CASE WHEN adjustment_reason IS NOT NULL THEN 1 END) as failed_count
            FROM orientation_adjustment_details
            WHERE task_id = :task_id
        """), {"task_id": task_id})
        
        detail_stats = result.fetchone()
        if detail_stats and detail_stats.total_records > 0:
            print(f"  总记录数: {detail_stats.total_records}")
            print(f"  成功调整: {detail_stats.adjusted_count}")
            print(f"  调整失败: {detail_stats.failed_count}")
            
            # 显示失败原因
            if detail_stats.failed_count > 0:
                print("\n  失败原因分布:")
                result = conn.execute(text("""
                    SELECT 
                        adjustment_reason,
                        COUNT(*) as count
                    FROM orientation_adjustment_details
                    WHERE task_id = :task_id
                        AND adjustment_reason IS NOT NULL
                    GROUP BY adjustment_reason
                    ORDER BY count DESC
                """), {"task_id": task_id})
                
                for row in result:
                    print(f"    - {row.adjustment_reason}: {row.count}")
        else:
            print("  ⚠️  未找到导向调整明细记录")
            print("     可能Step 3a未执行或执行失败")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        task_id = sys.argv[1]
    else:
        print("请提供任务ID:")
        print("  python verify_weight_adjustment.py <task_id>")
        print("\n或直接输入任务ID: ", end='')
        task_id = input().strip()
    
    if not task_id:
        print("错误: 未提供任务ID")
        exit(1)
    
    verify_task(task_id)
    
    print("\n" + "=" * 80)
    print("验证完成")
