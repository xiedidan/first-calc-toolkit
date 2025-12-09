# 更新指定的Step 5步骤
Write-Host "初始化Conda环境..." -ForegroundColor Cyan
& 'C:\software\anaconda3\shell\condabin\conda-hook.ps1'
conda activate hospital-backend

Write-Host "`n运行更新脚本..." -ForegroundColor Cyan
python update_step5_specific.py

Write-Host "`n按任意键退出..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
