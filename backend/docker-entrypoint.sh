#!/bin/bash
# ============================================
# Docker 容器入口脚本
# 用于在容器启动时执行初始化任务
# ============================================

set -e

echo "=========================================="
echo "  容器启动初始化"
echo "=========================================="

# 检查迁移文件
echo ">>> 检查迁移文件..."
MIGRATION_COUNT=$(ls -1 alembic/versions/*.py 2>/dev/null | wc -l)
echo "  迁移文件数量: $MIGRATION_COUNT"

# 检查迁移 heads
HEADS_COUNT=$(python -c "
from alembic.config import Config
from alembic.script import ScriptDirectory
try:
    cfg = Config('alembic.ini')
    script = ScriptDirectory.from_config(cfg)
    heads = script.get_revisions('heads')
    print(len(heads))
except Exception as e:
    print('0')
" 2>/dev/null)

echo "  迁移 heads 数量: $HEADS_COUNT"

if [ "$HEADS_COUNT" != "1" ] && [ "$HEADS_COUNT" != "0" ]; then
    echo "⚠ 警告: 检测到 $HEADS_COUNT 个迁移分支"
    echo "  这可能导致迁移失败"
    echo "  建议在部署前修复迁移文件链"
fi

echo "✓ 初始化完成"
echo ""

# 执行传入的命令
exec "$@"
