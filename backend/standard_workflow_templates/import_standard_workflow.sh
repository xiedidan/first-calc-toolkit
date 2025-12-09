#!/bin/bash

# ============================================================================
# 标准计算流程导入脚本
# ============================================================================
# 功能: 将标准计算流程SQL代码导入到系统数据库
# 作者: 系统自动生成
# 版本: 1.0
# ============================================================================

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印函数
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# ============================================================================
# 第1步: 读取backend/.env配置文件
# ============================================================================
print_info "读取backend/.env配置文件..."

ENV_FILE="../.env"
if [ ! -f "$ENV_FILE" ]; then
    print_error ".env文件不存在: $ENV_FILE"
    print_error "请确保在backend目录下存在.env配置文件"
    exit 1
fi

# 读取数据库配置
export $(grep -v '^#' "$ENV_FILE" | grep -E '^DATABASE_' | xargs)

# 检查是否使用DATABASE_URL格式
if [ -n "$DATABASE_URL" ] && [ -z "$DATABASE_HOST" ]; then
    print_info "检测到DATABASE_URL格式,正在解析..."
    
    # 解析DATABASE_URL
    # 格式: postgresql://user:password@host:port/database
    if [[ $DATABASE_URL =~ postgresql://([^:]+):([^@]+)@([^:]+):([^/]+)/(.+) ]]; then
        DATABASE_USER="${BASH_REMATCH[1]}"
        DATABASE_PASSWORD="${BASH_REMATCH[2]}"
        DATABASE_HOST="${BASH_REMATCH[3]}"
        DATABASE_PORT="${BASH_REMATCH[4]}"
        DATABASE_NAME="${BASH_REMATCH[5]}"
        
        print_success "成功解析DATABASE_URL"
    else
        print_error "DATABASE_URL格式不正确"
        print_error "期望格式: postgresql://user:password@host:port/database"
        print_error "实际值: $DATABASE_URL"
        exit 1
    fi
fi

# 验证必需的环境变量
if [ -z "$DATABASE_HOST" ]; then
    print_error "DATABASE_HOST未在.env文件中配置"
    print_error "请在.env文件中添加以下配置之一:"
    print_error "  方式1: DATABASE_URL=postgresql://user:password@host:port/database"
    print_error "  方式2: DATABASE_HOST, DATABASE_PORT, DATABASE_NAME, DATABASE_USER, DATABASE_PASSWORD"
    exit 1
fi

if [ -z "$DATABASE_PORT" ]; then
    print_error "DATABASE_PORT未在.env文件中配置"
    exit 1
fi

if [ -z "$DATABASE_NAME" ]; then
    print_error "DATABASE_NAME未在.env文件中配置"
    exit 1
fi

if [ -z "$DATABASE_USER" ]; then
    print_error "DATABASE_USER未在.env文件中配置"
    exit 1
fi

if [ -z "$DATABASE_PASSWORD" ]; then
    print_error "DATABASE_PASSWORD未在.env文件中配置"
    exit 1
fi

print_success "成功读取数据库配置:"
print_info "  主机: $DATABASE_HOST"
print_info "  端口: $DATABASE_PORT"
print_info "  数据库: $DATABASE_NAME"
print_info "  用户: $DATABASE_USER"


# ============================================================================
# 第2步: 解析命令行参数
# ============================================================================
print_info "解析命令行参数..."

VERSION_ID=""
WORKFLOW_NAME="标准计算流程"
HOSPITAL_ID=""
DATA_SOURCE_ID=""

# 解析参数
while [[ $# -gt 0 ]]; do
    case $1 in
        --version-id)
            VERSION_ID="$2"
            shift 2
            ;;
        --workflow-name)
            WORKFLOW_NAME="$2"
            shift 2
            ;;
        --hospital-id)
            HOSPITAL_ID="$2"
            shift 2
            ;;
        --data-source-id)
            DATA_SOURCE_ID="$2"
            shift 2
            ;;
        --help)
            echo "使用方法: bash import_standard_workflow.sh [选项]"
            echo ""
            echo "必填参数:"
            echo "  --version-id <ID>        模型版本ID"
            echo ""
            echo "可选参数:"
            echo "  --workflow-name <名称>   流程名称 (默认: 标准计算流程)"
            echo "  --hospital-id <ID>       医疗机构ID (如果不指定,将从版本中自动获取)"
            echo "  --data-source-id <ID>    数据源ID (如果指定,所有步骤将使用此数据源)"
            echo "  --help                   显示此帮助信息"
            echo ""
            echo "示例:"
            echo "  bash import_standard_workflow.sh --version-id 123"
            echo "  bash import_standard_workflow.sh --version-id 123 --data-source-id 1"
            echo "  bash import_standard_workflow.sh --version-id 123 --workflow-name '标准计算流程-2025'"
            echo "  bash import_standard_workflow.sh --version-id 123 --hospital-id 1 --data-source-id 1"
            exit 0
            ;;
        *)
            print_error "未知参数: $1"
            echo "使用 --help 查看帮助信息"
            exit 1
            ;;
    esac
