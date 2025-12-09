"""
测试AI配置服务

单元测试AI配置服务的功能，不需要运行服务器
"""
import sys
import os

# 添加backend目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app.models.ai_config import AIConfig
from app.models.api_usage_log import APIUsageLog
from app.schemas.ai_config import AIConfigCreate, AIConfigTest, APIUsageStatsResponse
from app.services.ai_config_service import AIConfigService
from app.utils.encryption import decrypt_api_key, mask_api_key


# 创建测试数据库
TEST_DATABASE_URL = "sqlite:///./test_ai_config.db"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def setup_database():
    """设置测试数据库"""
    # 只创建需要的表
    from app.models.ai_config import AIConfig
    from app.models.api_usage_log import APIUsageLog
    
    # 删除表（如果存在）
    APIUsageLog.__table__.drop(engine, checkfirst=True)
    AIConfig.__table__.drop(engine, checkfirst=True)
    
    # 创建表
    AIConfig.__table__.create(engine, checkfirst=True)
    APIUsageLog.__table__.create(engine, checkfirst=True)
    
    print("✓ 测试数据库已创建")


def test_create_config():
    """测试创建AI配置"""
    print("\n=== 测试创建AI配置 ===")
    
    db = TestingSessionLocal()
    try:
        # 创建配置
        config_data = AIConfigCreate(
            api_endpoint="https://api.deepseek.com/v1",
            api_key="sk-test-key-12345678901234567890",
            prompt_template="测试提示词模板\n{item_name}\n{dimensions}",
            call_delay=1.0,
            daily_limit=10000,
            batch_size=100
        )
        
        result = AIConfigService.create_or_update_config(db, hospital_id=1, config_data=config_data)
        
        # 验证结果
        assert result is not None, "创建配置失败"
        assert result.hospital_id == 1, "医疗机构ID不正确"
        assert result.api_endpoint == config_data.api_endpoint, "API端点不正确"
        assert "****" in result.api_key_masked, "密钥未掩码"
        assert result.prompt_template == config_data.prompt_template, "提示词模板不正确"
        assert result.call_delay == config_data.call_delay, "调用延迟不正确"
        assert result.daily_limit == config_data.daily_limit, "每日限额不正确"
        assert result.batch_size == config_data.batch_size, "批次大小不正确"
        
        print("✓ 创建AI配置成功")
        print(f"  配置ID: {result.id}")
        print(f"  API端点: {result.api_endpoint}")
        print(f"  密钥掩码: {result.api_key_masked}")
        print(f"  调用延迟: {result.call_delay}秒")
        print(f"  每日限额: {result.daily_limit}次")
        
        # 验证数据库中的密钥已加密
        db_config = db.query(AIConfig).filter(AIConfig.id == result.id).first()
        assert db_config is not None, "数据库中找不到配置"
        assert db_config.api_key_encrypted != config_data.api_key, "密钥未加密"
        
        # 验证可以解密
        decrypted_key = decrypt_api_key(db_config.api_key_encrypted)
        assert decrypted_key == config_data.api_key, "密钥解密失败"
        print("✓ 密钥加密和解密验证成功")
        
        return result.id
        
    finally:
        db.close()


def test_get_config(config_id):
    """测试获取AI配置"""
    print("\n=== 测试获取AI配置 ===")
    
    db = TestingSessionLocal()
    try:
        result = AIConfigService.get_config(db, hospital_id=1)
        
        # 验证结果
        assert result is not None, "获取配置失败"
        assert result.id == config_id, "配置ID不正确"
        assert "****" in result.api_key_masked, "密钥未掩码"
        
        print("✓ 获取AI配置成功")
        print(f"  配置ID: {result.id}")
        print(f"  密钥掩码: {result.api_key_masked}")
        
    finally:
        db.close()


def test_update_config(config_id):
    """测试更新AI配置"""
    print("\n=== 测试更新AI配置 ===")
    
    db = TestingSessionLocal()
    try:
        # 更新配置
        config_data = AIConfigCreate(
            api_endpoint="https://api.deepseek.com/v1",
            api_key="sk-test-key-updated-98765432109876543210",
            prompt_template="更新后的提示词模板\n{item_name}\n{dimensions}",
            call_delay=1.5,
            daily_limit=5000,
            batch_size=50
        )
        
        result = AIConfigService.create_or_update_config(db, hospital_id=1, config_data=config_data)
        
        # 验证结果
        assert result is not None, "更新配置失败"
        assert result.id == config_id, "配置ID不应该改变"
        assert result.call_delay == 1.5, "调用延迟未更新"
        assert result.daily_limit == 5000, "每日限额未更新"
        assert result.batch_size == 50, "批次大小未更新"
        
        print("✓ 更新AI配置成功")
        print(f"  调用延迟: {result.call_delay}秒")
        print(f"  每日限额: {result.daily_limit}次")
        print(f"  批次大小: {result.batch_size}个")
        
        # 验证密钥已更新
        db_config = db.query(AIConfig).filter(AIConfig.id == result.id).first()
        decrypted_key = decrypt_api_key(db_config.api_key_encrypted)
        assert decrypted_key == config_data.api_key, "密钥未更新"
        print("✓ 密钥更新验证成功")
        
    finally:
        db.close()


