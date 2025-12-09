# 医技智能分类分级 - 部署文档

## 1. 环境变量配置

### 必需环境变量
```bash
# 数据库
DATABASE_URL=postgresql://user:password@localhost:5432/hospital_value

# Redis
REDIS_URL=redis://localhost:6379/0

# 加密密钥（用于API密钥加密）
ENCRYPTION_KEY=<使用 generate_encryption_key.py 生成>

# Celery
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
```

### 生成加密密钥
```bash
cd backend
python generate_encryption_key.py
```

## 2. 数据库迁移

### 执行迁移
```bash
cd backend
alembic upgrade head
```

### 验证迁移
```bash
# 检查表是否创建
psql -h localhost -U admin -d hospital_value -c "\dt ai_*"
```

## 3. Redis配置

### 安装Redis
```bash
# Ubuntu/Debian
sudo apt-get install redis-server

# Windows
# 下载并安装 Redis for Windows
```

### 启动Redis
```bash
redis-server
```

### 验证连接
```bash
redis-cli ping
# 应返回 PONG
```

## 4. Celery Worker启动

### 启动命令
```bash
# Linux/Mac
cd backend
celery -A app.tasks.celery_app worker --loglevel=info

# Windows
cd backend
celery -A app.tasks.celery_app worker --loglevel=info --pool=solo
```

### 后台运行（生产环境）
```bash
# 使用 systemd
sudo systemctl start celery-worker
sudo systemctl enable celery-worker

# 或使用 supervisor
supervisorctl start celery-worker
```

### 验证Worker
```bash
celery -A app.tasks.celery_app inspect active
```

## 5. 监控和告警

### Celery监控
```bash
# 安装 Flower
pip install flower

# 启动监控界面
celery -A app.tasks.celery_app flower --port=5555
```

### 日志配置
```python
# backend/app/core/config.py
LOGGING_CONFIG = {
    'version': 1,
    'handlers': {
        'file': {
            'class': 'logging.FileHandler',
            'filename': 'logs/ai_classification.log',
            'level': 'INFO'
        }
    }
}
```

### 告警配置
- 监控Celery队列长度
- 监控任务失败率
- 监控API调用限额
- 监控Redis连接状态

## 6. 性能优化

### Celery并发
```bash
# 增加worker数量
celery -A app.tasks.celery_app worker --concurrency=4
```

### Redis持久化
```bash
# redis.conf
save 900 1
save 300 10
```

### 数据库索引
```sql
CREATE INDEX idx_task_hospital ON classification_tasks(hospital_id);
CREATE INDEX idx_plan_task ON classification_plans(task_id);
CREATE INDEX idx_item_plan ON plan_items(plan_id);
```

## 7. 故障排查

### Celery任务不执行
- 检查Redis连接
- 检查Worker是否运行
- 查看Celery日志

### API调用失败
- 验证API端点和密钥
- 检查网络连接
- 查看APIUsageLog表

### 加密解密错误
- 确认ENCRYPTION_KEY环境变量
- 重新生成密钥需重新配置API

## 8. 备份策略

### 数据库备份
```bash
pg_dump -h localhost -U admin hospital_value > backup.sql
```

### Redis备份
```bash
redis-cli BGSAVE
```
