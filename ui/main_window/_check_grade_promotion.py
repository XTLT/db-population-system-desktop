from datetime import date
from PyQt6.QtWidgets import QMessageBox


def _check_grade_promotion(self):
    today = date.today()
    if today.month == 9 and today.day == 1:
        QMessageBox.question(
            self, "年级升级提醒",
            "今天是9月1日，是否执行年级升级操作？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
    elif today.month == 8 and today.day >= 25:
        QMessageBox.information(
            self, "年级升级提醒",
            f"距离9月1日年级升级还有 {31 - today.day} 天，请做好准备。"
        )
