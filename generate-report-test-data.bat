@echo off
REM 生成业务价值报表测试数据
REM 
REM 用法:
REM   generate-report-test-data.bat              - 生成填0的测试数据
REM   generate-report-test-data.bat --random     - 生成随机值的测试数据

echo ========================================
echo 生成业务价值报表测试数据
echo ========================================
echo.

cd backend

REM 检查是否传入了参数
if "%1"=="--random" (
    echo 使用随机值生成测试数据...
    python generate_report_test_data.py --random
) else (
    echo 使用0值生成测试数据...
    python generate_report_test_data.py
)

cd ..

echo.
echo 按任意键退出...
pause >nul
