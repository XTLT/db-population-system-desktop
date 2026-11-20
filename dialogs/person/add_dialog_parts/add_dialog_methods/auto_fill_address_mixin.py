from .._imports import *
from .._consts import *
from ..funcs import *



class AddDialogAutoFillAddressMixin:
    def _auto_fill_address(self):
        if get_server_url():
            try:
                from network.client import api_family
                members = api_family(self.hu_hao)
                for m in members:
                    addr = m.get('address', '') if isinstance(m, dict) else getattr(m, 'address', '')
                    if addr and addr.strip():
                        self.txt_address.setEnabled(True)
                        self.txt_address.setText(addr.strip())
                        self.txt_address.setEnabled(False)
                        grp = m.get('group_name', '') if isinstance(m, dict) else getattr(m, 'group_name', '')
                        if grp and grp.strip():
                            self.txt_group_name.setText(grp.strip())
                        return
            except Exception:
                pass
        else:
            from core.database import get_family_members
            members = get_family_members(self.hu_hao)
            for m in members:
                if m.address and m.address.strip():
                    self.txt_address.setEnabled(True)
                    self.txt_address.setText(m.address.strip())
                    self.txt_address.setEnabled(False)
                    grp = getattr(m, 'group_name', '') or ''
                    if grp and grp.strip():
                        self.txt_group_name.setText(grp.strip())
                    return
