from datetime import datetime
from PyQt6.QtWidgets import QLineEdit, QMessageBox, QFileDialog, QInputDialog


def _export_excel(self):
    from dialogs.export_dialog import ExportFilterDialog

    if self.is_network_mode:
        dialog = ExportFilterDialog(self)

        def update_preview_network():
            try:
                filters = dialog.get_filters()
                from network.client import api_search
                all_data = []
                name = filters.get("name", "")
                if name:
                    results = api_search(name)
                    all_data = results
                else:
                    from network.client import _request
                    stats = _request('GET', '/api/stats')
                    total = stats.get('total_persons', 0)
                    if total > 0:
                        all_data = [{}] * total

                count = len(all_data) if all_data else 0
                dialog.update_count(count)
            except Exception as e:
                dialog.lbl_count.setText(f"查询出错：{e}")

        dialog.txt_name.textChanged.connect(lambda: update_preview_network())
        dialog.txt_address.textChanged.connect(lambda: update_preview_network())
        dialog.cmb_is_dead.currentTextChanged.connect(lambda: update_preview_network())
        dialog.cmb_relation.selectionChanged.connect(lambda: update_preview_network())
        dialog.cmb_disability.selectionChanged.connect(lambda: update_preview_network())
        dialog.cmb_dis_level.selectionChanged.connect(lambda: update_preview_network())
        dialog.cmb_poor_type.selectionChanged.connect(lambda: update_preview_network())
        dialog.cmb_dibao.currentTextChanged.connect(lambda: update_preview_network())
        dialog.cmb_jisheng.currentTextChanged.connect(lambda: update_preview_network())

        update_preview_network()

        if not dialog.exec():
            return

        filters = dialog.get_filters()
        path, _ = QFileDialog.getSaveFileName(
            self, "导出Excel", f"人口信息_{datetime.now().strftime('%Y%m%d')}.xlsx",
            "Excel文件 (*.xlsx)"
        )
        if path:
            try:
                from network.client import api_export_filtered
                try:
                    api_export_filtered(path, filters)
                except ConnectionError as e:
                    if '验证密码' in str(e):
                        password, ok = QInputDialog.getText(
                            self, "密码验证", "导出敏感数据需要验证密码：",
                            QLineEdit.EchoMode.Password
                        )
                        if ok and password:
                            api_export_filtered(path, filters, password)
                        else:
                            return
                    else:
                        raise
                QMessageBox.information(self, "成功", f"数据已导出到：\n{path}")
            except Exception as e:
                QMessageBox.critical(self, "导出失败", str(e))
        return

    from data.excel_importer import query_persons_with_filters

    dialog = ExportFilterDialog(self)

    def update_preview():
        try:
            filters = dialog.get_filters()
            persons = query_persons_with_filters(filters)
            count = len(persons) if persons else 0
            dialog.update_count(count)
        except Exception as e:
            dialog.lbl_count.setText(f"查询出错：{e}")

    dialog.txt_name.textChanged.connect(update_preview)
    dialog.txt_address.textChanged.connect(update_preview)
    dialog.txt_age_min.textChanged.connect(update_preview)
    dialog.txt_age_max.textChanged.connect(update_preview)
    dialog.cmb_is_dead.currentTextChanged.connect(lambda: update_preview())
    dialog.cmb_relation.selectionChanged.connect(lambda: update_preview())
    dialog.cmb_disability.selectionChanged.connect(lambda: update_preview())
    dialog.cmb_dis_level.selectionChanged.connect(lambda: update_preview())
    dialog.cmb_poor_type.selectionChanged.connect(lambda: update_preview())
    dialog.cmb_dibao.currentTextChanged.connect(lambda: update_preview())
    dialog.cmb_jisheng.currentTextChanged.connect(lambda: update_preview())

    update_preview()

    if not dialog.exec():
        return

    filters = dialog.get_filters()
    has_filter = any([
        filters.get("name"), filters.get("address"),
        filters.get("age_min"), filters.get("age_max"),
        filters["is_dead"] != "全部", filters["relation"],
        filters["disability"], filters["dis_level"],
        filters["poor_type"], filters["dibao"] != "全部",
        filters["jisheng"] != "全部", filters["land_area"] != "全部",
        filters["local_welfare_forest_area"] != "全部",
        filters["national_welfare_forest_area"] != "全部",
        filters["commercial_forest_area"] != "全部",
    ])

    path, _ = QFileDialog.getSaveFileName(
        self, "导出Excel", f"人口信息_{datetime.now().strftime('%Y%m%d')}.xlsx",
        "Excel文件 (*.xlsx)"
    )
    if path:
        from data.excel_importer import export_excel
        filter_params = filters if has_filter else None
        if export_excel(path, filters=filter_params):
            count_text = "筛选后" if has_filter else "全部"
            QMessageBox.information(self, "成功", f"{count_text}数据已导出到：\n{path}")
        else:
            QMessageBox.warning(self, "提示", "没有符合条件的数据可导出")
