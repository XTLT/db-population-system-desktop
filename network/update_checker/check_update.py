import json
import os
import sys
from typing import Optional, Tuple

import requests

from ._base import VERSION_URLS
from .load_local_config import load_local_config
from ._check_local_server import _check_local_server
from ._get_release_download_url import _get_release_download_url


def _get_bundled_version_code() -> int:
    """读取程序内置 updates/version.json 的 desktop_version_code。

    与左下角显示的 APP_VERSION 同源，保证“当前版本”永远与真实程序一致，
    避免外部 version_config.json 被提前写入新版本号导致误判“已是最新”。
    """
    candidates = []
    if getattr(sys, 'frozen', False):
        meipass = getattr(sys, '_MEIPASS', os.path.dirname(sys.executable))
        candidates.append(os.path.join(meipass, 'updates', 'version.json'))
    else:
        # 开发模式：network/update_checker/check_update.py -> 项目根/updates/version.json
        candidates.append(os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))),
            'updates', 'version.json'))
    for p in candidates:
        if os.path.exists(p):
            try:
                with open(p, encoding='utf-8') as f:
                    return int(json.load(f).get('desktop_version_code') or 0)
            except Exception:
                pass
    return 0


def check_update(app_type: str = "desktop") -> Tuple[Optional[dict], str]:
    config = load_local_config()
    # 当前版本优先取程序内置版本号（与 APP_VERSION 同源）；
    # 取不到时才回退外部 version_config.json。
    bundled_code = _get_bundled_version_code()
    current_code = bundled_code if bundled_code > 0 else config.get("version_code", 1)

    try:
        # Step 1: 服务器主源优先（更新包只发布到自建服务器，不再推送 Gitee/GitHub）
        local_result = _check_local_server(app_type, current_code)
        if local_result:
            return local_result, ""

        # Step 2: Gitee 兜底（仅兼容仍在使用旧 Gitee 更新源的版本；新更新包不再推送）
        data = None
        last_error = None
        import time
        for url in VERSION_URLS:
            try:
                cache_bust_url = f"{url}?t={int(time.time())}"
                resp = requests.get(cache_bust_url, timeout=10)
                resp.raise_for_status()
                data = resp.json()
                break
            except Exception as e:
                last_error = e
                continue

        if data:
            if app_type == "desktop":
                latest_code = data.get("desktop_version_code", data.get("version_code", 0))
            else:
                latest_code = data.get("server_version_code", data.get("version_code", 0))

            if latest_code > current_code:
                # Has update — get download URL from Gitee releases
                download_url = _get_release_download_url(app_type)
                if download_url:
                    data["download_url"] = download_url
                return data, ""
            else:
                return None, ""

        if last_error:
            return None, f"所有更新源均无法访问: {last_error}"
        return None, ""

    except requests.exceptions.RequestException as e:
        return None, f"检查更新失败: {e}"
    except json.JSONDecodeError as e:
        return None, f"解析版本信息失败: {e}"
    except Exception as e:
        return None, f"未知错误: {e}"