done

# 验证必填参数
if [ -z "$VERSION_ID" ]; then
    print_error "缺少必填参数: --version-id"
    echo "使用 --help 查看帮助信息"
    exit 1
fi

print_success "参数解析完成:"
print_info "  版本ID: $VERSION_ID"
print_info "  流程名称: $WORKFLOW_NAME"
if [ -n "$HOSPITAL_ID" ]; then
    print_info "  医疗机构ID: $HOSPITAL_ID"
fi
if [ -n "$DATA_SOURCE_ID" ]; then
    print_info "  数据源ID: $DATA_SOURCE_ID"
fi


# ============================================================================
# 第3步: 测试数据库连接
# ============================================================================
print_info "测试数据库连接..."

# 设置PGPASSWORD环境变量以避免密码提示
export PGPASSWORD="$DATABASE_PASSWORD"

# 测试连接
if ! psql -h "$DATABASE_HOST" -p "$DATABASE_PORT" -U "$DATABASE_USER" -d "$DATABASE_NAME" -c "SELECT 1;" > /dev/null 2>&1; then
    print_error "数据库连接失败"
    print_error "请检查:"
    print_error "  1. 数据库服务是否运行"
    print_error "  2. .env文件中的配置是否正确"
    print_error "  3. 网络连接是否正常"
    exit 1
fi

print_success "数据库连接成功"


# ============================================================================
# 第4步: 验证模型版本并获取医疗机构ID
# ============================================================================
print_info "验证模型版本ID: $VERSION_ID..."

# 查询版本信息
VERSION_INFO=$(psql -h "$DATABASE_HOST" -p "$DATABASE_PORT" -U "$DATABASE_USER" -d "$DATABASE_NAME" -t -c \
    "SELECT hospital_id, version, name FROM model_versions WHERE id = $VERSION_ID;")

if [ -z "$VERSION_INFO" ]; then
    print_error "模型版本不存在: ID=$VERSION_ID"
    print_error "请在前端'模型版本管理'页面查看可用的版本ID"
    exit 1
fi

# 解析版本信息
VERSION_HOSPITAL_ID=$(echo $VERSION_INFO | awk '{print $1}')
VERSION_NUMBER=$(echo $VERSION_INFO | awk '{print $2}')
VERSION_NAME=$(echo $VERSION_INFO | awk '{$1=$2=""; print $0}' | xargs)

# 如果用户没有指定hospital_id,使用版本中的hospital_id
if [ -z "$HOSPITAL_ID" ]; then
    HOSPITAL_ID=$VERSION_HOSPITAL_ID
    print_info "从模型版本中获取医疗机构ID: $HOSPITAL_ID"
else
    # 验证用户指定的hospital_id与版本中的是否一致
    if [ "$HOSPITAL_ID" != "$VERSION_HOSPITAL_ID" ]; then
        print_warning "指定的医疗机构ID($HOSPITAL_ID)与版本中的医疗机构ID($VERSION_HOSPITAL_ID)不一致"
        print_warning "将使用版本中的医疗机构ID: $VERSION_HOSPITAL_ID"
        HOSPITAL_ID=$VERSION_HOSPITAL_ID
    fi
