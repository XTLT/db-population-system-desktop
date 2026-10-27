import json
import os
import sys
from typing import Optional, Tuple

import requests

from ._base import VERSION_URLS  # noqa: F401  (保留引用，兼容旧配置导入)
from .load_local_config import load_local_config
from ._check_local_server import _check_local_server


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
        # Step 1: 服务器主源唯一（更新包只发布到自建服务器，不再推送 Gitee/GitHub）
        # 服务器不可达时直接报错重试，绝不再回退 Gitee——Gitee 上可能是旧版本包，
        # 引导装回旧包会重新引入旧 bug（历史事故 A13）。
        local_result = _check_local_server(app_type, current_code)
        if local_result is None:
            # 服务器不可达/异常
            return None, "无法连接更新服务器，请检查网络后重试"
        if local_result.get("has_update"):
            return local_result, ""
        # 服务器可达且已是最新版本：返回空信息，由上层显示“当前已是最新版本”
        return None, ""

    except requests.exceptions.RequestException as e:
        return None, f"检查更新失败: {e}"
    except json.JSONDecodeError as e:
        return None, f"解析版本信息失败: {e}"
    except Exception as e:
        return None, f"未知错误: {e}"
