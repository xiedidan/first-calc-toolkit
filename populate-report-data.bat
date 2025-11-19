@echo off
REM 业务价值报表数据填充脚本
REM 用于快速填充报表测试数据

echo ========================================
echo 业务价值报表数据填充
echo ========================================
echo.

REM 检查是否在项目根目录
if not exist "backend\populate_report_data.py" (
    echo 错误: 请在项目根目录运行此脚本
    pause
    exit /b 1
)

REM 切换到backend目录
cd backend

REM 获取当前年月
for /f "tokens=1-3 delims=/ " %%a in ('date /t') do (
    set YEAR=%%c
    set MONTH=%%a
)

REM 确保月份是两位数
if %MONTH% LSS 10 set MONTH=0%MONTH%

set DEFAULT_PERIOD=%YEAR%-%MONTH%

echo 当前年月: %DEFAULT_PERIOD%
echo.
echo 选择操作:
echo 1. 填充当前年月数据（使用0值）
echo 2. 填充当前年月数据（使用随机值）
echo 3. 填充指定周期数据（使用0值）
echo 4. 填充指定周期数据（使用随机值）
echo 5. 退出
echo.

set /p choice="请选择 (1-5): "

if "%choice%"=="1" (
    echo.
    echo 正在填充 %DEFAULT_PERIOD% 的数据（0值）...
    python populate_report_data.py --period %DEFAULT_PERIOD%
    goto end
)

if "%choice%"=="2" (
    echo.
    echo 正在填充 %DEFAULT_PERIOD% 的数据（随机值）...
    python populate_report_data.py --period %DEFAULT_PERIOD% --random
    goto end
)

if "%choice%"=="3" (
    echo.
    set /p period="请输入计算周期 (YYYY-MM): "
    echo.
    echo 正在填充 !period! 的数据（0值）...
    python populate_report_data.py --period !period!
    goto end
)

if "%choice%"=="4" (
    echo.
    set /p period="请输入计算周期 (YYYY-MM): "
    echo.
    echo 正在填充 !period! 的数据（随机值）...
    python populate_report_data.py --period !period! --random
    goto end
)

if "%choice%"=="5" (
    echo 已取消
    goto end
)

echo 无效的选择
goto end

:end
echo.
cd ..
pause
