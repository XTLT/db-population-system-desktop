                      
                       
                       \
\
   

import os
import sys
import json
import hashlib
import requests
from typing import Optional, Dict, Tuple

          
VERSION_URLS = [
    "https://gitee.com/tension0712/population-system/raw/main/updates/version.json",
]

def _get_config_dir():
                  
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))

CONFIG_DIR = _get_config_dir()
CONFIG_FILE = os.path.join(CONFIG_DIR, "version_config.json")
DOWNLOAD_DIR = os.path.join(CONFIG_DIR, "downloads")


def load_local_config() -> Dict:
                  
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            pass
    return {"current_version": "1.0.0", "version_code": 1}


def save_local_config(config: Dict):
                  
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
    except Exception:
        pass


def check_update(app_type: str = "desktop") -> Tuple[Optional[Dict], str]:
\
\
\
\
\
\
\
\
       
    config = load_local_config()
    current_version = config.get("current_version", "1.0.0")
    current_code = config.get("version_code", 1)
    
    try:
        data = None
        last_error = None
        for url in VERSION_URLS:
            try:
                resp = requests.get(url, timeout=10)
                resp.raise_for_status()
                data = resp.json()
                break
            except Exception as e:
                last_error = e
                continue
        
        if data is None:
            return None, f"所有更新源均无法访问: {last_error}"
        
                         
        if app_type == "desktop":
            latest_version = data.get("desktop_version", data.get("latest_version", "0.0.0"))
            latest_code = data.get("desktop_version_code", data.get("version_code", 0))
        else:
            latest_version = data.get("server_version", data.get("latest_version", "0.0.0"))
            latest_code = data.get("server_version_code", data.get("version_code", 0))
        
              
        if latest_code > current_code:
            return data, ""
        else:
            return None, ""
            
    except requests.exceptions.RequestException as e:
        return None, f"检查更新失败: {e}"
    except json.JSONDecodeError as e:
        return None, f"解析版本信息失败: {e}"
    except Exception as e:
        return None, f"未知错误: {e}"


def _get_release_download_url(app_type: str = "desktop") -> Optional[str]:
                                 
    try:
        api_url = "https://gitee.com/api/v5/repos/tension0712/population-system/releases/latest"
        headers = {'User-Agent': 'Mozilla/5.0'}
        resp = requests.get(api_url, headers=headers, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        
        assets = data.get('assets', [])
        for asset in assets:
            name = asset.get('name', '')
            if app_type == 'desktop' and '服务器' not in name and '服务' not in name and name.endswith('.exe'):
                return asset.get('browser_download_url')
            elif app_type == 'server' and ('服务器' in name or '服务' in name) and name.endswith('.exe'):
                return asset.get('browser_download_url')
    except Exception:
        pass
    return None


def download_update(version_info: Dict, progress_callback=None) -> Tuple[Optional[str], str]:
\
\
\
\
\
\
\
\
\
       
    urls = []
    if version_info.get("download_url"):
        urls.append(version_info["download_url"])
    if version_info.get("server_download_url") and version_info["server_download_url"] != version_info.get("download_url"):
        urls.append(version_info["server_download_url"])
    
    release_url = _get_release_download_url("desktop")
    if release_url and release_url not in urls:
        urls.append(release_url)
    
    if not urls:
        return None, "未找到下载链接"
    
    filename = "update.exe"
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)
    filepath = os.path.join(DOWNLOAD_DIR, filename)
    
    last_error = None
    for url in urls:
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            resp = requests.get(url, stream=True, timeout=300, allow_redirects=True, headers=headers)
            resp.raise_for_status()
            
            total = int(resp.headers.get('content-length', 0))
            downloaded = 0
            
            with open(filepath, 'wb') as f:
                for chunk in resp.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if progress_callback:
                            progress_callback(downloaded, total)
            
            if downloaded > 0:
                return filepath, ""
            else:
                last_error = "下载文件为空"
                if os.path.exists(filepath):
                    os.remove(filepath)
                continue
                
        except requests.exceptions.RequestException as e:
            last_error = str(e)
            if os.path.exists(filepath):
                os.remove(filepath)
            continue
    
    return None, f"所有下载源均失败: {last_error}"


def calculate_sha256(filepath: str) -> str:
                     
    sha256_hash = hashlib.sha256()
    with open(filepath, "rb") as f:
        for byte_block in iter(lambda: f.read(8192), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


def verify_file(filepath: str, expected_checksum: str) -> bool:
                 
    if not expected_checksum or not expected_checksum.startswith("sha256:"):
        return True              
    
    expected_hash = expected_checksum[7:]
    actual_hash = calculate_sha256(filepath)
    return expected_hash == actual_hash


def update_local_version(version_info: Dict, app_type: str = "desktop"):
                  
    config = load_local_config()
    if app_type == "desktop":
        config["current_version"] = version_info.get("desktop_version", config.get("current_version", "1.0.0"))
        config["version_code"] = version_info.get("desktop_version_code", config.get("version_code", 1) + 1)
    else:
        config["current_version"] = version_info.get("server_version", config.get("current_version", "1.0.0"))
        config["version_code"] = version_info.get("server_version_code", config.get("version_code", 1) + 1)
    save_local_config(config)


def apply_update(filepath: str):
    if not getattr(sys, 'frozen', False):
        return False, "非打包环境，无法自动更新"
    
    current_exe = sys.executable
    app_dir = os.path.dirname(current_exe)
    new_exe = filepath
    
    dangerous_chars = ['$', '`', '"', "'", '\\', '\n', '\r', ';', '&', '|', '<', '>', '(', ')']
    
    def is_path_safe(path):
        return not any(char in path for char in dangerous_chars)
    
    if not is_path_safe(current_exe) or not is_path_safe(new_exe) or not is_path_safe(app_dir):
        return False, "安全错误：更新路径包含不安全字符，拒绝自动更新"
    
    if sys.platform == 'win32':
        bat_path = os.path.join(app_dir, '_auto_update.bat')
        bat_content = f'''@echo off
chcp 65001 >nul
title 自动更新中...
echo 正在关闭程序...
taskkill /f /t /im "{os.path.basename(current_exe)}" >nul 2>&1
echo 等待文件释放...
:wait_loop
timeout /t 2 /nobreak >nul
copy /y "{new_exe}" "{current_exe}" >nul 2>&1
if errorlevel 1 goto wait_loop
echo 更新完成，正在启动...
del "{new_exe}" >nul 2>&1
start "" "{current_exe}"
timeout /t 3 /nobreak >nul
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
cp -f "{new_exe}" "{current_exe}"
chmod +x "{current_exe}"
rm -f "{new_exe}"
"{current_exe}" &
rm -f "{script_path}"
'''
        with open(script_path, 'w') as f:
            f.write(script_content)
        os.chmod(script_path, 0o755)
        import subprocess
        subprocess.Popen(['nohup', script_path], start_new_session=True)
        return True, ""
