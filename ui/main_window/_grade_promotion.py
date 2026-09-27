


def _grade_promotion(self):
    from dialogs.student.grade_promotion_dialog import GradePromotionDialog
    dialog = GradePromotionDialog(self)
    if dialog.exec():
        pass