fi

print_success "模型版本验证通过:"
print_info "  版本号: $VERSION_NUMBER"
print_info "  版本名称: $VERSION_NAME"
print_info "  医疗机构ID: $HOSPITAL_ID"


# ============================================================================
# 第4.5步: 验证数据源ID（如果指定）
# ============================================================================
if [ -n "$DATA_SOURCE_ID" ]; then
    print_info "验证数据源ID: $DATA_SOURCE_ID..."
    
    # 查询数据源信息
    DATA_SOURCE_INFO=$(psql -h "$DATABASE_HOST" -p "$DATABASE_PORT" -U "$DATABASE_USER" -d "$DATABASE_NAME" -t -c \
        "SELECT name, db_type, is_enabled FROM data_sources WHERE id = $DATA_SOURCE_ID;")
    
    if [ -z "$DATA_SOURCE_INFO" ]; then
        print_error "数据源不存在: ID=$DATA_SOURCE_ID"
        print_error "请在前端'数据源管理'页面查看可用的数据源ID"
        exit 1
    fi
    
    # 解析数据源信息
    DATA_SOURCE_NAME=$(echo $DATA_SOURCE_INFO | awk '{print $1}')
    DATA_SOURCE_TYPE=$(echo $DATA_SOURCE_INFO | awk '{print $2}')
    DATA_SOURCE_ENABLED=$(echo $DATA_SOURCE_INFO | awk '{print $3}')
    
    print_success "数据源验证通过:"
    print_info "  数据源名称: $DATA_SOURCE_NAME"
    print_info "  数据源类型: $DATA_SOURCE_TYPE"
    print_info "  是否启用: $DATA_SOURCE_ENABLED"
    
    # 检查数据源是否启用
    if [ "$DATA_SOURCE_ENABLED" != "t" ]; then
        print_warning "数据源未启用，可能无法正常使用"
    fi
fi


# ============================================================================
# 第5步: 读取SQL代码文件
# ============================================================================
print_info "读取SQL代码文件..."

STEP1_FILE="step1_data_preparation.sql"
STEP2_FILE="step2_dimension_catalog.sql"
STEP3A_FILE="step3a_orientation_adjustment.sql"
STEP3B_FILE="step3b_indicator_calculation.sql"
STEP3C_FILE="step3c_workload_dimensions.sql"
STEP5_FILE="step5_value_aggregation.sql"

# 检查文件是否存在
for file in "$STEP1_FILE" "$STEP2_FILE" "$STEP3A_FILE" "$STEP3B_FILE" "$STEP3C_FILE" "$STEP5_FILE"; do
    if [ ! -f "$file" ]; then
        print_error "SQL文件不存在: $file"
        exit 1
    fi
done

# 读取文件内容(转义单引号)
STEP1_SQL=$(cat "$STEP1_FILE" | sed "s/'/''/g")
STEP2_SQL=$(cat "$STEP2_FILE" | sed "s/'/''/g")
STEP3A_SQL=$(cat "$STEP3A_FILE" | sed "s/'/''/g")
STEP3B_SQL=$(cat "$STEP3B_FILE" | sed "s/'/''/g")
STEP3C_SQL=$(cat "$STEP3C_FILE" | sed "s/'/''/g")
STEP5_SQL=$(cat "$STEP5_FILE" | sed "s/'/''/g")

print_success "成功读取6个SQL文件"


# ============================================================================
# 第6步: 创建计算流程记录
# ============================================================================
print_info "创建计算流程记录..."

