"""桌面端版本号读取（与发布版本保持一致）。"""

import os
import sys

from .paths import PROJECT_ROOT


def load_app_version() -> str:
    """从 updates/version.json 读取桌面端版本号，与发布版本保持一致。"""
    try:
        candidates = []
        if getattr(sys, 'frozen', False):
            # PyInstaller onedir：datas 打包到 sys._MEIPASS 下的 updates/
            meipass = getattr(sys, '_MEIPASS', os.path.dirname(sys.executable))
            candidates.append(os.path.join(meipass, 'updates', 'version.json'))
            # 兼容旧布局：exe 同级 updates/
            candidates.append(os.path.join(os.path.dirname(sys.executable), 'updates', 'version.json'))
        else:
            candidates.append(os.path.join(PROJECT_ROOT, 'updates', 'version.json'))
        for p in candidates:
            if os.path.exists(p):
                import json
                with open(p, encoding='utf-8') as f:
                    return (json.load(f).get('desktop_version') or '').strip()
    except Exception:
        pass
    return ""
