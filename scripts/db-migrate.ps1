# 数据库迁移脚本
# 用于执行Alembic数据库迁移

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "数据库迁移工具" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 检查是否在项目根目录
if (-not (Test-Path "backend\alembic")) {
    Write-Host "错误: 请在项目根目录执行此脚本" -ForegroundColor Red
    exit 1
}

# 进入backend目录
Set-Location backend

Write-Host "1. 检查Conda环境..." -ForegroundColor Yellow
$condaEnv = conda env list | Select-String "hospital_value"
if (-not $condaEnv) {
    Write-Host "错误: Conda环境 'hospital_value' 不存在" -ForegroundColor Red
    Write-Host "请先运行: .\scripts\setup-conda-env.ps1" -ForegroundColor Yellow
    Set-Location ..
    exit 1
}
Write-Host "✓ Conda环境已找到" -ForegroundColor Green

Write-Host ""
Write-Host "2. 查看当前迁移状态..." -ForegroundColor Yellow
conda run -n hospital_value alembic current
Write-Host ""

Write-Host "3. 查看迁移历史..." -ForegroundColor Yellow
conda run -n hospital_value alembic history
Write-Host ""

Write-Host "4. 执行迁移..." -ForegroundColor Yellow
$confirm = Read-Host "是否执行迁移到最新版本? (y/n)"
if ($confirm -eq "y" -or $confirm -eq "Y") {
    conda run -n hospital_value alembic upgrade head
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "✓ 迁移执行成功!" -ForegroundColor Green
        Write-Host ""
        Write-Host "5. 验证迁移结果..." -ForegroundColor Yellow
        conda run -n hospital_value alembic current
    } else {
        Write-Host ""
        Write-Host "✗ 迁移执行失败!" -ForegroundColor Red
        Write-Host "请检查错误信息并修复问题" -ForegroundColor Yellow
    }
} else {
    Write-Host "迁移已取消" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "迁移工具执行完成" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# 返回项目根目录
Set-Location ..
