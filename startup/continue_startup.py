"""登录与主窗口创建流程（更新检查结束后调用）。"""

import os
import sys


def continue_startup(app, window_ref):
    from PyQt6.QtWidgets import QMessageBox

    from main import MainWindow
    from dialogs.connect_dialog import ConnectDialog, get_recent_servers  # noqa: F401

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
        from core.database import Person

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
    window_ref[0] = window
    window.show()
