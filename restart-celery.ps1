# 重启Celery Worker
Write-Host "停止Celery Worker..." -ForegroundColor Yellow

# 查找并停止celery进程
$celeryProcesses = Get-Process -Name "celery" -ErrorAction SilentlyContinue
if ($celeryProcesses) {
    $celeryProcesses | Stop-Process -Force
    Write-Host "已停止 $($celeryProcesses.Count) 个Celery进程" -ForegroundColor Green
} else {
    Write-Host "未找到运行中的Celery进程" -ForegroundColor Cyan
}

Write-Host "`n初始化Conda环境..." -ForegroundColor Cyan
& 'C:\software\anaconda3\shell\condabin\conda-hook.ps1'
conda activate hospital-backend

Write-Host "`n启动Celery Worker..." -ForegroundColor Cyan
cd backend
Start-Process powershell -ArgumentList "-NoExit", "-Command", "& 'C:\software\anaconda3\shell\condabin\conda-hook.ps1'; conda activate hospital-backend; celery -A app.celery_app worker --loglevel=info --pool=solo"

Write-Host "`nCelery Worker已在新窗口中启动" -ForegroundColor Green
Write-Host "请检查新窗口确认启动成功" -ForegroundColor Yellow
