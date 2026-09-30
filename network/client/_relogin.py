# -*- coding: utf-8 -*-
"""401 自动重新登录：会话过期时异步弹出登录框。"""

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer


def _relogin():
    """会话过期（401）时自动弹出登录框重新登录。

    QDialog 只能在主线程执行，此处用 QTimer.singleShot 投递到主线程（线程安全）。
    登录成功后通过 set_token 更新全局 TOKEN，用户后续操作自动生效。
    """
    app = QApplication.instance()
    if app is None:
        return
    from . import _base
    if not _base.SERVER_URL:
        return

    def _do():
        from dialogs.user_dialog import LoginDialog
        dlg = LoginDialog()
        if dlg.exec():
            token = dlg.get_token()
            if token:
                from ._base import set_token
                set_token(token)

    QTimer.singleShot(0, _do)
