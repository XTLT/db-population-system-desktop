import ssl
from typing import Optional, Dict

import requests

from ._get_server_url_and_token import _get_server_url_and_token


def _check_local_server(app_type: str, current_code: int) -> Optional[Dict]:
    """Fallback: query local server's /api/update/check endpoint."""
    server_url, token = _get_server_url_and_token()
    if not server_url:
        return None

    try:
        url = f"{server_url}/api/update/check"
        params = {"type": app_type, "version_code": current_code}
        headers = {}
        if token:
            headers["Authorization"] = f"Bearer {token}"

        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE

        resp = requests.get(url, params=params, headers=headers, timeout=10, verify=False)
        resp.raise_for_status()
        data = resp.json()

        if data.get("has_update"):
            download_url = data.get("download_url", "")
            if download_url and not download_url.startswith("http"):
                data["download_url"] = f"{server_url}{download_url}"
            return data
    except Exception:
        pass
    return None
