#!/bin/bash
# ============================================================================
# 业务类别字段迁移脚本
# ============================================================================
# 功能: 自动执行业务类别字段的迁移流程
# 
# 使用方法:
#   ./migrate_business_type.sh <host> <user> <database>
#
# 示例:
#   ./migrate_business_type.sh localhost admin hospital_external_data
# ============================================================================

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 参数检查
if [ $# -lt 3 ]; then
    echo -e "${RED}错误: 参数不足${NC}"
    echo "使用方法: $0 <host> <user> <database>"
    echo "示例: $0 localhost admin hospital_external_data"
    exit 1
fi

HOST=$1
USER=$2
DATABASE=$3

echo -e "${BLUE}============================================================================${NC}"
echo -e "${BLUE}业务类别字段迁移脚本${NC}"
echo -e "${BLUE}============================================================================${NC}"
echo -e "数据库主机: ${GREEN}$HOST${NC}"
echo -e "数据库用户: ${GREEN}$USER${NC}"
echo -e "数据库名称: ${GREEN}$DATABASE${NC}"
echo -e "${BLUE}============================================================================${NC}"
echo ""

# 确认执行
read -p "是否继续执行迁移? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}已取消迁移${NC}"
    exit 0
fi

# 步骤1: 备份数据库
echo -e "\n${BLUE}步骤 1/3: 备份数据库${NC}"
BACKUP_FILE="backup_${DATABASE}_$(date +%Y%m%d_%H%M%S).dump"
echo "备份文件: $BACKUP_FILE"

if pg_dump -h $HOST -U $USER -d $DATABASE -F c -f $BACKUP_FILE; then
    echo -e "${GREEN}✅ 备份成功${NC}"
else
    echo -e "${RED}❌ 备份失败，终止迁移${NC}"
    exit 1
fi

# 步骤2: 添加字段
echo -e "\n${BLUE}步骤 2/3: 添加 business_type 字段${NC}"

if psql -h $HOST -U $USER -d $DATABASE -P pager=off -f add_business_type_to_charge_details.sql; then
    echo -e "${GREEN}✅ 字段添加成功${NC}"
else
    echo -e "${RED}❌ 字段添加失败${NC}"
    echo -e "${YELLOW}提示: 可以使用以下命令恢复备份:${NC}"
    echo "pg_restore -h $HOST -U $USER -d $DATABASE -c $BACKUP_FILE"
    exit 1
fi

# 步骤3: 验证结果
echo -e "\n${BLUE}步骤 3/3: 验证迁移结果${NC}"

VERIFICATION_SQL="
SELECT 
    CASE 
        WHEN EXISTS (
            SELECT 1 FROM information_schema.columns 
            WHERE table_name = 'charge_details' 
            AND column_name = 'business_type'
        ) THEN '✅ 字段存在'
        ELSE '❌ 字段不存在'
    END as field_check,
    CASE 
        WHEN EXISTS (
            SELECT 1 FROM pg_indexes 
            WHERE tablename = 'charge_details' 
            AND indexname = 'idx_charge_details_business_type'
        ) THEN '✅ 索引存在'
        ELSE '⚠️  索引不存在'
    END as index_check;
"

if psql -h $HOST -U $USER -d $DATABASE -P pager=off -c "$VERIFICATION_SQL"; then
    echo -e "${GREEN}✅ 验证完成${NC}"
else
    echo -e "${YELLOW}⚠️  验证失败，请手动检查${NC}"
fi

# 完成
echo -e "\n${BLUE}============================================================================${NC}"
echo -e "${GREEN}✅ 迁移完成!${NC}"
echo -e "${BLUE}============================================================================${NC}"
echo ""
echo -e "备份文件: ${GREEN}$BACKUP_FILE${NC}"
echo ""
echo -e "${YELLOW}后续步骤:${NC}"
echo "1. 如果有历史数据，执行更新脚本:"
echo "   psql -h $HOST -U $USER -d $DATABASE -f update_historical_business_type.sql"
echo ""
echo "2. 生成新的测试数据:"
echo "   python backend/standard_workflow_templates/generate_test_data.py --hospital-id 1 --period 2025-11"
echo ""
echo "3. 运行计算任务，验证业务类别区分是否正常工作"
echo ""
