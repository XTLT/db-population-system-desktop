import os
from typing import Optional, Tuple

import requests
import urllib3

from ._base import DOWNLOAD_DIR
from ._get_release_download_url import _get_release_download_url
from ._get_server_url_and_token import _get_server_url_and_token
from ..client._base import get_client_cert_args

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
    # 只要任一候选源是 .exe 就按安装包处理（优先找 exe，找不到才用 zip）
    exe_url = None
    for u in urls:
        if '.exe' in u.split('?')[0].lower():
            exe_url = u
            break
    if exe_url:
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
            is_server_url = server_url and url.startswith(server_url)
            cert_args = None
            if is_server_url:
                if token:
                    headers["Authorization"] = f"Bearer {token}"
                # 服务器直连（mTLS）：必须出示客户端证书，否则 stunnel 拒绝握手
                cert_args = get_client_cert_args()

            resp = requests.get(
                url, stream=True, timeout=300, allow_redirects=True,
                headers=headers, verify=False, cert=cert_args,
            )
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

            if downloaded <= 0:
                last_error = "下载文件为空"
                if os.path.exists(filepath):
                    os.remove(filepath)
                continue

            # 校验文件头，防止下载到 HTML 错误页/损坏文件
            with open(filepath, 'rb') as f:
                head = f.read(4)
            if filename.endswith('.exe') and not head.startswith(b'MZ'):
                last_error = "下载内容不是有效的 EXE 文件"
                os.remove(filepath)
                continue
            if filename.endswith('.zip') and not head.startswith(b'PK'):
                last_error = "下载内容不是有效的 ZIP 文件"
                os.remove(filepath)
                continue

            return filepath, ""
        except requests.exceptions.RequestException as e:
            last_error = str(e)
            if os.path.exists(filepath):
                os.remove(filepath)
            continue

    return None, f"所有下载源均失败: {last_error}"
