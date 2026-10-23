import os
from typing import Optional, Tuple

import requests
import urllib3

from ._base import DOWNLOAD_DIR
from ._get_server_url_and_token import _get_server_url_and_token
from ..client._base import get_client_cert_args

# 自签证书场景下有意使用 verify=False，屏蔽 urllib3 的告警噪音
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def _sha256_file(path: str) -> str:
    import hashlib
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def download_update(version_info: dict, progress_callback=None) -> Tuple[Optional[str], str]:
    urls = []
    if version_info.get("download_url"):
        urls.append(version_info["download_url"])
    if version_info.get("server_download_url") and version_info["server_download_url"] != version_info.get("download_url"):
        urls.append(version_info["server_download_url"])

    # 只使用服务器接口下发的下载地址（服务器主源，或服务器按旧版本下发的
    # Gitee 外部 URL）。绝不主动去查 Gitee latest release——那里可能是
    # 旧版本包，装回旧包会重新引入旧 bug（历史事故 A13）。
    if not urls:
        return None, "未找到下载链接"

    # 文件名按下载链接后缀决定：.exe 走安装包更新，.zip 走解压更新。
    # 服务器下发的 URL 是 API 端点（/api/update/download?type=desktop），不带 .exe 后缀，
    # 此时按安装包（exe）处理——服务器 desktop 更新包即 exe（历史事故 A14）。
    exe_url = None
    zip_url = None
    for u in urls:
        path_part = u.split('?')[0].lower()
        if '.exe' in path_part:
            exe_url = u
            break
        if '.zip' in path_part and zip_url is None:
            zip_url = u
    if exe_url:
        filename = "update_setup.exe"
    elif zip_url:
        filename = "update.zip"
    else:
        filename = "update_setup.exe"  # 服务器 API 端点默认 exe
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

            # SHA256 强校验：服务器清单里的 checksum 必须与下载文件一致，
            # 防止下载到旧包/损坏包后静默安装（历史事故 A13）
            expected_checksum = (version_info.get("checksum") or "").strip().lower()
            if expected_checksum:
                actual = _sha256_file(filepath)
                if actual != expected_checksum:
                    last_error = f"SHA256 校验失败（期望 {expected_checksum[:16]}...，实际 {actual[:16]}...）"
                    if os.path.exists(filepath):
                        os.remove(filepath)
                    continue

            return filepath, ""
        except requests.exceptions.RequestException as e:
            last_error = str(e)
            if os.path.exists(filepath):
                os.remove(filepath)
            continue

    return None, f"所有下载源均失败: {last_error}"
