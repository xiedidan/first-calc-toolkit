@echo off
REM AI智能数据生成批处理脚本
REM 使用方法: generate_ai_data.bat [配置文件] [周期]

setlocal enabledelayedexpansion

echo ======================================================================
echo AI智能数据生成工具
echo ======================================================================
echo.

REM 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到Python，请先安装Python
    pause
    exit /b 1
)

REM 设置默认参数
set CONFIG_FILE=report_data_config.example.json
set PERIOD=2025-10
set MODEL=gpt-3.5-turbo

REM 解析命令行参数
if not "%1"=="" set CONFIG_FILE=%1
if not "%2"=="" set PERIOD=%2
if not "%3"=="" set MODEL=%3

echo 配置文件: %CONFIG_FILE%
echo 计算周期: %PERIOD%
echo AI模型: %MODEL%
echo.

REM 检查配置文件是否存在
if not exist "%CONFIG_FILE%" (
    echo [错误] 配置文件不存在: %CONFIG_FILE%
    echo.
    echo 可用的示例配置文件:
    echo   - report_data_config.example.json ^(眼科医院^)
    echo   - report_data_config_comprehensive.example.json ^(综合医院^)
    echo.
    pause
    exit /b 1
)

REM 检查API密钥
if "%OPENAI_API_KEY%"=="" (
    echo [警告] 未设置OPENAI_API_KEY环境变量
    echo.
    set /p API_KEY="请输入OpenAI API密钥: "
    if "!API_KEY!"=="" (
        echo [错误] 必须提供API密钥
        pause
        exit /b 1
    )
    set OPENAI_API_KEY=!API_KEY!
)

echo ======================================================================
echo 步骤1: 验证配置文件
echo ======================================================================
echo.

python validate_config.py "%CONFIG_FILE%"
if errorlevel 1 (
    echo.
    echo [错误] 配置文件验证失败，请修复后重试
    pause
    exit /b 1
)

echo.
echo ======================================================================
echo 步骤2: 生成数据
echo ======================================================================
echo.

set /p CONFIRM="确认开始生成数据? (Y/N): "
if /i not "%CONFIRM%"=="Y" (
    echo 已取消
    pause
    exit /b 0
)

echo.
echo 正在生成数据，请稍候...
echo.

python populate_report_data_ai.py --config "%CONFIG_FILE%" --period "%PERIOD%" --model "%MODEL%"

if errorlevel 1 (
    echo.
    echo [错误] 数据生成失败
    pause
    exit /b 1
)

echo.
echo ======================================================================
echo 数据生成完成!
echo ======================================================================
echo.
echo 下一步:
echo   1. 启动后端服务: cd backend ^&^& uvicorn app.main:app --reload
echo   2. 访问前端页面查看数据
echo   3. 检查汇总表和明细表
echo.

pause
