from PyQt6.QtWidgets import QFileDialog, QMessageBox


def _generate_payment_template(self, func_name, default_filename):
    from data.excel_payment_templates import (
        generate_land_subsidy_template,
        generate_treatment_payment_template,
        generate_pension_insurance_template,
        generate_dibao_payment_template,
        generate_tekun_payment_template,
        generate_disability_care_payment_template,
        generate_elderly_allowance_template,
    )
    func_map = {
        'land_subsidy': generate_land_subsidy_template,
        'treatment_payment': generate_treatment_payment_template,
        'pension_insurance': generate_pension_insurance_template,
        'dibao_payment': generate_dibao_payment_template,
        'tekun_payment': generate_tekun_payment_template,
        'disability_care_payment': generate_disability_care_payment_template,
        'elderly_allowance': generate_elderly_allowance_template,
    }
    path, _ = QFileDialog.getSaveFileName(
        self, "保存模板", default_filename,
        "Excel文件 (*.xlsx)"
    )
    if path:
        func_map[func_name](path)
        QMessageBox.information(self, "成功", f"模板已生成：{path}")
