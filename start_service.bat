@echo off
chcp 65001
setlocal enabledelayedexpansion

NET SESSION >nul 2>&1
if %errorLevel% neq 0 (
    echo 需要管理员权限运行此命令
    echo 请右键点击此批处理文件，选择"以管理员身份运行"
    pause
    exit /b 1
)

set "CONFIG_FILE=%~dp0config.ini"
if not exist "%CONFIG_FILE%" (
    echo Error: config.ini not found
    exit /b 1
)

for /f "usebackq tokens=2 delims==" %%a in (`type "%CONFIG_FILE%" ^| findstr /C:"python_path"`) do set "PYTHON_PATH=%%a"
set "PYTHON_PATH=!PYTHON_PATH: =!"
set "SCRIPT_PATH=%~dp0video_converter.py"

if not exist "!PYTHON_PATH!" (
    echo Error: Python interpreter not found at: !PYTHON_PATH!
    echo Please check python_path in config.ini
    exit /b 1
)

if "%1"=="" (
    echo 请指定参数: start, install, remove, 或 stop
    exit /b 1
)

echo Using Python: !PYTHON_PATH!
echo Running script: !SCRIPT_PATH!

if "%1"=="install" (
    echo [信息] 正在安装服务...
    "!PYTHON_PATH!" "!SCRIPT_PATH!" --startup auto install
    sc description HandBrakeConverter "自动监控并转换视频文件的服务"
    echo [信息] 服务安装完成，请检查服务管理器
) else if "%1"=="remove" (
    echo [信息] 正在移除服务...
    "!PYTHON_PATH!" "!SCRIPT_PATH!" remove
) else (
    "!PYTHON_PATH!" "!SCRIPT_PATH!" %1
)

if "%1"=="install" (
    echo.
    echo [提示] 请在服务管理器中查看 "HandBrakeConverter" 服务
    echo [提示] 可以通过以下命令启动服务：
    echo       net start HandBrakeConverter
    pause
)
