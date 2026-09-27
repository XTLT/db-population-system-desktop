import json
from typing import Optional, Tuple

import requests

from ._base import VERSION_URLS
from .load_local_config import load_local_config
from ._check_local_server import _check_local_server
from ._get_release_download_url import _get_release_download_url


def check_update(app_type: str = "desktop") -> Tuple[Optional[dict], str]:
    config = load_local_config()
    current_code = config.get("version_code", 1)

    try:
        # Step 1: Check version.json (authoritative for version comparison)
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
                # Has update — get download URL from GitHub releases
                download_url = _get_release_download_url(app_type)
                if download_url:
                    data["download_url"] = download_url
                return data, ""
            else:
                return None, ""

        # Step 2: Fall back to local server check
        local_result = _check_local_server(app_type, current_code)
        if local_result:
            return local_result, ""

        if last_error:
            return None, f"所有更新源均无法访问: {last_error}"
        return None, ""

    except requests.exceptions.RequestException as e:
        return None, f"检查更新失败: {e}"
    except json.JSONDecodeError as e:
        return None, f"解析版本信息失败: {e}"
    except Exception as e:
        return None, f"未知错误: {e}"
