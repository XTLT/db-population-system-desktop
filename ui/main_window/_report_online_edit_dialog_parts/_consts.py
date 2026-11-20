"""原模块的模块级常量。"""
from ._imports import *

"""本地在线编辑窗口：不依赖浏览器，用 desktop 内嵌 mTLS 客户端证书直连服务器。

替代原 webbrowser.open 方式（浏览器缺客户端证书会报 ERR_BAD_SSL_CLIENT_AUTH_CERT）。
数据流：
  GET  /api/reports/<id>/data[?sheet=<name>]   → {sheet_name, sheets, headers, rows}（Bearer token）
  POST /api/reports/<id>/save                  → {success}（Bearer token，JSON 带 sheet 字段）

编辑器能力（v0.0.40）：
  - 多工作表切换（工具栏下拉；切换前若有未保存修改会提示，保存时写回对应工作表）
  - 双击/按键编辑单元格
  - 批量插入行 / 删除行（多选）
  - 批量插入列 / 删除列（多选）
  - 撤销 / 重做（Ctrl+Z / Ctrl+Y，编辑与增删行列均可）
  - 查找 / 替换（当前表内）
  - 脏标记：有未保存修改时关闭会提示
"""

UNDO_LIMIT = 50

__all__ = ['UNDO_LIMIT']
