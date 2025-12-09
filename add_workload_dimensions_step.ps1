# 添加工作量维度统计步骤到现有流程

$WORKFLOW_ID = 27
$DATA_SOURCE_ID = 3

if ($args.Count -gt 0) {
    $WORKFLOW_ID = $args[0]
}
if ($args.Count -gt 1) {
    $DATA_SOURCE_ID = $args[1]
}

Write-Host "============================================================" -ForegroundColor Blue
Write-Host "添加工作量维度统计步骤" -ForegroundColor Blue
Write-Host "============================================================" -ForegroundColor Blue
Write-Host ""
Write-Host "目标流程ID: $WORKFLOW_ID" -ForegroundColor Cyan
Write-Host "数据源ID: $DATA_SOURCE_ID" -ForegroundColor Cyan
Write-Host ""

# 设置数据库连接参数
$env:PGPASSWORD = "root"
$PSQL = "C:\software\PostgreSQL\18\bin\psql.exe"
$DB_HOST = "47.108.227.254"
$DB_PORT = "50016"
$DB_USER = "root"
$DB_NAME = "hospital_value"

# 查询流程信息
Write-Host "查询流程信息..." -ForegroundColor Yellow
$workflow_info = & $PSQL -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -P pager=off -t -c "SELECT w.name, w.version_id, mv.name FROM calculation_workflows w JOIN model_versions mv ON w.version_id = mv.id WHERE w.id = $WORKFLOW_ID;"

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ 查询流程失败" -ForegroundColor Red
    exit 1
}

Write-Host "流程信息: $workflow_info" -ForegroundColor Green
Write-Host ""

# 检查步骤是否已存在
Write-Host "检查步骤是否已存在..." -ForegroundColor Yellow
$existing = & $PSQL -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -P pager=off -t -c "SELECT id FROM calculation_steps WHERE workflow_id = $WORKFLOW_ID AND name = '工作量维度统计';"

if ($existing -and $existing.Trim()) {
    Write-Host "⚠️  步骤已存在 (ID=$($existing.Trim()))，跳过" -ForegroundColor Yellow
} else {
    # 读取SQL文件
    Write-Host "读取SQL文件..." -ForegroundColor Yellow
    $sql_content = Get-Content -Path "backend/standard_workflow_templates/step3c_workload_dimensions.sql" -Raw -Encoding UTF8
    
    # 转义单引号
    $sql_content = $sql_content -replace "'", "''"
    
    # 构建INSERT语句
    $insert_sql = @"
INSERT INTO calculation_steps (
    workflow_id, 
    name, 
    description, 
    code_type, 
    code_content, 
    data_source_id,
    sort_order, 
    is_enabled, 
    created_at, 
    updated_at
) 
VALUES (
    $WORKFLOW_ID,
    '工作量维度统计',
    '从工作量统计表中提取护理床日、出入转院、手术管理、手术室护理等维度的工作量',
    'sql',
    '$sql_content',
    $DATA_SOURCE_ID,
    3.60,
    TRUE,
    NOW(),
    NOW()
)
RETURNING id;
"@
    
    # 保存到临时文件
    $temp_file = [System.IO.Path]::GetTempFileName()
    $insert_sql | Out-File -FilePath $temp_file -Encoding UTF8
    
    # 执行插入
    Write-Host "插入新步骤..." -ForegroundColor Yellow
    $step_id = & $PSQL -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -P pager=off -t -f $temp_file
    
    # 删除临时文件
    Remove-Item -Path $temp_file -Force
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ 成功添加步骤 (ID=$($step_id.Trim()))" -ForegroundColor Green
    } else {
        Write-Host "❌ 添加步骤失败" -ForegroundColor Red
        exit 1
    }
}

Write-Host ""
Write-Host "当前流程的所有步骤:" -ForegroundColor Yellow
& $PSQL -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -P pager=off -c "SELECT id, name, sort_order, is_enabled FROM calculation_steps WHERE workflow_id = $WORKFLOW_ID ORDER BY sort_order;"

Write-Host ""
Write-Host "============================================================" -ForegroundColor Blue
Write-Host "完成" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Blue
