# ============================================================================
# 业务类别字段迁移脚本 (PowerShell)
# ============================================================================
# 功能: 自动执行业务类别字段的迁移流程
# 
# 使用方法:
#   .\migrate_business_type.ps1 -Host <host> -User <user> -Database <database>
#
# 示例:
#   .\migrate_business_type.ps1 -Host localhost -User admin -Database hospital_external_data
# ============================================================================

param(
    [Parameter(Mandatory=$true)]
    [string]$Host,
    
    [Parameter(Mandatory=$true)]
    [string]$User,
    
    [Parameter(Mandatory=$true)]
    [string]$Database
)

# 颜色输出函数
function Write-ColorOutput {
    param(
        [string]$Message,
        [string]$Color = "White"
    )
    Write-Host $Message -ForegroundColor $Color
}

# PostgreSQL 客户端路径
$PSQL_PATH = "C:\software\PostgreSQL\18\bin\psql.exe"
$PG_DUMP_PATH = "C:\software\PostgreSQL\18\bin\pg_dump.exe"

# 检查 PostgreSQL 客户端是否存在
if (-not (Test-Path $PSQL_PATH)) {
    Write-ColorOutput "❌ 错误: 找不到 psql.exe，请检查路径: $PSQL_PATH" "Red"
    exit 1
}

if (-not (Test-Path $PG_DUMP_PATH)) {
    Write-ColorOutput "❌ 错误: 找不到 pg_dump.exe，请检查路径: $PG_DUMP_PATH" "Red"
    exit 1
}

Write-ColorOutput "============================================================================" "Blue"
Write-ColorOutput "业务类别字段迁移脚本" "Blue"
Write-ColorOutput "============================================================================" "Blue"
Write-ColorOutput "数据库主机: $Host" "Green"
Write-ColorOutput "数据库用户: $User" "Green"
Write-ColorOutput "数据库名称: $Database" "Green"
Write-ColorOutput "============================================================================" "Blue"
Write-Host ""

# 确认执行
$confirmation = Read-Host "是否继续执行迁移? (y/n)"
if ($confirmation -ne 'y' -and $confirmation -ne 'Y') {
    Write-ColorOutput "已取消迁移" "Yellow"
    exit 0
}

# 步骤1: 备份数据库
Write-Host ""
Write-ColorOutput "步骤 1/3: 备份数据库" "Blue"
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$backupFile = "backup_${Database}_${timestamp}.dump"
Write-Host "备份文件: $backupFile"

try {
    & $PG_DUMP_PATH -h $Host -U $User -d $Database -F c -f $backupFile
    if ($LASTEXITCODE -eq 0) {
        Write-ColorOutput "✅ 备份成功" "Green"
    } else {
        throw "备份失败"
    }
} catch {
    Write-ColorOutput "❌ 备份失败，终止迁移" "Red"
    Write-ColorOutput "错误信息: $_" "Red"
    exit 1
}

# 步骤2: 添加字段
Write-Host ""
Write-ColorOutput "步骤 2/3: 添加 business_type 字段" "Blue"

try {
    & $PSQL_PATH -h $Host -U $User -d $Database -P pager=off -f add_business_type_to_charge_details.sql
    if ($LASTEXITCODE -eq 0) {
        Write-ColorOutput "✅ 字段添加成功" "Green"
    } else {
        throw "字段添加失败"
    }
} catch {
    Write-ColorOutput "❌ 字段添加失败" "Red"
    Write-ColorOutput "提示: 可以使用以下命令恢复备份:" "Yellow"
    Write-Host "pg_restore -h $Host -U $User -d $Database -c $backupFile"
    exit 1
}

# 步骤3: 验证结果
Write-Host ""
Write-ColorOutput "步骤 3/3: 验证迁移结果" "Blue"

$verificationSQL = @"
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
"@

try {
    & $PSQL_PATH -h $Host -U $User -d $Database -P pager=off -c $verificationSQL
    if ($LASTEXITCODE -eq 0) {
        Write-ColorOutput "✅ 验证完成" "Green"
    } else {
        Write-ColorOutput "⚠️  验证失败，请手动检查" "Yellow"
    }
} catch {
    Write-ColorOutput "⚠️  验证失败，请手动检查" "Yellow"
}

# 完成
Write-Host ""
Write-ColorOutput "============================================================================" "Blue"
Write-ColorOutput "✅ 迁移完成!" "Green"
Write-ColorOutput "============================================================================" "Blue"
Write-Host ""
Write-ColorOutput "备份文件: $backupFile" "Green"
Write-Host ""
Write-ColorOutput "后续步骤:" "Yellow"
Write-Host "1. 如果有历史数据，执行更新脚本:"
Write-Host "   & '$PSQL_PATH' -h $Host -U $User -d $Database -f update_historical_business_type.sql"
Write-Host ""
Write-Host "2. 生成新的测试数据:"
Write-Host "   & 'C:\software\anaconda3\shell\condabin\conda-hook.ps1'"
Write-Host "   conda activate hospital-backend"
Write-Host "   python backend/standard_workflow_templates/generate_test_data.py --hospital-id 1 --period 2025-11"
Write-Host ""
Write-Host "3. 运行计算任务，验证业务类别区分是否正常工作"
Write-Host ""
