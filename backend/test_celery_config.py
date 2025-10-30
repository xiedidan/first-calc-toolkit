"""
测试 Celery 配置加载
"""
import os
import sys

# 确保在 backend 目录下运行
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=" * 60)
print("测试 Celery 配置加载")
print("=" * 60)

# 1. 检查环境变量
print("\n1. 检查 .env 文件:")
env_file = ".env"
if os.path.exists(env_file):
    print(f"   ✅ {env_file} 存在")
    with open(env_file, 'r', encoding='utf-8') as f:
        for line in f:
            if 'CELERY' in line and not line.strip().startswith('#'):
                print(f"   {line.strip()}")
else:
    print(f"   ❌ {env_file} 不存在")

# 2. 加载配置
print("\n2. 加载配置:")
try:
    from app.config import settings
    print(f"   ✅ 配置加载成功")
    print(f"   CELERY_BROKER_URL: {settings.CELERY_BROKER_URL}")
    print(f"   CELERY_RESULT_BACKEND: {settings.CELERY_RESULT_BACKEND}")
except Exception as e:
    print(f"   ❌ 配置加载失败: {e}")
    sys.exit(1)

# 3. 检查 Celery app
print("\n3. 检查 Celery app:")
try:
    from app.celery_app import celery_app
    print(f"   ✅ Celery app 创建成功")
    print(f"   Broker: {celery_app.conf.broker_url}")
    print(f"   Backend: {celery_app.conf.result_backend}")
    
    # 检查是否是 Redis
    if 'redis' in str(celery_app.conf.broker_url).lower():
        print(f"   ✅ 使用 Redis 作为 broker")
    elif 'amqp' in str(celery_app.conf.broker_url).lower():
        print(f"   ❌ 错误：使用 RabbitMQ (AMQP) 作为 broker")
    else:
        print(f"   ⚠️  未知的 broker 类型")
        
except Exception as e:
    print(f"   ❌ Celery app 创建失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# 4. 测试连接
print("\n4. 测试 Redis 连接:")
try:
    import redis
    r = redis.from_url(settings.CELERY_BROKER_URL)
    r.ping()
    print(f"   ✅ Redis 连接成功")
except Exception as e:
    print(f"   ❌ Redis 连接失败: {e}")

print("\n" + "=" * 60)
print("测试完成")
print("=" * 60)
