@echo off
chcp 65001 >nul
echo ========================================
echo 科室汇总表计算验证
echo ========================================
echo.

cd /d "%~dp0backend"

echo 选择操作:
echo 1. 验证最新任务
echo 2. 验证指定周期
echo 3. 验证指定任务ID
echo.

set /p choice="请输入选项 (1-3): "

if "%choice%"=="1" (
    echo.
    echo 正在验证最新任务...
    python verify_summary_calculation.py
) else if "%choice%"=="2" (
    echo.
    set /p period="请输入计算周期 (YYYY-MM): "
    echo.
    echo 正在验证周期 %period% 的任务...
    python verify_summary_calculation.py --period %period%
) else if "%choice%"=="3" (
    echo.
    set /p task_id="请输入任务ID: "
    echo.
    echo 正在验证任务 %task_id%...
    python verify_summary_calculation.py --task-id %task_id%
) else (
    echo 无效的选项
    pause
    exit /b 1
)

echo.
pause
