from typing import Optional

import requests


def _get_release_download_url(app_type: str = "desktop") -> Optional[str]:
    try:
        api_url = "https://gitee.com/api/v5/repos/tension0712/db-population-system-desktop/releases/latest"
        headers = {'User-Agent': 'Mozilla/5.0'}
        resp = requests.get(api_url, headers=headers, timeout=10)
        resp.raise_for_status()
        data = resp.json()

        assets = data.get('assets', [])
        for asset in assets:
            name = asset.get('name', '')
            if app_type == 'desktop':
                if name.endswith('.zip') and ('人口通' in name or name.startswith('population_')):
                    return asset.get('browser_download_url')
    except Exception:
        pass
    return None
