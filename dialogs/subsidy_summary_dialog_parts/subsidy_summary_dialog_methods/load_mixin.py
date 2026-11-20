from .._imports import *
from .._consts import *
from ..funcs import *

_HEADERS = None
_LOCAL_MODULES = None
_to_amount = None

class SubsidySummaryDialogLoadMixin:
    def _load(self):
        if self.is_network_mode:
            records, by_module, total_count, truncated = self._fetch_remote()
        else:
            records, by_module, total_count, truncated = self._query_local()
        self._render(records, by_module, total_count, truncated)
