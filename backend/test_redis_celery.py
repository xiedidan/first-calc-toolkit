"""
测试 Redis 和 Celery 配置
"""
import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_redis_connection():
    """测试 Redis 连接"""
    print("=" * 60)
    print("测试 Redis 连接")
    print("=" * 60)
    
    try:
        import redis
        r = redis.Redis(host='localhost', port=6379, db=0)
        r.ping()
        print("✅ Redis 连接成功")
        
        # 测试读写
        r.set('test_key', 'test_value')
        value = r.get('test_key')
        if value == b'test_value':
            print("✅ Redis 读写测试成功")
        r.delete('test_key')
        
        return True
    except Exception as e:
        print(f"❌ Redis 连接失败: {e}")
        return False


def test_celery_config():
    """测试 Celery 配置"""
    print("\n" + "=" * 60)
    print("测试 Celery 配置")
    print("=" * 60)
    
    try:
        from app.celery_app import celery_app
        
        print(f"✅ Celery app 创建成功")
        print(f"   Broker: {celery_app.conf.broker_url}")
        print(f"   Backend: {celery_app.conf.result_backend}")
        
        # 检查 backend 类型
        backend_type = type(celery_app.backend).__name__
        print(f"   Backend 类型: {backend_type}")
        
        if backend_type == 'DisabledBackend':
            print("❌ Backend 被禁用！请检查配置。")
            return False
        else:
            print("✅ Backend 已启用")
        
        return True
    except Exception as e:
        print(f"❌ Celery 配置加载失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_task_result():
    """测试任务结果查询"""
    print("\n" + "=" * 60)
    print("测试任务结果查询")
    print("=" * 60)
    
    try:
        from app.celery_app import celery_app
        
        # 创建一个测试任务 ID
        test_task_id = "test-task-id-12345"
        
        # 尝试查询任务状态
        result = celery_app.AsyncResult(test_task_id)
        state = result.state
        
        print(f"✅ 任务状态查询成功")
        print(f"   测试任务 ID: {test_task_id}")
        print(f"   任务状态: {state}")
        
        return True
    except Exception as e:
        print(f"❌ 任务状态查询失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_env_config():
    """测试环境变量配置"""
    print("\n" + "=" * 60)
    print("测试环境变量配置")
    print("=" * 60)
    
    try:
        from app.config import settings
        
        print(f"✅ 配置加载成功")
        print(f"   CELERY_BROKER_URL: {settings.CELERY_BROKER_URL}")
        print(f"   CELERY_RESULT_BACKEND: {settings.CELERY_RESULT_BACKEND}")
        
        # 检查配置是否为空
        if not settings.CELERY_BROKER_URL or not settings.CELERY_RESULT_BACKEND:
            print("❌ Celery 配置为空！")
            return False
        
        return True
    except Exception as e:
        print(f"❌ 配置加载失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """运行所有测试"""
    print("\n" + "=" * 60)
    print("Redis 和 Celery 配置测试")
    print("=" * 60 + "\n")
    
    results = []
    
    # 测试环境变量
    results.append(("环境变量配置", test_env_config()))
    
    # 测试 Redis 连接
    results.append(("Redis 连接", test_redis_connection()))
    
    # 测试 Celery 配置
    results.append(("Celery 配置", test_celery_config()))
    
    # 测试任务结果查询
    results.append(("任务结果查询", test_task_result()))
    
    # 总结
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)
    
    for name, success in results:
        status = "✅ 通过" if success else "❌ 失败"
        print(f"{name}: {status}")
    
    all_passed = all(success for _, success in results)
    
    if all_passed:
        print("\n🎉 所有测试通过！异步导入功能应该可以正常工作。")
    else:
        print("\n⚠️  部分测试失败，请根据上面的错误信息进行修复。")
        print("\n常见问题：")
        print("1. Redis 未启动 - 请安装并启动 Redis/Memurai")
        print("2. .env 配置错误 - 检查 CELERY_BROKER_URL 和 CELERY_RESULT_BACKEND")
        print("3. 需要重启服务 - 修改配置后需要重启 FastAPI 和 Celery Worker")
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
