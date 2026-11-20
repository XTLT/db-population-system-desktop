"""桌面端入口。

- 智能 IPv4/IPv6 选路补丁：见 startup/net_patch.py（import 时即生效）
- 启动流程（更新检查、登录、主窗口）：见 startup/app_startup.py
- 主窗口方法：见 ui/main_window/，import 期绑定回本类
"""

import sys

# 智能 IPv4/IPv6 选路补丁必须在其它网络相关模块之前生效
from startup.net_patch import install_network_patch  # noqa: E402,F401

from PyQt6.QtWidgets import QMainWindow  # noqa: E402


class MainWindow(QMainWindow):
    """主窗口。方法拆分至 ui/main_window/，import 期绑定回本类。"""
    pass


from ui.main_window import (  # noqa: E402,F401
    __init__ as _mw_init,
    _setup_ui,
    _setup_menu,
    _setup_tray,
    _restore_from_tray,
    _on_tray_activated,
    _quit_app,
    closeEvent,
    _do_search,
    _display_name_list,
    _show_family,
    _open_subsidy_detail,
    _show_subsidy_dialog,
    _on_double_click,
    _import_excel,
    _recover_person,
    _export_excel,
    _report_import_excel,
    _report_online_edit,
    _report_export_excel,
    _show_report_logs,
    _view_change_log,
    _show_report_logs_dialog,
    _batch_import_ids,
    _fill_masked_id_cards,
    _manual_backup,
    _auto_backup,
    _do_backup,
    _refresh_status,
    _update_status_bar,
    _change_profile,
    _show_about,
    _check_for_updates,
    _auto_check_updates,
    _show_update_dialog,
    _on_version_check_done,
    _check_grade_promotion,
    _view_forest_info,
    _import_forest_data,
    _export_forest_data,
    _student_query,
    _import_student_education,
    _export_student_education,
    _generate_student_template,
    _generate_person_template,
    _generate_forest_template,
    _generate_payment_template,
    _generate_land_subsidy_template,
    _generate_pension_insurance_template,
    _generate_dibao_payment_template,
    _generate_tekun_payment_template,
    _grade_promotion,
    _import_land_subsidy,
    _view_land_subsidy,
    _import_pension_insurance,
    _view_pension_insurance,
    _add_household,
    _split_household,
    _merge_household,
    _import_dibao_payment,
    _view_dibao_payment,
    _import_tekun_payment,
    _view_tekun_payment,
    _import_disability_care_payment,
    _view_disability_care_payment,
    _import_elderly_allowance,
    _view_elderly_allowance,
    _generate_disability_care_payment_template,
    _generate_elderly_allowance_template,
)

MainWindow.__init__ = _mw_init
MainWindow._setup_ui = _setup_ui
MainWindow._setup_menu = _setup_menu
MainWindow._setup_tray = _setup_tray
MainWindow._restore_from_tray = _restore_from_tray
MainWindow._on_tray_activated = _on_tray_activated
MainWindow._quit_app = _quit_app
MainWindow.closeEvent = closeEvent
MainWindow._do_search = _do_search
MainWindow._display_name_list = _display_name_list
MainWindow._show_family = _show_family
MainWindow._open_subsidy_detail = _open_subsidy_detail
MainWindow._show_subsidy_dialog = _show_subsidy_dialog
MainWindow._on_double_click = _on_double_click
MainWindow._import_excel = _import_excel
MainWindow._recover_person = _recover_person
MainWindow._export_excel = _export_excel
MainWindow._report_import_excel = _report_import_excel
MainWindow._report_online_edit = _report_online_edit
MainWindow._report_export_excel = _report_export_excel
MainWindow._show_report_logs = _show_report_logs
MainWindow._view_change_log = _view_change_log
MainWindow._show_report_logs_dialog = _show_report_logs_dialog
MainWindow._batch_import_ids = _batch_import_ids
MainWindow._fill_masked_id_cards = _fill_masked_id_cards
MainWindow._manual_backup = _manual_backup
MainWindow._auto_backup = _auto_backup
MainWindow._do_backup = _do_backup
MainWindow._refresh_status = _refresh_status
MainWindow._update_status_bar = _update_status_bar
MainWindow._change_profile = _change_profile
MainWindow._show_about = _show_about
MainWindow._check_for_updates = _check_for_updates
MainWindow._auto_check_updates = _auto_check_updates
MainWindow._show_update_dialog = _show_update_dialog
MainWindow._on_version_check_done = _on_version_check_done
MainWindow._check_grade_promotion = _check_grade_promotion
MainWindow._view_forest_info = _view_forest_info
MainWindow._import_forest_data = _import_forest_data
MainWindow._export_forest_data = _export_forest_data
MainWindow._student_query = _student_query
MainWindow._import_student_education = _import_student_education
MainWindow._export_student_education = _export_student_education
MainWindow._generate_student_template = _generate_student_template
MainWindow._generate_person_template = _generate_person_template
MainWindow._generate_forest_template = _generate_forest_template
MainWindow._generate_payment_template = _generate_payment_template
MainWindow._generate_land_subsidy_template = _generate_land_subsidy_template
MainWindow._generate_pension_insurance_template = _generate_pension_insurance_template
MainWindow._generate_dibao_payment_template = _generate_dibao_payment_template
MainWindow._generate_tekun_payment_template = _generate_tekun_payment_template
MainWindow._grade_promotion = _grade_promotion
MainWindow._import_land_subsidy = _import_land_subsidy
MainWindow._view_land_subsidy = _view_land_subsidy
MainWindow._import_pension_insurance = _import_pension_insurance
MainWindow._view_pension_insurance = _view_pension_insurance
MainWindow._add_household = _add_household
MainWindow._split_household = _split_household
MainWindow._merge_household = _merge_household
MainWindow._import_dibao_payment = _import_dibao_payment
MainWindow._view_dibao_payment = _view_dibao_payment
MainWindow._import_tekun_payment = _import_tekun_payment
MainWindow._view_tekun_payment = _view_tekun_payment
MainWindow._import_disability_care_payment = _import_disability_care_payment
MainWindow._view_disability_care_payment = _view_disability_care_payment
MainWindow._import_elderly_allowance = _import_elderly_allowance
MainWindow._view_elderly_allowance = _view_elderly_allowance
MainWindow._generate_disability_care_payment_template = _generate_disability_care_payment_template
MainWindow._generate_elderly_allowance_template = _generate_elderly_allowance_template


if __name__ == "__main__":
    from startup.app_startup import main
    main()