def test_get_usage_stats():
    """测试获取使用统计"""
    print("\n=== 测试获取使用统计 ===")
    
    db = TestingSessionLocal()
    try:
        result = AIConfigService.get_usage_stats(db, hospital_id=1, days=30)
        
        # 验证结果
        assert result is not None, "获取使用统计失败"
        assert result.total_calls == 0, "总调用次数应为0"
        assert result.successful_calls == 0, "成功次数应为0"
        assert result.failed_calls == 0, "失败次数应为0"
        assert result.today_calls == 0, "今日调用应为0"
        assert result.daily_limit == 5000, "每日限额不正确"
        assert result.period_days == 30, "统计天数不正确"
        
        print("✓ 获取使用统计成功")
        print(f"  总调用次数: {result.total_calls}")
        print(f"  成功次数: {result.successful_calls}")
        print(f"  失败次数: {result.failed_calls}")
        print(f"  今日调用: {result.today_calls}")
        print(f"  每日限额: {result.daily_limit}")
        print(f"  预估成本: ¥{result.estimated_cost}")
        
    finally:
        db.close()


def test_multi_tenant_isolation():
    """测试多租户隔离"""
    print("\n=== 测试多租户隔离 ===")
    
    db = TestingSessionLocal()
    try:
        # 为医疗机构2创建配置
        config_data = AIConfigCreate(
            api_endpoint="https://api.deepseek.com/v1",
            api_key="sk-hospital2-key-12345678901234567890",
            prompt_template="医疗机构2的提示词模板",
            call_delay=2.0,
            daily_limit=20000,
            batch_size=200
        )
        
        result2 = AIConfigService.create_or_update_config(db, hospital_id=2, config_data=config_data)
        
        # 验证医疗机构1的配置不受影响
        result1 = AIConfigService.get_config(db, hospital_id=1)
        assert result1 is not None, "医疗机构1的配置丢失"
        assert result1.call_delay == 1.5, "医疗机构1的配置被修改"
        
        # 验证医疗机构2的配置正确
        assert result2 is not None, "医疗机构2的配置创建失败"
        assert result2.hospital_id == 2, "医疗机构ID不正确"
        assert result2.call_delay == 2.0, "医疗机构2的配置不正确"
        
        print("✓ 多租户隔离验证成功")
        print(f"  医疗机构1配置ID: {result1.id}, 调用延迟: {result1.call_delay}秒")
        print(f"  医疗机构2配置ID: {result2.id}, 调用延迟: {result2.call_delay}秒")
        
    finally:
        db.close()


def test_mask_api_key():
    """测试密钥掩码功能"""
    print("\n=== 测试密钥掩码功能 ===")
    
    # 测试不同长度的密钥
    test_cases = [
        ("sk-test-key-12345678901234567890", "****7890"),
        ("short", "****hort"),
        ("abc", "****abc"),
        ("", "****"),
    ]
    
    for original, expected_suffix in test_cases:
        masked = mask_api_key(original)
        assert "****" in masked, f"密钥 '{original}' 未正确掩码"
        if len(original) > 4:
            assert masked.endswith(original[-4:]), f"密钥 '{original}' 后缀不正确"
        print(f"  '{original}' -> '{masked}' ✓")
    
    print("✓ 密钥掩码功能验证成功")


def cleanup_database():
    """清理测试数据库"""
    # 关闭所有连接
    engine.dispose()
    
    # 等待一下让文件释放
    import time
    time.sleep(0.5)
    
    if os.path.exists("test_ai_config.db"):
        try:
            os.remove("test_ai_config.db")
            print("\n✓ 测试数据库已清理")
        except PermissionError:
            print("\n⚠ 无法删除测试数据库文件（文件被占用），请手动删除")


def main():
    """主测试流程"""
    print("=" * 60)
    print("AI配置服务单元测试")
    print("=" * 60)
    
    try:
        # 设置数据库
        setup_database()
        
        # 测试密钥掩码
        test_mask_api_key()
        
        # 测试创建配置
        config_id = test_create_config()
        
        # 测试获取配置
        test_get_config(config_id)
        
        # 测试更新配置
        test_update_config(config_id)
        
        # 测试获取使用统计
        test_get_usage_stats()
        
        # 测试多租户隔离
        test_multi_tenant_isolation()
        
        print("\n" + "=" * 60)
        print("✓ 所有测试通过")
        print("=" * 60)
        
    except AssertionError as e:
        print(f"\n✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
    except Exception as e:
        print(f"\n✗ 测试出错: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # 清理数据库
        cleanup_database()


if __name__ == "__main__":
    main()
