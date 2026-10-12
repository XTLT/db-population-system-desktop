import os
from typing import Optional, Tuple

import requests
import urllib3

from ._base import DOWNLOAD_DIR
from ._get_release_download_url import _get_release_download_url
from ._get_server_url_and_token import _get_server_url_and_token

# 自签证书场景下有意使用 verify=False，屏蔽 urllib3 的告警噪音
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def download_update(version_info: dict, progress_callback=None) -> Tuple[Optional[str], str]:
    urls = []
    if version_info.get("download_url"):
        urls.append(version_info["download_url"])
    if version_info.get("server_download_url") and version_info["server_download_url"] != version_info.get("download_url"):
        urls.append(version_info["server_download_url"])

    # 优先 Gitee Release 中的 .exe 安装包（静默安装覆盖更新最可靠），其次 .zip
    release_url = _get_release_download_url("desktop")
    if release_url:
        urls.insert(0, release_url)

    if not urls:
        return None, "未找到下载链接"

    # 文件名按下载链接后缀决定：.exe 走安装包更新，.zip 走解压更新
    if release_url and '.exe' in release_url.split('?')[0].lower():
        filename = "update_setup.exe"
    else:
        filename = "update.zip"
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)
    filepath = os.path.join(DOWNLOAD_DIR, filename)

    last_error = None
    for url in urls:
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }

            server_url, token = _get_server_url_and_token()
            if server_url and url.startswith(server_url) and token:
                headers["Authorization"] = f"Bearer {token}"

            resp = requests.get(url, stream=True, timeout=300, allow_redirects=True, headers=headers, verify=False)
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
