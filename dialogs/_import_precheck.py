"""导入预检的确认对话框（6 个补贴导入界面共用）。"""
from PyQt6.QtWidgets import QMessageBox


def format_precheck_message(result: dict) -> str:
    total = result.get("total", 0)
    imported = result.get("imported", 0)
    updated = result.get("updated", 0)
    skipped = result.get("skipped", 0)
    errors = result.get("errors", []) or []
    not_found = sorted(set(result.get("not_found", []) or []))

    msg = "预检完成，尚未写入数据库。\n\n"
    msg += f"文件总行数：{total}\n"
    msg += f"将新增：{imported} 条\n"
    if updated:
        msg += f"将更新：{updated} 条\n"
    msg += f"将跳过：{skipped} 条\n"

    if not_found:
        msg += f"\n人员库中不存在（{len(not_found)} 人）：\n"
        msg += "\n".join(not_found[:10])
        if len(not_found) > 10:
            msg += f"\n…等 {len(not_found)} 人"

    if errors:
        msg += f"\n\n跳过原因（共 {len(errors)} 条，显示前 5 条）：\n"
        msg += "\n".join(errors[:5])
        if len(errors) > 5:
            msg += "\n…"

    msg += "\n\n确认按以上结果写入数据库吗？"
    return msg


def confirm_precheck(parent, result: dict) -> bool:
    """返回 True 表示用户确认继续真正导入。"""
    box = QMessageBox(parent)
    box.setWindowTitle("导入预检")
    box.setIcon(QMessageBox.Icon.Question)
    box.setText(format_precheck_message(result))
    yes_btn = box.addButton("确认导入", QMessageBox.ButtonRole.AcceptRole)
    box.addButton("取消", QMessageBox.ButtonRole.RejectRole)
    box.setDefaultButton(yes_btn)
    box.exec()
    return box.clickedButton() is yes_btn
