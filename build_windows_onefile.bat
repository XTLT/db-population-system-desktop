@echo off
chcp 65001 > nul
REM ========================================
REM 人口信息查询系统 - Windows 单文件打包
REM ========================================
REM 此脚本生成单个 .exe 文件，无需其他依赖文件
REM 文件较大，但便于分发

echo.
echo ========================================
echo   人口信息查询系统 - 单文件打包
echo ========================================
echo.

REM 检查 Python
python --version > nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到 Python
    pause
    exit /b 1
)

REM 检查虚拟环境
if not exist "venv\Scripts\activate.bat" (
    echo [信息] 创建虚拟环境...
    python -m venv venv
)

call venv\Scripts\activate.bat

echo [信息] 安装依赖...
pip install -r ..\requirements_desktop.txt -q
pip install pyinstaller -q

REM 清理
if exist "build" rd /s /q "build"
if exist "dist" rd /s /q "dist"

echo [信息] 打包单文件...
echo.

pyinstaller --onefile ^
    --windowed ^
    --name "人口信息查询系统" ^
    --hidden-import PyQt6.sip ^
    --hidden-import sqlalchemy.dialects.sqlite ^
    --exclude-module tkinter ^
    --exclude-module matplotlib ^
    --exclude-module IPython ^
    --noconfirm ^
    main.py

if exist "dist\人口信息查询系统.exe" (
    echo.
    echo ========================================
    echo   打包成功！
    echo ========================================
    echo.
    echo 输出文件: %cd%\dist\人口信息查询系统.exe
    echo.
    dir "dist\人口信息查询系统.exe" | find ".exe"
    echo.
) else (
    echo [错误] 打包失败
    pause
    exit /b 1
)

deactivate
pause
