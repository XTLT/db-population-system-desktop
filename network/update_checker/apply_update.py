import os
import sys


def apply_update(filepath: str):
    """解压 ZIP 更新包并自动替换整个应用目录后重启。

    filepath 指向下载的 update.zip。ZIP 包内应包含完整的应用文件
    （人口通.exe + _internal/ 目录等），解压后直接覆盖当前应用目录。
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

    import zipfile
    if not zipfile.is_zipfile(zip_path):
        return False, "下载的文件不是有效的 ZIP 格式"

    if sys.platform == 'win32':
        bat_path = os.path.join(app_dir, '_auto_update.bat')
        exe_name = os.path.basename(current_exe)
        bat_content = f'''@echo off
chcp 65001 >nul
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
