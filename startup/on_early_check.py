"""启动早期检查更新后的分支处理。

检查完成发现新版本时：若主窗口尚未创建，用轻量宿主直接弹窗
（模态，用户可先"立即更新"，更新重启后只需登录一次）；若已进入
主窗口则用主窗口承载。无更新/失败静默。
"""


def on_early_check(result, error, window_ref, early_check_done, on_continue):
    if not (result and not error):
        on_continue()
        return

    early_check_done[0] = True
    if window_ref[0] is not None:
        window_ref[0]._show_update_dialog(result)
        on_continue()
        return

    # 主窗口尚未创建：用轻量宿主承载更新弹窗（复用主窗口的两个方法）
    from main import MainWindow

    class _UpdateHost:
        pass

    _UpdateHost._show_update_dialog = MainWindow._show_update_dialog
    _UpdateHost._on_version_check_done = MainWindow._on_version_check_done

    host = _UpdateHost()
    host._show_update_dialog(result)
    dlg = getattr(host, '_update_dialog', None)
    if dlg is not None:
        # 非模态 + 独立置顶窗口：按钮始终可点，与 ConnectDialog.exec()
        # 的应用级模态互斥问题彻底消除。用户处理完（立即更新 / 暂不更新 /
        # 直接关闭）后由 finished 信号驱动继续启动流程。
        dlg.setModal(False)
        dlg.show()
        dlg.raise_()
        dlg.activateWindow()
        dlg.finished.connect(lambda *_: on_continue())
    else:
        on_continue()
