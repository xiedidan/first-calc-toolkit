#!/bin/bash
# ============================================
# 迁移文件诊断脚本
# 用于检查 Alembic 迁移文件的状态
# ============================================

set -e

echo "=========================================="
echo "  Alembic 迁移文件诊断"
echo "=========================================="
echo ""

# 检查容器是否运行
if ! docker ps | grep -q hospital_backend_offline; then
    echo "✗ 后端容器未运行"
    echo "请先启动容器: docker-compose -f config/docker-compose.offline.yml up -d backend"
    exit 1
fi

echo ">>> 检查迁移文件数量..."
MIGRATION_COUNT=$(docker exec hospital_backend_offline ls -1 alembic/versions/*.py 2>/dev/null | wc -l)
echo "  迁移文件数量: $MIGRATION_COUNT"
echo ""

echo ">>> 检查迁移 heads..."
docker exec hospital_backend_offline python -c "
from alembic.config import Config
from alembic.script import ScriptDirectory

cfg = Config('alembic.ini')
script = ScriptDirectory.from_config(cfg)

heads = script.get_revisions('heads')
print(f'Found {len(heads)} head(s):')
for h in heads:
    print(f'  - {h.revision}: {h.doc}')
"

echo ""
echo ">>> 最近的 10 个迁移..."
docker exec hospital_backend_offline python -c "
from alembic.config import Config
from alembic.script import ScriptDirectory

cfg = Config('alembic.ini')
script = ScriptDirectory.from_config(cfg)

count = 0
for rev in script.walk_revisions():
    down = rev.down_revision[:12] if rev.down_revision else 'None'
    print(f'{rev.revision[:12]} <- {down:12} | {rev.doc}')
    count += 1
    if count >= 10:
        break
"

echo ""
echo ">>> 数据库当前版本..."
docker exec hospital_backend_offline alembic current

echo ""
echo "=========================================="
echo "  诊断完成"
echo "=========================================="
echo ""
echo "如果发现多个 heads，可以尝试："
echo "  1. 使用 'alembic upgrade heads' 升级所有分支"
echo "  2. 或者清理数据库并重新初始化"
