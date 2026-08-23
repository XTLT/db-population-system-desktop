@echo off
chcp 65001 > nul
REM ========================================
REM 人口信息查询系统 - Windows 打包脚本
REM ========================================

echo.
echo ========================================
echo   人口信息查询系统 - Windows 打包
echo ========================================
echo.

REM 检查 Python
python --version > nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到 Python，请先安装 Python 3.10+
    pause
    exit /b 1
)

REM 检查虚拟环境
if not exist "venv\Scripts\activate.bat" (
    echo [信息] 创建虚拟环境...
    python -m venv venv
)

REM 激活虚拟环境
call venv\Scripts\activate.bat

REM 升级 pip
echo [信息] 升级 pip...
python -m pip install --upgrade pip -q

REM 安装依赖
echo [信息] 安装依赖包...
pip install -r ..\requirements_desktop.txt -q
pip install pyinstaller -q

REM 检查 PyInstaller
pyinstaller --version > nul 2>&1
if errorlevel 1 (
    echo [错误] PyInstaller 安装失败
    pause
    exit /b 1
)

REM 清理旧的构建文件
if exist "build" rd /s /q "build"
if exist "dist" rd /s /q "dist"

REM 开始打包
echo [信息] 开始打包...
echo.

REM 使用 spec 文件打包
pyinstaller build_windows.spec --clean

REM 检查打包结果
if exist "dist\人口信息查询系统\人口信息查询系统.exe" (
    echo.
    echo ========================================
    echo   打包成功！
    echo ========================================
    echo.
    echo 输出目录: %cd%\dist\人口信息查询系统
    echo 可执行文件: 人口信息查询系统.exe
    echo.
    
    REM 计算文件大小
    for /f %%A in ('dir /s /b "dist\人口信息查询系统" 2^> nul ^| find /c /v ""') do set FILE_COUNT=%%A
    echo 文件数量: %FILE_COUNT% 个文件
    
    REM 显示目录大小
    for /f "tokens=3" %%A in ('dir /s "dist\人口信息查询系统" 2^> nul ^| find "个文件"') do set DIR_SIZE=%%A
    echo 总大小: %DIR_SIZE%
    
    echo.
    echo 使用方法:
    echo   1. 将 dist\人口信息查询系统 文件夹复制到目标电脑
    echo   2. 运行 人口信息查询系统.exe
    echo.
    
    REM 询问是否打开输出目录
    set /p OPEN_DIR="是否打开输出目录? (y/n): "
    if /i "%OPEN_DIR%"=="y" (
        explorer "dist\人口信息查询系统"
    )
) else (
    echo.
    echo [错误] 打包失败，请检查错误信息
    pause
    exit /b 1
)

REM 退出虚拟环境
deactivate

pause
