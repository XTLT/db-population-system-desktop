from dialogs.subsidy_summary_dialog import SubsidySummaryDialog


def _open_subsidy_detail(self, id_card: str, name: str):
    """查看该人的全部补贴记录（6 个模块汇总在一屏）。"""
    dialog = SubsidySummaryDialog(self.is_network_mode, id_card, name, self)
    dialog.exec()
