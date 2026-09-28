"""MainWindow 方法集合（由 main.py 拆分而来）。main.py 在 import 期绑定回 MainWindow。"""

from ._init_method import __init__
from ._setup_ui import _setup_ui
from ._setup_menu import _setup_menu
from ._setup_tray import _setup_tray
from ._restore_from_tray import _restore_from_tray
from ._on_tray_activated import _on_tray_activated
from ._quit_app import _quit_app
from .closeEvent import closeEvent
from ._do_search import _do_search
from ._display_name_list import _display_name_list
from ._show_family import _show_family
from ._open_subsidy_detail import _open_subsidy_detail
from ._show_subsidy_dialog import _show_subsidy_dialog
from ._on_double_click import _on_double_click
from ._import_excel import _import_excel
from ._recover_person import _recover_person
from ._export_excel import _export_excel
from ._report_import_excel import _report_import_excel
from ._report_online_edit import _report_online_edit
from ._report_export_excel import _report_export_excel
from ._show_report_logs import _show_report_logs
from ._view_change_log import _view_change_log
from ._show_report_logs_dialog import _show_report_logs_dialog
from ._batch_import_ids import _batch_import_ids
from ._manual_backup import _manual_backup
from ._auto_backup import _auto_backup
from ._do_backup import _do_backup
from ._refresh_status import _refresh_status
from ._update_status_bar import _update_status_bar
from ._change_profile import _change_profile
from ._show_about import _show_about
from ._check_for_updates import _check_for_updates
from ._show_update_dialog import _show_update_dialog
from ._on_version_check_done import _on_version_check_done
from ._check_grade_promotion import _check_grade_promotion
from ._view_forest_info import _view_forest_info
from ._import_forest_data import _import_forest_data
from ._export_forest_data import _export_forest_data
from ._student_query import _student_query
from ._import_student_education import _import_student_education
from ._export_student_education import _export_student_education
from ._generate_student_template import _generate_student_template
from ._generate_forest_template import _generate_forest_template
from ._generate_payment_template import _generate_payment_template
from ._generate_land_subsidy_template import _generate_land_subsidy_template
from ._generate_treatment_payment_template import _generate_treatment_payment_template
from ._generate_pension_insurance_template import _generate_pension_insurance_template
from ._generate_dibao_payment_template import _generate_dibao_payment_template
from ._generate_tekun_payment_template import _generate_tekun_payment_template
from ._grade_promotion import _grade_promotion
from ._import_land_subsidy import _import_land_subsidy
from ._view_land_subsidy import _view_land_subsidy
from ._import_treatment_payment import _import_treatment_payment
from ._view_treatment_payment import _view_treatment_payment
from ._import_pension_insurance import _import_pension_insurance
from ._view_pension_insurance import _view_pension_insurance
from ._add_household import _add_household
from ._split_household import _split_household
from ._merge_household import _merge_household
from ._import_dibao_payment import _import_dibao_payment
from ._view_dibao_payment import _view_dibao_payment
from ._import_tekun_payment import _import_tekun_payment
from ._view_tekun_payment import _view_tekun_payment
from ._import_disability_care_payment import _import_disability_care_payment
from ._view_disability_care_payment import _view_disability_care_payment
from ._import_elderly_allowance import _import_elderly_allowance
from ._view_elderly_allowance import _view_elderly_allowance
from ._generate_disability_care_payment_template import _generate_disability_care_payment_template
from ._generate_elderly_allowance_template import _generate_elderly_allowance_template

__all__ = [
    '__init__',
    '_setup_ui',
    '_setup_menu',
    '_setup_tray',
    '_restore_from_tray',
    '_on_tray_activated',
    '_quit_app',
    'closeEvent',
    '_do_search',
    '_display_name_list',
    '_show_family',
    '_open_subsidy_detail',
    '_show_subsidy_dialog',
    '_on_double_click',
    '_import_excel',
    '_recover_person',
    '_export_excel',
    '_report_import_excel',
    '_report_online_edit',
    '_report_export_excel',
    '_show_report_logs',
    '_view_change_log',
    '_show_report_logs_dialog',
    '_batch_import_ids',
    '_manual_backup',
    '_auto_backup',
    '_do_backup',
    '_refresh_status',
    '_update_status_bar',
    '_change_profile',
    '_show_about',
    '_check_for_updates',
    '_show_update_dialog',
    '_on_version_check_done',
    '_check_grade_promotion',
    '_view_forest_info',
    '_import_forest_data',
    '_export_forest_data',
    '_student_query',
    '_import_student_education',
    '_export_student_education',
    '_generate_student_template',
    '_generate_forest_template',
    '_generate_payment_template',
    '_generate_land_subsidy_template',
    '_generate_treatment_payment_template',
    '_generate_pension_insurance_template',
    '_generate_dibao_payment_template',
    '_generate_tekun_payment_template',
    '_grade_promotion',
    '_import_land_subsidy',
    '_view_land_subsidy',
    '_import_treatment_payment',
    '_view_treatment_payment',
    '_import_pension_insurance',
    '_view_pension_insurance',
    '_add_household',
    '_split_household',
    '_merge_household',
    '_import_dibao_payment',
    '_view_dibao_payment',
    '_import_tekun_payment',
    '_view_tekun_payment',
    '_import_disability_care_payment',
    '_view_disability_care_payment',
    '_import_elderly_allowance',
    '_view_elderly_allowance',
    '_generate_disability_care_payment_template',
    '_generate_elderly_allowance_template',
]
