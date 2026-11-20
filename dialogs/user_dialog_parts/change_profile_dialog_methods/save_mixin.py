from .._imports import *
from .._consts import *
from ..funcs import *



class ChangeProfileDialogSaveMixin:
    def _save(self):
        new_username = self.txt_new_username.text().strip()
        real_name = self.txt_real_name.text().strip()
        old_pw = self.txt_old_pw.text()
        new_pw = self.txt_new_pw.text()
        confirm_pw = self.txt_confirm_pw.text()

        if not new_username:
            QMessageBox.warning(self, "提示", "用户名不能为空！")
            return

        from network.client import get_server_url
        server_url = get_server_url()

        if server_url:
            try:
                from network.client import _request
                data = {}
                if new_username != self.user_info.get('username', ''):
                    data['username'] = new_username
                if real_name != self.user_info.get('real_name', ''):
                    data['real_name'] = real_name
                if new_pw:
                    if not old_pw:
                        QMessageBox.warning(self, "提示", "请输入当前密码！")
                        return
                    if new_pw != confirm_pw:
                        QMessageBox.warning(self, "提示", "两次输入的密码不一致！")
                        return
                    data['old_password'] = old_pw
                    data['password'] = new_pw
                if data:
                    result = _request('PUT', f'/api/users/{self.user_info["id"]}', data)
                    if result.get('success'):
                        if new_pw:
                            QMessageBox.information(self, "成功", "密码已修改，程序即将重新启动。")
                            import sys
                            import os
                            os.execl(sys.executable, sys.executable, *sys.argv)
                        else:
                            QMessageBox.information(self, "成功", "账户信息已更新！")
                            self.accept()
                    else:
                        QMessageBox.warning(self, "错误", result.get('error', '修改失败'))
            except Exception as e:
                QMessageBox.warning(self, "错误", f"修改失败：{str(e)}")
        else:
            try:
                if new_username != self.user_info.get('username', ''):
                    from core.database import get_session, User as UserModel
                    sess = get_session()
                    try:
                        existing = sess.query(UserModel).filter(UserModel.username == new_username).first()
                        if existing:
                            QMessageBox.warning(self, "错误", "用户名已存在！")
                            return
                    finally:
                        sess.close()

                if new_pw:
                    if not old_pw:
                        QMessageBox.warning(self, "提示", "请输入当前密码！")
                        return
                    if new_pw != confirm_pw:
                        QMessageBox.warning(self, "提示", "两次输入的密码不一致！")
                        return
                    from core.database import change_user_password
                    ok, msg = change_user_password(self.user_info['id'], old_pw, new_pw)
                    if not ok:
                        QMessageBox.warning(self, "错误", msg)
                        return

                from core.database import update_user
                updates = {}
                if new_username != self.user_info.get('username', ''):
                    updates['username'] = new_username
                if real_name != self.user_info.get('real_name', ''):
                    updates['real_name'] = real_name
                if updates:
                    update_user(self.user_info['id'], **updates)

                if new_pw:
                    QMessageBox.information(self, "成功", "密码已修改，程序即将重新启动。")
                    from core.database import reset_engine, encrypt_database, get_db_password
                    db_pw = get_db_password()
                    if db_pw:
                        reset_engine()
                        encrypt_database(db_pw)
                    import sys
                    import os
                    os.execl(sys.executable, sys.executable, *sys.argv)
                else:
                    QMessageBox.information(self, "成功", "账户信息已更新！")
                    self.accept()
            except Exception as e:
                QMessageBox.warning(self, "错误", f"修改失败：{str(e)}")
