import os
from PyQt6.QtWidgets import QHBoxLayout, QApplication, QPushButton
from network.update_checker import update_local_version, verify_file, apply_update
from .workers import DownloadWorker


def _on_version_check_done(self, version_info, error):
    self._update_progress.setRange(0, 1)
    self._update_progress.setValue(1)

    if error:
        self._update_status.setText("检查更新失败")
        self._update_status.setStyleSheet("color: red;")
        self._update_info.setVisible(True)
        self._update_info.setText(error)
        self._update_btn_close.setVisible(True)
        return

    if not version_info:
        self._update_status.setText("当前已是最新版本")
        self._update_status.setStyleSheet("color: green;")
        self._update_btn_close.setVisible(True)
        return

    latest_version = version_info.get("desktop_version", version_info.get("latest_version", ""))
    release_notes = version_info.get("desktop_release_notes", version_info.get("release_notes", "无"))
    file_size = version_info.get("desktop_file_size", version_info.get("file_size", 0))

    self._update_status.setText(f"发现新版本：{latest_version}")
    self._update_status.setStyleSheet("color: #0066CC; font-weight: bold;")

    size_text = ""
    if file_size > 1024 * 1024:
        size_text = f"文件大小：{file_size / 1024 / 1024:.1f} MB"
    elif file_size > 1024:
        size_text = f"文件大小：{file_size / 1024:.1f} KB"

    self._update_info.setVisible(True)
    self._update_info.setText(f"更新内容：\n{release_notes}\n\n{size_text}")
    self._update_info.setStyleSheet("background-color: #F5F5F5;")

    self._update_btn_close.setText("暂不更新")
    self._update_btn_close.setVisible(True)

    if hasattr(self, '_update_btn_now') and self._update_btn_now:
        return

    btn_update = QPushButton("立即更新")
    btn_update.setStyleSheet("background-color: #0078D4; color: white; font-weight: bold; padding: 8px 24px;")
    self._update_btn_now = btn_update
    btn_layout = self._update_dialog.findChild(QHBoxLayout)
    btn_layout.insertWidget(0, btn_update)

    def do_update():
        btn_update.setEnabled(False)
        btn_update.setText("下载中...")
        self._update_btn_close.setEnabled(False)
        self._update_progress.setRange(0, 100)
        self._update_progress.setValue(0)
        self._update_status.setText("正在下载更新...")
        self._update_status.setStyleSheet("color: #0066CC;")
        self._update_info.setVisible(False)

        self._dl_worker = DownloadWorker(version_info)

        def on_progress(downloaded, total):
            if total > 0:
                percent = int(downloaded * 100 / total)
                self._update_progress.setValue(percent)
                mb_done = downloaded / 1024 / 1024
                mb_total = total / 1024 / 1024
                self._update_status.setText(f"正在下载更新... {mb_done:.1f}/{mb_total:.1f} MB ({percent}%)")
            else:
                mb_done = downloaded / 1024 / 1024
                self._update_status.setText(f"正在下载更新... {mb_done:.1f} MB")

        def on_finished(filepath, error):
            if error:
                self._update_progress.setRange(0, 1)
                self._update_progress.setValue(1)
                self._update_status.setText("下载失败")
                self._update_status.setStyleSheet("color: red;")
                self._update_info.setVisible(True)
                self._update_info.setText(error)
                btn_update.setText("下载失败")
                self._update_btn_close.setEnabled(True)
                return

            self._update_status.setText("正在验证文件...")
            self._update_progress.setRange(0, 0)

            checksum = version_info.get("checksum", "")
            if not verify_file(filepath, checksum):
                self._update_progress.setRange(0, 1)
                self._update_progress.setValue(1)
                self._update_status.setText("验证失败")
                self._update_status.setStyleSheet("color: red;")
                self._update_info.setVisible(True)
                self._update_info.setText("下载文件验证失败，请重新下载。")
                os.remove(filepath)
                btn_update.setText("验证失败")
                self._update_btn_close.setEnabled(True)
                return

            self._update_status.setText("正在准备安装...")
            update_local_version(version_info)

            ok, err = apply_update(filepath)
            if ok:
                self._update_status.setText("更新成功，程序即将重启...")
                self._update_status.setStyleSheet("color: green; font-weight: bold;")
                self._update_progress.setRange(0, 1)
                self._update_progress.setValue(1)
                btn_update.setVisible(False)
                self._update_btn_close.setText("立即重启")
                self._update_btn_close.setVisible(True)
                self._update_btn_close.setEnabled(True)
                self._update_btn_close.clicked.disconnect()
                self._update_btn_close.clicked.connect(QApplication.quit)
            else:
                self._update_progress.setRange(0, 1)
                self._update_progress.setValue(1)
                self._update_status.setText("下载完成")
                self._update_status.setStyleSheet("color: green;")
                self._update_info.setVisible(True)
                self._update_info.setText(f"更新文件已下载到：\n{filepath}\n\n请手动安装更新。")
                btn_update.setVisible(False)
                self._update_btn_close.setEnabled(True)

        self._dl_worker.progress.connect(on_progress)
        self._dl_worker.finished.connect(on_finished)
        self._dl_worker.start()

    btn_update.clicked.connect(do_update)
