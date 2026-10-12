import sys
import os
import signal

from PyQt6.QtWidgets import QApplication, QMainWindow, QMessageBox
from PyQt6.QtCore import QTimer
from PyQt6.QtGui import QFont

from core.config import FONT_NAME, FONT_SIZE, ensure_dirs
from core.database import Person

from ui.main_window.workers import DownloadWorker, VersionCheckWorker


class MainWindow(QMainWindow):
    """主窗口。方法拆分至 ui/main_window/，import 期绑定回本类。"""
    pass


from ui.main_window import (  # noqa: E402,F401
    __init__ as _mw_init,
    _setup_ui,
    _setup_menu,
    _setup_tray,
    _restore_from_tray,
    _on_tray_activated,
    _quit_app,
    closeEvent,
    _do_search,
    _display_name_list,
    _show_family,
    _open_subsidy_detail,
    _show_subsidy_dialog,
    _on_double_click,
    _import_excel,
    _recover_person,
    _export_excel,
    _report_import_excel,
    _report_online_edit,
    _report_export_excel,
    _show_report_logs,
    _view_change_log,
    _show_report_logs_dialog,
    _batch_import_ids,
    _manual_backup,
    _auto_backup,
    _do_backup,
    _refresh_status,
    _update_status_bar,
    _change_profile,
    _show_about,
    _check_for_updates,
    _auto_check_updates,
    _show_update_dialog,
    _on_version_check_done,
    _check_grade_promotion,
    _view_forest_info,
    _import_forest_data,
    _export_forest_data,
    _student_query,
    _import_student_education,
    _export_student_education,
    _generate_student_template,
    _generate_forest_template,
    _generate_payment_template,
    _generate_land_subsidy_template,
    _generate_pension_insurance_template,
    _generate_dibao_payment_template,
    _generate_tekun_payment_template,
    _grade_promotion,
    _import_land_subsidy,
    _view_land_subsidy,
    _import_pension_insurance,
    _view_pension_insurance,
    _add_household,
    _split_household,
    _merge_household,
    _import_dibao_payment,
    _view_dibao_payment,
    _import_tekun_payment,
    _view_tekun_payment,
    _import_disability_care_payment,
    _view_disability_care_payment,
    _import_elderly_allowance,
    _view_elderly_allowance,
    _generate_disability_care_payment_template,
    _generate_elderly_allowance_template,
)

MainWindow.__init__ = _mw_init
MainWindow._setup_ui = _setup_ui
MainWindow._setup_menu = _setup_menu
MainWindow._setup_tray = _setup_tray
MainWindow._restore_from_tray = _restore_from_tray
MainWindow._on_tray_activated = _on_tray_activated
MainWindow._quit_app = _quit_app
MainWindow.closeEvent = closeEvent
MainWindow._do_search = _do_search
MainWindow._display_name_list = _display_name_list
MainWindow._show_family = _show_family
MainWindow._open_subsidy_detail = _open_subsidy_detail
MainWindow._show_subsidy_dialog = _show_subsidy_dialog
MainWindow._on_double_click = _on_double_click
MainWindow._import_excel = _import_excel
MainWindow._recover_person = _recover_person
MainWindow._export_excel = _export_excel
MainWindow._report_import_excel = _report_import_excel
MainWindow._report_online_edit = _report_online_edit
MainWindow._report_export_excel = _report_export_excel
MainWindow._show_report_logs = _show_report_logs
MainWindow._view_change_log = _view_change_log
MainWindow._show_report_logs_dialog = _show_report_logs_dialog
MainWindow._batch_import_ids = _batch_import_ids
MainWindow._manual_backup = _manual_backup
MainWindow._auto_backup = _auto_backup
MainWindow._do_backup = _do_backup
MainWindow._refresh_status = _refresh_status
MainWindow._update_status_bar = _update_status_bar
MainWindow._change_profile = _change_profile
MainWindow._show_about = _show_about
MainWindow._check_for_updates = _check_for_updates
MainWindow._auto_check_updates = _auto_check_updates
MainWindow._show_update_dialog = _show_update_dialog
MainWindow._on_version_check_done = _on_version_check_done
MainWindow._check_grade_promotion = _check_grade_promotion
MainWindow._view_forest_info = _view_forest_info
MainWindow._import_forest_data = _import_forest_data
MainWindow._export_forest_data = _export_forest_data
MainWindow._student_query = _student_query
MainWindow._import_student_education = _import_student_education
MainWindow._export_student_education = _export_student_education
MainWindow._generate_student_template = _generate_student_template
MainWindow._generate_forest_template = _generate_forest_template
MainWindow._generate_payment_template = _generate_payment_template
MainWindow._generate_land_subsidy_template = _generate_land_subsidy_template
MainWindow._generate_pension_insurance_template = _generate_pension_insurance_template
MainWindow._generate_dibao_payment_template = _generate_dibao_payment_template
MainWindow._generate_tekun_payment_template = _generate_tekun_payment_template
MainWindow._grade_promotion = _grade_promotion
MainWindow._import_land_subsidy = _import_land_subsidy
MainWindow._view_land_subsidy = _view_land_subsidy
MainWindow._import_pension_insurance = _import_pension_insurance
MainWindow._view_pension_insurance = _view_pension_insurance
MainWindow._add_household = _add_household
MainWindow._split_household = _split_household
MainWindow._merge_household = _merge_household
MainWindow._import_dibao_payment = _import_dibao_payment
MainWindow._view_dibao_payment = _view_dibao_payment
MainWindow._import_tekun_payment = _import_tekun_payment
MainWindow._view_tekun_payment = _view_tekun_payment
MainWindow._import_disability_care_payment = _import_disability_care_payment
MainWindow._view_disability_care_payment = _view_disability_care_payment
MainWindow._import_elderly_allowance = _import_elderly_allowance
MainWindow._view_elderly_allowance = _view_elderly_allowance
MainWindow._generate_disability_care_payment_template = _generate_disability_care_payment_template
MainWindow._generate_elderly_allowance_template = _generate_elderly_allowance_template