# 使用-q参数禁止所有输出,只保留查询结果
WORKFLOW_ID=$(psql -h "$DATABASE_HOST" -p "$DATABASE_PORT" -U "$DATABASE_USER" -d "$DATABASE_NAME" -qtA -c \
    "INSERT INTO calculation_workflows (version_id, name, description, is_active, created_at, updated_at) 
     VALUES ($VERSION_ID, '$WORKFLOW_NAME', '基于数据集规范的标准计算流程', TRUE, NOW(), NOW()) 
     RETURNING id;")

# 提取纯数字(去除所有非数字字符)
WORKFLOW_ID=$(echo "$WORKFLOW_ID" | grep -o '[0-9]*' | head -1)

if [ -z "$WORKFLOW_ID" ]; then
    print_error "创建计算流程失败,无法获取流程ID"
    exit 1
fi

print_success "计算流程创建成功, ID: $WORKFLOW_ID"


# ============================================================================
# 第7步: 创建计算步骤记录
# ============================================================================
print_info "创建计算步骤记录..."

# 构建data_source_id字段（如果指定）
if [ -n "$DATA_SOURCE_ID" ]; then
    DATA_SOURCE_FIELD="data_source_id,"
    DATA_SOURCE_VALUE="$DATA_SOURCE_ID,"
else
    DATA_SOURCE_FIELD=""
    DATA_SOURCE_VALUE=""
fi

# 步骤1: 数据准备
psql -h "$DATABASE_HOST" -p "$DATABASE_PORT" -U "$DATABASE_USER" -d "$DATABASE_NAME" -c \
    "INSERT INTO calculation_steps (workflow_id, name, description, code_type, code_content, ${DATA_SOURCE_FIELD} sort_order, is_enabled, created_at, updated_at) 
     VALUES ($WORKFLOW_ID, '数据准备', '从门诊和住院收费明细表生成统一的收费明细数据', 'sql', '$STEP1_SQL', ${DATA_SOURCE_VALUE} 1.00, TRUE, NOW(), NOW());" > /dev/null

print_success "步骤1创建成功: 数据准备"

# 步骤2: 维度目录统计
psql -h "$DATABASE_HOST" -p "$DATABASE_PORT" -U "$DATABASE_USER" -d "$DATABASE_NAME" -c \
    "INSERT INTO calculation_steps (workflow_id, name, description, code_type, code_content, ${DATA_SOURCE_FIELD} sort_order, is_enabled, created_at, updated_at) 
     VALUES ($WORKFLOW_ID, '维度目录统计', '根据维度-收费项目映射统计各维度的工作量', 'sql', '$STEP2_SQL', ${DATA_SOURCE_VALUE} 2.00, TRUE, NOW(), NOW());" > /dev/null

print_success "步骤2创建成功: 维度目录统计"

# 步骤3a: 业务导向调整
psql -h "$DATABASE_HOST" -p "$DATABASE_PORT" -U "$DATABASE_USER" -d "$DATABASE_NAME" -c \
    "INSERT INTO calculation_steps (workflow_id, name, description, code_type, code_content, ${DATA_SOURCE_FIELD} sort_order, is_enabled, created_at, updated_at) 
     VALUES ($WORKFLOW_ID, '业务导向调整', '根据业务导向规则调整维度的学科业务价值', 'sql', '$STEP3A_SQL', ${DATA_SOURCE_VALUE} 3.00, TRUE, NOW(), NOW());" > /dev/null

print_success "步骤3a创建成功: 业务导向调整"

# 步骤3b: 指标计算-护理床日数
psql -h "$DATABASE_HOST" -p "$DATABASE_PORT" -U "$DATABASE_USER" -d "$DATABASE_NAME" -c \
    "INSERT INTO calculation_steps (workflow_id, name, description, code_type, code_content, ${DATA_SOURCE_FIELD} sort_order, is_enabled, created_at, updated_at) 
     VALUES ($WORKFLOW_ID, '指标计算-护理床日数', '从工作量统计表中提取护理床日数', 'sql', '$STEP3B_SQL', ${DATA_SOURCE_VALUE} 3.50, TRUE, NOW(), NOW());" > /dev/null

print_success "步骤3b创建成功: 指标计算-护理床日数"

# 步骤3c: 工作量维度统计
psql -h "$DATABASE_HOST" -p "$DATABASE_PORT" -U "$DATABASE_USER" -d "$DATABASE_NAME" -c \
    "INSERT INTO calculation_steps (workflow_id, name, description, code_type, code_content, ${DATA_SOURCE_FIELD} sort_order, is_enabled, created_at, updated_at) 
     VALUES ($WORKFLOW_ID, '工作量维度统计', '从工作量统计表中提取护理床日、出入转院、手术管理、手术室护理等维度的工作量', 'sql', '$STEP3C_SQL', ${DATA_SOURCE_VALUE} 3.60, TRUE, NOW(), NOW());" > /dev/null

print_success "步骤3c创建成功: 工作量维度统计"

# 步骤5: 业务价值汇总
psql -h "$DATABASE_HOST" -p "$DATABASE_PORT" -U "$DATABASE_USER" -d "$DATABASE_NAME" -c \
    "INSERT INTO calculation_steps (workflow_id, name, description, code_type, code_content, ${DATA_SOURCE_FIELD} sort_order, is_enabled, created_at, updated_at) 
     VALUES ($WORKFLOW_ID, '业务价值汇总', '根据模型结构和权重汇总各科室的业务价值', 'sql', '$STEP5_SQL', ${DATA_SOURCE_VALUE} 5.00, TRUE, NOW(), NOW());" > /dev/null

print_success "步骤5创建成功: 业务价值汇总"


# ============================================================================
# 第8步: 输出导入结果
# ============================================================================
echo ""
echo "========================================"
print_success "标准计算流程导入成功!"
echo "========================================"
echo ""
print_info "流程信息:"
echo "  流程ID: $WORKFLOW_ID"
echo "  流程名称: $WORKFLOW_NAME"
echo "  模型版本ID: $VERSION_ID"
echo "  步骤数量: 6"
if [ -n "$DATA_SOURCE_ID" ]; then
    echo "  数据源ID: $DATA_SOURCE_ID ($DATA_SOURCE_NAME)"
fi
echo ""
print_info "步骤详情:"
if [ -n "$DATA_SOURCE_ID" ]; then
    echo "  1. 数据准备 (SQL, 数据源: $DATA_SOURCE_ID, 排序: 1.00)"
    echo "  2. 维度目录统计 (SQL, 数据源: $DATA_SOURCE_ID, 排序: 2.00)"
    echo "  3a. 业务导向调整 (SQL, 数据源: $DATA_SOURCE_ID, 排序: 3.00)"
    echo "  3b. 指标计算-护理床日数 (SQL, 数据源: $DATA_SOURCE_ID, 排序: 3.50)"
    echo "  3c. 工作量维度统计 (SQL, 数据源: $DATA_SOURCE_ID, 排序: 3.60)"
    echo "  5. 业务价值汇总 (SQL, 数据源: $DATA_SOURCE_ID, 排序: 5.00)"
else
    echo "  1. 数据准备 (SQL, 排序: 1.00) - 需手动设置数据源"
    echo "  2. 维度目录统计 (SQL, 排序: 2.00) - 需手动设置数据源"
    echo "  3a. 业务导向调整 (SQL, 排序: 3.00) - 需手动设置数据源"
    echo "  3b. 指标计算-护理床日数 (SQL, 排序: 3.50) - 需手动设置数据源"
    echo "  3c. 工作量维度统计 (SQL, 排序: 3.60) - 需手动设置数据源"
    echo "  5. 业务价值汇总 (SQL, 排序: 5.00) - 需手动设置数据源"
fi
echo ""
print_info "前端访问:"
echo "  http://localhost/calculation-workflows/$WORKFLOW_ID"
echo ""
print_info "下一步操作:"
echo "  1. 在前端查看和编辑计算流程"
echo "  2. 根据实际维度添加更多指标计算步骤"
echo "  3. 创建计算任务并选择此流程"
echo ""
echo "========================================"

# 清理环境变量
unset PGPASSWORD

exit 0
