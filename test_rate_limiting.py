"""
测试API调用限流和统计功能
"""
import sys
import os
from datetime import datetime, timedelta

# 添加backend目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.ai_config import AIConfig
from app.models.api_usage_log import APIUsageLog
from app.services.ai_config_service import AIConfigService


def test_rate_limiting_config():
    """测试限流配置"""
    print("\n=== 测试限流配置 ===")
    
    # 创建测试数据库连接
    DATABASE_URL = "postgresql://admin:admin123@localhost:5432/hospital_value"
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    
    try:
        # 查询AI配置
        config = db.query(AIConfig).filter(AIConfig.hospital_id == 1).first()
        
        if config:
            print(f"✓ 找到AI配置")
            print(f"  - 调用延迟: {config.call_delay} 秒")
            print(f"  - 批次大小: {config.batch_size}")
            print(f"  - 每日限额: {config.daily_limit}")
        else:
            print("✗ 未找到AI配置")
            
    finally:
        db.close()


def test_usage_statistics():
    """测试使用统计功能"""
    print("\n=== 测试使用统计功能 ===")
    
    # 创建测试数据库连接
    DATABASE_URL = "postgresql://admin:admin123@localhost:5432/hospital_value"
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    
    try:
        # 获取使用统计
        stats = AIConfigService.get_usage_stats(
            db=db,
            hospital_id=1,
            days=30,
            cost_per_call=0.001
        )
        
        print(f"✓ 使用统计（最近30天）:")
        print(f"  - 总调用次数: {stats.total_calls}")
        print(f"  - 成功调用: {stats.successful_calls}")
        print(f"  - 失败调用: {stats.failed_calls}")
        print(f"  - 今日调用: {stats.today_calls}")
        print(f"  - 每日限额: {stats.daily_limit}")
        print(f"  - 平均响应时间: {stats.avg_duration:.3f} 秒")
        print(f"  - 预估成本: ¥{stats.estimated_cost:.2f}")
        
        # 测试不同单价
        stats_high_cost = AIConfigService.get_usage_stats(
            db=db,
            hospital_id=1,
            days=30,
            cost_per_call=0.01  # 10倍单价
        )
        print(f"\n✓ 使用高单价计算（0.01元/次）:")
        print(f"  - 预估成本: ¥{stats_high_cost.estimated_cost:.2f}")
        
    finally:
        db.close()


def test_daily_limit_check():
    """测试每日限额检查"""
    print("\n=== 测试每日限额检查 ===")
    
    # 创建测试数据库连接
    DATABASE_URL = "postgresql://admin:admin123@localhost:5432/hospital_value"
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    
    try:
        # 查询今日调用次数
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        today_calls = db.query(APIUsageLog).filter(
            APIUsageLog.hospital_id == 1,
            APIUsageLog.created_at >= today_start
        ).count()
        
        # 获取每日限额
        config = db.query(AIConfig).filter(AIConfig.hospital_id == 1).first()
        daily_limit = config.daily_limit if config else 10000
        
        print(f"✓ 每日限额检查:")
        print(f"  - 今日已调用: {today_calls} 次")
        print(f"  - 每日限额: {daily_limit} 次")
        print(f"  - 剩余额度: {daily_limit - today_calls} 次")
        
        if today_calls >= daily_limit:
            print(f"  ⚠ 警告: 已达到每日限额！")
        else:
            usage_percent = (today_calls / daily_limit) * 100
            print(f"  - 使用率: {usage_percent:.1f}%")
            
    finally:
        db.close()


def test_batch_processing_logic():
    """测试批次处理逻辑"""
    print("\n=== 测试批次处理逻辑 ===")
    
    # 模拟批次处理
    batch_size = 100
    total_items = 350
    call_delay = 1.0
    
    print(f"配置:")
    print(f"  - 批次大小: {batch_size}")
    print(f"  - 总项目数: {total_items}")
    print(f"  - 调用延迟: {call_delay} 秒")
    
    # 计算批次数
    num_batches = (total_items + batch_size - 1) // batch_size
    print(f"\n预计处理:")
    print(f"  - 批次数: {num_batches}")
    
    # 计算预计时间
    items_delay = (total_items - 1) * call_delay  # 项目间延迟
    batch_pause = (num_batches - 1) * (call_delay * 2)  # 批次间暂停
    total_time = items_delay + batch_pause
    
    print(f"  - 项目间延迟总时间: {items_delay:.0f} 秒")
    print(f"  - 批次间暂停总时间: {batch_pause:.0f} 秒")
    print(f"  - 预计总时间: {total_time:.0f} 秒 ({total_time/60:.1f} 分钟)")


if __name__ == "__main__":
    print("=" * 60)
    print("API调用限流和统计功能测试")
    print("=" * 60)
    
    try:
        test_rate_limiting_config()
        test_usage_statistics()
        test_daily_limit_check()
        test_batch_processing_logic()
        
        print("\n" + "=" * 60)
        print("✓ 所有测试完成")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n✗ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
