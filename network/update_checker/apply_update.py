import os
import sys


def apply_update(filepath: str):
    """应用更新包。

    - .exe（Inno 安装包）：杀进程 -> 静默安装 -> 安装器自动启动新版
    - .zip：解压覆盖整个应用目录
    """
    if not getattr(sys, 'frozen', False):
        return False, "非打包环境，无法自动更新"

    current_exe = sys.executable
    app_dir = os.path.dirname(current_exe)
    zip_path = filepath

    dangerous_chars = ['$', '`', '"', "'", '\n', '\r', ';', '&', '|', '<', '>', '(', ')']

    def is_path_safe(path):
        return not any(char in path for char in dangerous_chars)

    if not is_path_safe(current_exe) or not is_path_safe(zip_path) or not is_path_safe(app_dir):
        return False, "安全错误：更新路径包含不安全字符，拒绝自动更新"

    # ===== .exe 安装包更新 =====
    if zip_path.lower().endswith('.exe'):
        if sys.platform != 'win32':
            return False, "仅 Windows 支持安装包更新"
        bat_path = os.path.join(app_dir, '_auto_update.bat')
        exe_name = os.path.basename(current_exe)
        installer = zip_path
        # bat 以 GBK 编码写入，cmd 默认代码页(936)即可正确解析中文路径；
        # 因此不能写 chcp 65001（会把 GBK 字节按 UTF-8 解析导致中文路径乱码）
        bat_content = f'''@echo off
title 自动更新中...
cd /d "%~dp0"
echo ======================================== > _auto_update.log
echo   正在更新 人口通 桌面客户端... >> _auto_update.log
echo ======================================== >> _auto_update.log
echo [%date% %time%] 开始更新 >> _auto_update.log
echo 关闭旧进程: {exe_name} >> _auto_update.log
taskkill /f /t /im "{exe_name}" >> _auto_update.log 2>&1
echo 等待文件释放... >> _auto_update.log
timeout /t 2 /nobreak >nul
echo 运行安装程序静默安装... >> _auto_update.log
start "" /wait "{installer}" /VERYSILENT /SUPPRESSMSGBOXES /NORESTART >> _auto_update.log 2>&1
echo 安装完成 >> _auto_update.log
del "{installer}" >> _auto_update.log 2>&1
echo [%date% %time%] 更新完成 >> _auto_update.log
del "%~f0"
'''
        with open(bat_path, 'w', encoding='gbk') as f:
            f.write(bat_content)

        os.startfile(bat_path)
        return True, ""

    # ===== .zip 解压更新 =====
    import zipfile
    if not zipfile.is_zipfile(zip_path):
        return False, "下载的文件不是有效的 ZIP 格式"

    if sys.platform == 'win32':
        bat_path = os.path.join(app_dir, '_auto_update.bat')
        exe_name = os.path.basename(current_exe)
        # bat 以 GBK 编码写入，cmd 默认代码页(936)即可正确解析中文路径；
        # 因此不能写 chcp 65001（会把 GBK 字节按 UTF-8 解析导致中文路径乱码）
        bat_content = f'''@echo off
title 自动更新中...
cd /d "%~dp0"
echo ======================================== > _auto_update.log
echo   正在更新 人口通 桌面客户端... >> _auto_update.log
echo ======================================== >> _auto_update.log
echo [%date% %time%] 开始更新 >> _auto_update.log
echo 关闭旧进程: {exe_name} >> _auto_update.log
taskkill /f /t /im "{exe_name}" >> _auto_update.log 2>&1
echo 等待文件释放... >> _auto_update.log
timeout /t 2 /nobreak >nul
echo 解压更新包: {zip_path} >> _auto_update.log
powershell -NoProfile -Command "Expand-Archive -LiteralPath '{zip_path}' -DestinationPath '{app_dir}' -Force" >> _auto_update.log 2>&1
if errorlevel 1 (
    echo 解压失败！请手动解压 {zip_path} 到 {app_dir}，或查看 _auto_update.log >> _auto_update.log
    echo 解压失败！请手动解压 {zip_path} 到 {app_dir}，或查看 _auto_update.log
    pause
    exit /b 1
)
echo 解压完成，启动程序... >> _auto_update.log
start "" "{current_exe}"
echo 清理更新包与脚本... >> _auto_update.log
timeout /t 3 /nobreak >nul
del "{zip_path}" >> _auto_update.log 2>&1
echo [%date% %time%] 更新完成 >> _auto_update.log
del "%~f0"
'''
        with open(bat_path, 'w', encoding='gbk') as f:
            f.write(bat_content)

        os.startfile(bat_path)
        return True, ""
    else:
        script_path = os.path.join(app_dir, '_auto_update.sh')
        if not is_path_safe(script_path):
            return False, "安全错误：脚本路径包含不安全字符，拒绝自动更新"

        script_content = f'''#!/bin/bash
sleep 2
killall "{os.path.basename(current_exe)}" 2>/dev/null
sleep 1
cd "{app_dir}"
unzip -o "{zip_path}" -d "{app_dir}"
rm -f "{zip_path}"
"{current_exe}" &
rm -f "{script_path}"
'''
        with open(script_path, 'w') as f:
            f.write(script_content)
        os.chmod(script_path, 0o755)
        import subprocess
        subprocess.Popen(['nohup', script_path], start_new_session=True)
        return True, ""
