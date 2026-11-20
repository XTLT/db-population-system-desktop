from .._imports import *
from .._consts import *
from ..funcs import *



class LoginDialogLoginMixin:
    def _login(self):
        username = self.txt_username.text().strip()
        password = self.txt_password.text()
        if not username or not password:
            QMessageBox.warning(self, "提示", "请输入用户名和密码！")
            return
        
        from network.client import get_server_url
        server_url = get_server_url()
        
        if server_url:
            try:
                from network.client import api_login
                result = api_login(username, password)
                if result.get('success'):
                    self.user = result.get('user')
                    self.token = result.get('token')
                    self.accept()
                else:
                    QMessageBox.warning(self, "错误", result.get('error', '登录失败'))
            except Exception as e:
                QMessageBox.warning(self, "错误", f"登录失败：{str(e)}")
        else:
            try:
                user = authenticate_user(username, password)
                if user:
                    self.user = {
                        'id': user.id,
                        'username': user.username,
                        'real_name': user.real_name,
                        'role': user.role
                    }
                    self.token = "local"
                    self.accept()
                else:
                    from core.database import get_session, User as UserModel
                    sess = get_session()
                    try:
                        u = sess.query(UserModel).filter(UserModel.username == username).first()
                        if u and u.locked_until:
                            from datetime import datetime
                            try:
                                lock_time = datetime.strptime(u.locked_until, "%Y-%m-%d %H:%M:%S")
                                if datetime.now() < lock_time:
                                    remaining = int((lock_time - datetime.now()).total_seconds() / 60) + 1
                                    QMessageBox.warning(self, "账户已锁定", f"密码错误次数过多，账户已锁定。\n请 {remaining} 分钟后重试。")
                                else:
                                    QMessageBox.warning(self, "错误", "用户名或密码错误！")
                            except Exception:
                                QMessageBox.warning(self, "错误", "用户名或密码错误！")
                        else:
                            QMessageBox.warning(self, "错误", "用户名或密码错误！")
                    except Exception:
                        QMessageBox.warning(self, "错误", "用户名或密码错误！")
                    finally:
                        sess.close()
            except Exception as e:
                QMessageBox.warning(self, "错误", f"登录失败：{str(e)}")