def main():
    ensure_dirs()
    from core.database import init_db
    init_db()
    app = QApplication(sys.argv)
    app.setFont(QFont(FONT_NAME, FONT_SIZE))
    app.setQuitOnLastWindowClosed(False)

    # Ctrl+C (SIGINT) 退出：事件循环运行期间收到中断信号时干净退出
    signal.signal(signal.SIGINT, lambda *a: QApplication.quit())
    # Qt C 事件循环期间外部 SIGINT 不会主动回到 Python 解释器，
    # 用低频定时器周期性回到 Python，使上面的 SIGINT 回调得以执行
    _sigint_wakeup = QTimer()
    _sigint_wakeup.start(200)
    _sigint_wakeup.timeout.connect(lambda: None)

    from dialogs.connect_dialog import ConnectDialog, get_recent_servers
    # 命令行已传入服务器地址（start_desktop.sh start network <url>）时，
    # 直接使用，不再弹出连接对话框
    server_url = (os.environ.get("POPULATION_SERVER_URL") or "").strip()
    if not server_url:
        connect_dialog = ConnectDialog()
        if not connect_dialog.exec():
            sys.exit(0)
        server_url = connect_dialog.get_server_url()

    current_user = {}

    if server_url:
        from network.client import set_server_url, test_connection, set_token
        set_server_url(server_url)
        if not test_connection():
            QMessageBox.critical(None, "连接失败", f"无法连接到服务器：\n{server_url}\n\n请检查服务器是否启动，或检查网络连接。")
            sys.exit(1)
        from dialogs.user_dialog import LoginDialog
        login_dialog = LoginDialog()
        if login_dialog.exec():
            token = login_dialog.get_token()
            if token:
                set_token(token)
            current_user = login_dialog.get_user() or {}
        else:
            sys.exit(1)
    else:
        from core.database import get_session, set_db_password, reset_engine, is_database_encrypted, decrypt_database, encrypt_database, init_db, get_all_users
        from core.config import DB_PATH

        password = None
        from dialogs.password_dialog import PasswordDialog
        from dialogs.user_dialog import LoginDialog

        if is_database_encrypted():
            dialog = PasswordDialog(is_new=False)
            if dialog.exec():
                password = dialog.get_password()
                if not decrypt_database(password):
                    reply = QMessageBox.question(
                        None, "解密失败",
                        "密码错误或数据库损坏！\n\n"
                        "⚠️ 重要提示：\n"
                        "如果忘记密码，数据将永久丢失，无法恢复！\n\n"
                        "是否删除加密文件重新开始？\n"
                        "（将丢失所有原有数据）",
                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                    )
                    if reply == QMessageBox.StandardButton.Yes:
                        os.remove(DB_PATH + '.enc')
                        if os.path.exists(DB_PATH + '.key'):
                            os.remove(DB_PATH + '.key')
                        password = None
                    else:
                        sys.exit(0)
                else:
                    reset_engine()
            else:
                sys.exit(0)
        
        if not password:
            dialog = PasswordDialog(is_new=True)
            if dialog.exec():
                password = dialog.get_password()
            else:
                sys.exit(0)
        
        if password:
            set_db_password(password)
        
        def cleanup():
            if password:
                try:
                    reset_engine()
                    encrypt_database(password)
                except Exception:
                    pass
        
        app.aboutToQuit.connect(cleanup)
        
        users = get_all_users()
        if not users:
            QMessageBox.warning(None, "系统未初始化", "系统未初始化！\n\n请先在Web服务端创建用户账户后再登录。\n\n启动Web服务端命令：python3 web_app.py")
            sys.exit(0)
        
        login_dialog = LoginDialog()
        if login_dialog.exec():
            current_user = login_dialog.get_user()
        else:
            sys.exit(0)

        session = get_session()
        try:
            session.query(Person).count()
        except Exception:
            if password:
                QMessageBox.critical(None, "错误", "数据库访问失败！")
                sys.exit(1)
            raise
        finally:
            session.close()

    window = MainWindow(current_user)
    window.show()

    # 启动自动检查更新：此时服务器地址已设置、网络已连通，
    # 有更新才弹窗提示（无更新/失败静默），延迟 3 秒避免打扰启动
    QTimer.singleShot(3000, window._auto_check_updates)

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
