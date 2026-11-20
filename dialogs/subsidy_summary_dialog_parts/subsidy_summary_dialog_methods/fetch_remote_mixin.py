from .._imports import *
from .._consts import *
from ..funcs import *

_HEADERS = None
_LOCAL_MODULES = None
_to_amount = None

class SubsidySummaryDialogFetchRemoteMixin:
    def _fetch_remote(self):
        from network.client import _request

        data = _request("GET", f"/api/person/{self.id_card}/subsidies")
        return (
            data.get("records", []),
            data.get("by_module", []),
            data.get("total_count", 0),
            bool(data.get("truncated", False)),
        )
