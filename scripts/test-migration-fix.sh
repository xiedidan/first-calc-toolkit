#!/bin/bash
# ============================================
# 测试迁移文件自动修复逻辑
# 仅用于开发测试，不要在生产环境运行
# ============================================

set -e

echo "=========================================="
echo "  测试迁移文件自动修复"
echo "=========================================="
echo ""

# 检查是否在正确的目录
if [ ! -f "backend/alembic.ini" ]; then
    echo "✗ 请在项目根目录运行此脚本"
    exit 1
fi

cd backend

echo ">>> 当前迁移状态..."
python -c "
from alembic.config import Config
from alembic.script import ScriptDirectory

cfg = Config('alembic.ini')
script = ScriptDirectory.from_config(cfg)

heads = script.get_revisions('heads')
print(f'Heads: {len(heads)}')
for h in heads:
    print(f'  - {h.revision}: {h.doc}')
"

echo ""
echo ">>> 测试场景："
echo "  1. 单个 head - 正常升级"
echo "  2. 多个 heads - 自动合并"
echo ""

# 模拟检测逻辑
HEADS_COUNT=$(python -c "
from alembic.config import Config
from alembic.script import ScriptDirectory
cfg = Config('alembic.ini')
script = ScriptDirectory.from_config(cfg)
heads = script.get_revisions('heads')
print(len(heads))
")

echo "检测到 $HEADS_COUNT 个 head(s)"

if [ "$HEADS_COUNT" = "1" ]; then
    echo "✓ 单个 head，可以正常升级"
    echo "  命令: alembic upgrade head"
elif [ "$HEADS_COUNT" -gt "1" ]; then
    echo "⚠ 多个 heads，需要合并"
    
    # 获取所有 heads
    HEADS=$(python -c "
from alembic.config import Config
from alembic.script import ScriptDirectory
cfg = Config('alembic.ini')
script = ScriptDirectory.from_config(cfg)
heads = script.get_revisions('heads')
print(' '.join([h.revision for h in heads]))
")
    
    echo "  Heads: $HEADS"
    echo "  命令: alembic merge -m 'auto merge' $HEADS"
    echo ""
    echo "是否创建合并迁移? (y/n)"
    read -r response
    
    if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
        TIMESTAMP=$(date +%Y%m%d_%H%M%S)
        alembic merge -m "test merge $TIMESTAMP" $HEADS
        echo "✓ 合并迁移已创建"
        echo ""
        echo "新的迁移状态:"
        python -c "
from alembic.config import Config
from alembic.script import ScriptDirectory
cfg = Config('alembic.ini')
script = ScriptDirectory.from_config(cfg)
heads = script.get_revisions('heads')
print(f'Heads: {len(heads)}')
for h in heads:
    print(f'  - {h.revision}: {h.doc}')
"
    fi
else
    echo "✗ 未找到任何 head"
fi

cd ..

echo ""
echo "测试完成"
