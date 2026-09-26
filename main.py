import sys
import os
import shutil
from datetime import datetime, date

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QFormLayout, QLineEdit, QPushButton, QLabel, QTableWidget, QTableWidgetItem,
    QMenu, QMessageBox, QHeaderView, QAbstractItemView, QSplitter, QScrollArea,
    QSystemTrayIcon, QDialog, QFileDialog, QInputDialog, QCheckBox, QTextEdit, QProgressBar
)
from PyQt6.QtCore import Qt, QTimer, QThread, pyqtSignal
from PyQt6.QtGui import QFont, QColor, QAction, QIcon, QPixmap, QPainter

from core.config import (
    APP_NAME, FONT_NAME, FONT_SIZE, MATCHES_PER_COLUMN,
    BTN_SAVE_COLOR, BTN_ADD_COLOR, BTN_CANCEL_COLOR, PHOTOS_DIR, ensure_dirs, GRADE_DISPLAY
)
from core.database import search_by_name, get_family_members, get_person_count, get_student_education, Person
from core.utils import has_any_photo
from dialogs.person.edit_dialog import EditDialog
from dialogs.import_export.import_dialog import ImportDialog
from dialogs.land_subsidy.import_dialog import LandSubsidyImportDialog
from dialogs.land_subsidy.view_dialog import LandSubsidyViewDialog
from dialogs.treatment_payment.import_dialog import TreatmentPaymentImportDialog
from dialogs.treatment_payment.view_dialog import TreatmentPaymentViewDialog
from dialogs.pension_insurance.import_dialog import PensionInsuranceImportDialog
from dialogs.pension_insurance.view_dialog import PensionInsuranceViewDialog
from data.excel_importer import backup_database
from network.client import get_server_url
from network.update_checker import download_update, verify_file, update_local_version, apply_update


class DownloadWorker(QThread):
    progress = pyqtSignal(int, int)
    finished = pyqtSignal(str, str)

    def __init__(self, version_info):
        super().__init__()
        self.version_info = version_info

    def run(self):
        def on_progress(downloaded, total):
            self.progress.emit(downloaded, total)

        filepath, error = download_update(self.version_info, progress_callback=on_progress)
        self.finished.emit(filepath or "", error)


class VersionCheckWorker(QThread):
    finished = pyqtSignal(object, str)

    def run(self):
        try:
            from network.update_checker import check_update
            result, error = check_update("desktop")
            self.finished.emit(result, error)
        except Exception as e:
            self.finished.emit(None, str(e))


class MainWindow(QMainWindow):
    def __init__(self, current_user=None):
        super().__init__()
        self.current_user = current_user or {}
        self.is_network_mode = bool(get_server_url())
        mode_text = "【网络模式】" if self.is_network_mode else "【本地模式】"
        self.setWindowTitle(f"{APP_NAME} {mode_text}")
        icon_dir = os.path.dirname(os.path.abspath(__file__))
        if getattr(sys, 'frozen', False):
            icon_dir = os.path.dirname(sys.executable)
        window_icon = os.path.join(icon_dir, "window_icon.png")
        if os.path.exists(window_icon):
            self.setWindowIcon(QIcon(window_icon))
        else:
            ico = os.path.join(icon_dir, "app.ico")
            if os.path.exists(ico):
                self.setWindowIcon(QIcon(ico))
        screen = QApplication.primaryScreen().geometry()
        w = min(1400, int(screen.width() * 0.85))
        h = min(900, int(screen.height() * 0.85))
        self.resize(w, h)
        self.matches = []
        self.current_name = None
        self.current_family = []
        self.current_hu_hao = None
        self._update_dialog = None
        self._setup_ui()
        self._setup_menu()
        self._setup_tray()
        if not self.is_network_mode:
            self._auto_backup()
            self._check_grade_promotion()

    def _setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        search_layout = QHBoxLayout()
        lbl_search = QLabel("输入姓名查询：")
        lbl_search.setFont(QFont(FONT_NAME, FONT_SIZE))
        self.txt_search = QLineEdit()
        self.txt_search.setFont(QFont(FONT_NAME, FONT_SIZE))
        self.txt_search.setPlaceholderText("请输入姓名进行模糊查询...")
        self.txt_search.returnPressed.connect(self._do_search)
        btn_search = QPushButton("查询")
        btn_search.setFont(QFont(FONT_NAME, FONT_SIZE))
        btn_search.clicked.connect(self._do_search)
        search_layout.addWidget(lbl_search)
        search_layout.addWidget(self.txt_search)
        search_layout.addWidget(btn_search)
        layout.addLayout(search_layout)

        self.splitter = QSplitter(Qt.Orientation.Vertical)
        self.name_container = QWidget()
        self.name_layout = QVBoxLayout(self.name_container)
        self.name_label = QLabel("")
        self.name_label.setFont(QFont(FONT_NAME, 12))
        self.name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.name_label.setStyleSheet("background-color: #DDEBF7; font-weight: bold; padding: 8px; border: 1px solid #4472C4;")
        self.name_layout.addWidget(self.name_label)

        self.table = QTableWidget()
        self.table.setFont(QFont(FONT_NAME, FONT_SIZE))
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectItems)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.table.doubleClicked.connect(self._on_double_click)
        self.table.verticalHeader().setVisible(False)

        self.splitter.addWidget(self.name_container)
        self.splitter.addWidget(self.table)
        self.splitter.setSizes([400, 300])
        layout.addWidget(self.splitter)

        status_layout = QHBoxLayout()
        from core.config import APP_VERSION
        self.lbl_version = QLabel(f"版本：v{APP_VERSION}")
        self.lbl_version.setFont(QFont(FONT_NAME, 9))
        self.lbl_version.setStyleSheet("color: #666;")
        status_layout.addWidget(self.lbl_version)

        self.lbl_status = QLabel(f"数据库记录数：{get_person_count()}")
        self.lbl_status.setFont(QFont(FONT_NAME, 9))
        status_layout.addWidget(self.lbl_status)
        
        self.lbl_backup = QLabel("")
        self.lbl_backup.setFont(QFont(FONT_NAME, 9))
        status_layout.addWidget(self.lbl_backup)
        
        self.lbl_disk = QLabel("")
        self.lbl_disk.setFont(QFont(FONT_NAME, 9))
        status_layout.addWidget(self.lbl_disk)
        
        layout.addLayout(status_layout)
        
        self._update_status_bar()

    def _setup_menu(self):
        menubar = self.menuBar()
        file_menu = menubar.addMenu("文件")
        import_action = QAction("导入Excel", self)
        import_action.triggered.connect(self._import_excel)
        export_action = QAction("导出Excel", self)
        export_action.triggered.connect(self._export_excel)
        backup_action = QAction("手动备份", self)
        backup_action.triggered.connect(self._manual_backup)
        exit_action = QAction("退出", self)
        exit_action.triggered.connect(self.close)

        is_admin = self.current_user.get('role') == 'admin'
        import_action.setEnabled(is_admin)

        file_menu.addAction(import_action)
        file_menu.addAction(export_action)
        file_menu.addAction(backup_action)
        file_menu.addSeparator()
        file_menu.addAction(exit_action)

        report_menu = menubar.addMenu("报表填写")
        report_import_action = QAction("导入Excel", self)
        report_import_action.triggered.connect(self._report_import_excel)
        report_online_action = QAction("在线编辑", self)
        report_online_action.triggered.connect(self._report_online_edit)
        report_export_action = QAction("导出Excel", self)
        report_export_action.triggered.connect(self._report_export_excel)
        report_log_action = QAction("查看修改日志", self)
        report_log_action.triggered.connect(self._view_change_log)
        report_batch_action = QAction("一键导入证件号码", self)
        report_batch_action.triggered.connect(self._batch_import_ids)
        report_menu.addAction(report_import_action)
        report_menu.addAction(report_online_action)
        report_menu.addAction(report_export_action)
        report_menu.addAction(report_log_action)
        report_menu.addAction(report_batch_action)

        hh_menu = menubar.addMenu("户籍管理")
        add_hh_action = QAction("新增户", self)
        add_hh_action.triggered.connect(self._add_household)
        split_hh_action = QAction("分户", self)
        split_hh_action.triggered.connect(self._split_household)
        merge_hh_action = QAction("合户", self)
        merge_hh_action.triggered.connect(self._merge_household)
        hh_menu.addAction(add_hh_action)
        hh_menu.addAction(split_hh_action)
        hh_menu.addAction(merge_hh_action)
        hh_menu.addSeparator()
        recover_action = QAction("找回已删除人员", self)
        recover_action.triggered.connect(self._recover_person)
        hh_menu.addAction(recover_action)

        forest_menu = menubar.addMenu("林地管理")
        forest_view_action = QAction("查看林地信息", self)
        forest_view_action.triggered.connect(self._view_forest_info)
        forest_export_action = QAction("导出林地数据", self)
        forest_export_action.triggered.connect(self._export_forest_data)
        forest_menu.addAction(forest_view_action)
        forest_menu.addAction(forest_export_action)

        student_menu = menubar.addMenu("学生管理")
        student_query_action = QAction("学生信息查询", self)
        student_query_action.triggered.connect(self._student_query)
        student_import_action = QAction("导入就读信息", self)
        student_import_action.triggered.connect(self._import_student_education)
        student_export_action = QAction("导出就读信息", self)
        student_export_action.triggered.connect(self._export_student_education)
        grade_promotion_action = QAction("年级升级", self)
        grade_promotion_action.triggered.connect(self._grade_promotion)

        student_import_action.setEnabled(is_admin)

        student_menu.addAction(student_query_action)
        student_menu.addAction(student_import_action)
        student_menu.addAction(student_export_action)
        student_menu.addSeparator()
        student_menu.addAction(grade_promotion_action)

        subsidy_menu = menubar.addMenu("地力补贴")
        subsidy_import_action = QAction("导入地力补贴", self)
        subsidy_import_action.triggered.connect(self._import_land_subsidy)
        subsidy_view_action = QAction("查看地力补贴", self)
        subsidy_view_action.triggered.connect(self._view_land_subsidy)
        subsidy_import_action.setEnabled(is_admin)
        subsidy_menu.addAction(subsidy_import_action)
        subsidy_menu.addAction(subsidy_view_action)

        treatment_menu = menubar.addMenu("待遇发放")
        treatment_import_action = QAction("导入待遇发放", self)
        treatment_import_action.triggered.connect(self._import_treatment_payment)
        treatment_view_action = QAction("查看待遇发放", self)
        treatment_view_action.triggered.connect(self._view_treatment_payment)
        treatment_import_action.setEnabled(is_admin)
        treatment_menu.addAction(treatment_import_action)
        treatment_menu.addAction(treatment_view_action)

        pension_menu = menubar.addMenu("养老保险")
        pension_import_action = QAction("导入养老保险", self)
        pension_import_action.triggered.connect(self._import_pension_insurance)
        pension_view_action = QAction("查看养老保险", self)
        pension_view_action.triggered.connect(self._view_pension_insurance)
        pension_import_action.setEnabled(is_admin)
        pension_menu.addAction(pension_import_action)
        pension_menu.addAction(pension_view_action)

        template_menu = menubar.addMenu("下载模板")
        tpl_student = QAction("就读信息模板", self)
        tpl_student.triggered.connect(self._generate_student_template)
        tpl_forest = QAction("林地面积模板", self)
        tpl_forest.triggered.connect(self._generate_forest_template)
        tpl_subsidy = QAction("地力补贴模板", self)
        tpl_subsidy.triggered.connect(self._generate_land_subsidy_template)
        tpl_treatment = QAction("待遇发放模板", self)
        tpl_treatment.triggered.connect(self._generate_treatment_payment_template)
        tpl_pension = QAction("养老保险模板", self)
        tpl_pension.triggered.connect(self._generate_pension_insurance_template)
        tpl_dibao = QAction("低保发放模板", self)
        tpl_dibao.triggered.connect(self._generate_dibao_payment_template)
        tpl_tekun = QAction("特困发放模板", self)
        tpl_tekun.triggered.connect(self._generate_tekun_payment_template)
        template_menu.addAction(tpl_student)
        template_menu.addAction(tpl_forest)
        template_menu.addAction(tpl_subsidy)
        template_menu.addAction(tpl_treatment)
        template_menu.addAction(tpl_pension)
        template_menu.addAction(tpl_dibao)
        template_menu.addAction(tpl_tekun)

        help_menu = menubar.addMenu("帮助")
        check_update_action = QAction("检查更新", self)
        check_update_action.triggered.connect(self._check_for_updates)
        about_action = QAction("关于", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(check_update_action)
        help_menu.addAction(about_action)

        account_menu = menubar.addMenu("账户")
        profile_action = QAction("账户设置", self)
        profile_action.triggered.connect(self._change_profile)
        account_menu.addAction(profile_action)

    def _setup_tray(self):
        icon_dir = os.path.dirname(os.path.abspath(__file__))
        if getattr(sys, 'frozen', False):
            icon_dir = os.path.dirname(sys.executable)
        tray_icon_path = os.path.join(icon_dir, "tray_icon.png")
        if os.path.exists(tray_icon_path):
            self._tray_icon_obj = QIcon(tray_icon_path)
        else:
            pixmap = QPixmap(64, 64)
            pixmap.fill(QColor(0, 102, 204))
            painter = QPainter(pixmap)
            painter.setPen(QColor(255, 255, 255))
            painter.setFont(QFont("Arial", 28, QFont.Weight.Bold))
            painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, "人")
            painter.end()
            self._tray_pixmap = pixmap
            self._tray_icon_obj = QIcon(pixmap)

        self.tray_icon = QSystemTrayIcon(self._tray_icon_obj)
        self.tray_icon.setToolTip(APP_NAME)
        tray_menu = QMenu()
        show_action = tray_menu.addAction("显示窗口")
        show_action.triggered.connect(self._restore_from_tray)
        tray_menu.addSeparator()
        quit_action = tray_menu.addAction("退出")
        quit_action.triggered.connect(self._quit_app)
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.activated.connect(self._on_tray_activated)
        if not self.tray_icon.show():
            pass

    def _restore_from_tray(self):
        self.showNormal()
        self.setWindowState(Qt.WindowState.WindowNoState)
        self.activateWindow()
        self.raise_()
        self.setFocus()

    def _on_tray_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            self._restore_from_tray()

    def _quit_app(self):
        self.tray_icon.hide()
        QApplication.quit()



    def closeEvent(self, event):
        event.ignore()
        self.setWindowState(Qt.WindowState.WindowMinimized)
        self.hide()
        self.tray_icon.show()
        self.tray_icon.showMessage(
            APP_NAME,
            "程序已最小化到系统托盘，双击托盘图标可恢复窗口。",
            QSystemTrayIcon.MessageIcon.Information,
            1500
        )

    def _do_search(self):
        name = self.txt_search.text().strip()
        if not name:
            return
        self.current_name = name
        if self.is_network_mode:
            from network.client import api_search
            try:
                results = api_search(name)
                self.matches = [type('Person', (), r)() for r in results]
            except ConnectionError as e:
                QMessageBox.critical(self, "连接错误", str(e))
                return
        else:
            self.matches = search_by_name(name)
        self._display_name_list()

    def _display_name_list(self):
        for i in reversed(range(self.name_layout.count())):
            widget = self.name_layout.itemAt(i).widget()
            if widget and widget != self.name_label:
                widget.deleteLater()

        self.table.setRowCount(0)
        self.table.setColumnCount(0)

        if not self.matches:
            self.name_label.setText("未找到该人员")
            self.name_label.setStyleSheet("color: red; font-weight: bold; background-color: #DDEBF7; padding: 8px; border: 1px solid #4472C4;")
            return

        count = len(self.matches)
        self.name_label.setText(f"共找到 {count} 个同名同姓人员（点击姓名查看所有同名人员信息）")
        self.name_label.setStyleSheet("color: #003366; font-weight: bold; background-color: #DDEBF7; padding: 8px; border: 1px solid #4472C4;")

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_widget = QWidget()
        grid_layout = QGridLayout(scroll_widget)
        grid_layout.setSpacing(4)
        grid_layout.setContentsMargins(8, 8, 8, 8)

        for idx, person in enumerate(self.matches):
            col = idx // MATCHES_PER_COLUMN
            row = idx % MATCHES_PER_COLUMN
            btn = QPushButton(person.name)
            btn.setFont(QFont(FONT_NAME, 14, QFont.Weight.Bold))
            if person.is_migrated == "是":
                btn.setStyleSheet("background-color: #FFFFCC; padding: 6px; border: 1px solid #ccc; color: #CC0000; text-decoration: line-through;")
            else:
                btn.setStyleSheet("background-color: #FFFFCC; padding: 6px; border: 1px solid #ccc;")
            btn.setFixedHeight(36)
            btn.setMinimumWidth(120)
            btn.clicked.connect(lambda checked, p=person: self._show_family(p))
            grid_layout.addWidget(btn, row, col)

        scroll.setWidget(scroll_widget)
        self.name_layout.addWidget(scroll)

    def _show_family(self, person: Person):
        same_name = [p for p in self.matches if p.name == person.name]
        self.name_label.setText(f"您选择查看：{person.name}（共找到 {len(same_name)} 个同名人员）")
        self.name_label.setStyleSheet("color: #006633; font-weight: bold; background-color: #DDF7DD; padding: 8px; border: 1px solid #00994C;")

        headers = [
            "匹配序号", "家庭人员姓名", "身份证号码", "与户主关系", "本户地址", "年龄",
            "电话号码", "是否死亡", "社保卡号1", "社保卡号2", "社保卡号3",
            "脱贫户或监测户", "备注", "残疾", "残疾等级", "低保", "是否计生家庭",
            "特困供养", "供养类型", "土地面积", "地方公益林", "国家公益林", "非国有天然商品林",
            "本年地力补贴", "照片", "学生标记", "操作"
        ]
        self.table.setColumnCount(len(headers))
        self.table.setHorizontalHeaderLabels(headers)

        self.current_family = []
        self.current_hu_hao = person.hu_hao
        all_families = []
        for idx, p in enumerate(same_name):
            if self.is_network_mode:
                from network.client import api_family
                try:
                    family = api_family(p.hu_hao)
                    family = [type('Member', (), m)() for m in family]
                except ConnectionError as e:
                    QMessageBox.critical(self, "连接错误", str(e))
                    return
            else:
                family = get_family_members(p.hu_hao)
            all_families.append((idx + 1, family))
            self.current_family.extend(family)

        total_rows = 0
        for match_idx, family in all_families:
            total_rows += 1
            total_rows += len(family)

        self.table.setRowCount(total_rows)

        all_visible = set(range(len(headers)))
        all_persons = []
        for match_idx, family in all_families:
            all_persons.extend(family)

        empty_cols = [
            (8, 'social_card1'), (9, 'social_card2'), (10, 'social_card3'),
            (11, 'poor_type'), (12, 'remark'), (13, 'disability'),
            (14, 'dis_level'), (15, 'dibao'), (16, 'jisheng'),
            (17, 'tekun'), (18, 'tekun_type'), (19, 'land_area'),
            (20, 'local_welfare_forest_area'), (21, 'national_welfare_forest_area'), (22, 'commercial_forest_area')
        ]
        for col_idx, field in empty_cols:
            if not any(getattr(p, field, None) and getattr(p, field) != "无" for p in all_persons):
                all_visible.discard(col_idx)

        current_year = str(datetime.now().year)

        row_idx = 0
        for match_idx, family in all_families:
            match_item = QTableWidgetItem(f"第{match_idx}个匹配 - 当前家庭人数：{len(family)}")
            match_item.setBackground(QColor(221, 247, 221))
            match_item.setFont(QFont(FONT_NAME, FONT_SIZE, QFont.Weight.Bold))
            match_item.setForeground(QColor(0, 102, 51))
            match_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setSpan(row_idx, 0, 1, len(headers))
            self.table.setItem(row_idx, 0, match_item)
            row_idx += 1

            for p in family:
                if self.is_network_mode:
                    photo_status = "查看"
                    student_mark = getattr(p, 'student_mark', '') or ""
                    subsidy_amount = getattr(p, 'subsidy_amount', '') or ""
                else:
                    photo_status = "有" if has_any_photo(p.id_card, p.social_card1, p.social_card2, p.social_card3, PHOTOS_DIR) else "无"
                    edu = get_student_education(p.id)
                    student_mark = ""
                    if edu:
                        grade_display = GRADE_DISPLAY.get(edu.grade, edu.grade)
                        student_mark = f"{grade_display} {edu.school_name}"
                    from data.excel_importer import get_person_subsidy_total
                    subsidy_amount = get_person_subsidy_total(p.id_card, current_year)

                values = [
                    "", p.name, p.id_card, p.relation, p.address,
                    p.age, p.phone, p.is_dead,
                    p.social_card1, p.social_card2, p.social_card3,
                    p.poor_type, p.remark, p.disability, p.dis_level,
                    p.dibao, p.jisheng,
                    getattr(p, 'tekun', None) or "", getattr(p, 'tekun_type', None) or "",
                    p.land_area or "",
                    getattr(p, 'local_welfare_forest_area', None) or "",
                    getattr(p, 'national_welfare_forest_area', None) or "",
                    getattr(p, 'commercial_forest_area', None) or "",
                    subsidy_amount, photo_status, student_mark, "查看补贴"
                ]
                is_dead = p.is_dead == "是"
                is_migrated = p.is_migrated == "是"
                for col_idx, val in enumerate(values):
                    if col_idx == len(headers) - 1:
                        btn = QPushButton("查看补贴")
                        btn.setFont(QFont(FONT_NAME, 9))
                        btn.setStyleSheet("background-color: #4CAF50; color: white; padding: 2px 6px; border: none; border-radius: 3px;")
                        btn.clicked.connect(lambda checked, card=p.id_card, name=p.name: self._open_subsidy_detail(card, name))
                        self.table.setCellWidget(row_idx, col_idx, btn)
                    else:
                        item = QTableWidgetItem(str(val) if val else "")
                        item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                        if col_idx == 23 and val:
                            item.setForeground(QColor(0, 102, 0))
                            item.setFont(QFont(FONT_NAME, FONT_SIZE, QFont.Weight.Bold))
                        if is_dead:
                            item.setForeground(QColor(192, 0, 0))
                            item.setFont(QFont(FONT_NAME, FONT_SIZE, QFont.Weight.Bold))
                        elif is_migrated:
                            item.setForeground(QColor(204, 0, 0))
                            font = QFont(FONT_NAME, FONT_SIZE)
                            font.setStrikeOut(True)
                            item.setFont(font)
                        if col_idx not in all_visible:
                            self.table.setColumnHidden(col_idx, True)
                        self.table.setItem(row_idx, col_idx, item)
                row_idx += 1

        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setStretchLastSection(True)

    def _open_subsidy_detail(self, id_card: str, name: str):

        is_admin = self.current_user.get('role') == 'admin'

        dialog = QDialog(self)
        dialog.setWindowTitle("查看补贴")
        dialog.setFixedSize(300, 150)

        layout = QVBoxLayout(dialog)
        layout.setSpacing(10)
        layout.setContentsMargins(20, 20, 20, 20)

        title = QLabel(f"请选择补贴类型：{name}")
        title.setFont(QFont(FONT_NAME, 12))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        btn_layout = QHBoxLayout()

        subsidy_types = [
            ("地力补贴", "land_subsidy"),
            ("待遇发放", "treatment_payment"),
        ]

        for display_name, subsidy_key in subsidy_types:
            btn = QPushButton(display_name)
            btn.setFont(QFont(FONT_NAME, 11))
            btn.clicked.connect(lambda checked, key=subsidy_key: self._show_subsidy_dialog(key, id_card, name, is_admin, dialog))
            btn_layout.addWidget(btn)

        layout.addLayout(btn_layout)

        btn_close = QPushButton("关闭")
        btn_close.clicked.connect(dialog.close)
        layout.addWidget(btn_close)

        dialog.exec()

    def _show_subsidy_dialog(self, subsidy_key: str, id_card: str, name: str, is_admin: bool, parent_dialog: QDialog):
        if subsidy_key == "land_subsidy":
            dialog = LandSubsidyViewDialog(self.is_network_mode, is_admin, parent_dialog)
            dialog.filter_id_card = id_card
            dialog.txt_search.setText(name)
            dialog.exec()
        elif subsidy_key == "treatment_payment":
            dialog = TreatmentPaymentViewDialog(self.is_network_mode, is_admin, parent_dialog)
            dialog.txt_id_card.setText(id_card)
            dialog.exec()

    def _on_double_click(self, index):
        row = index.row()
        if row < 0:
            return
        name_item = self.table.item(row, 1)
        id_item = self.table.item(row, 2)
        if not name_item or not id_item:
            return
        if not name_item.text() or name_item.text().startswith("第") or name_item.text().startswith("匹配"):
            return
        if self.is_network_mode:
            from network.client import api_person
            try:
                data = api_person(id_item.text())
                person = type('Person', (), data)()
                person.id = data['id']
                dialog = EditDialog(person, self)
                if dialog.exec():
                    self._do_search()
            except ConnectionError as e:
                QMessageBox.critical(self, "连接错误", str(e))
        else:
            from core.database import get_session
            session = get_session()
            try:
                person = session.query(Person).filter(
                    Person.name == name_item.text(),
                    Person.id_card == id_item.text()
                ).first()
                if person:
                    dialog = EditDialog(person, self)
                    if dialog.exec():
                        self._do_search()
            finally:
                session.close()

    def _import_excel(self):
        if self.is_network_mode:
            path, _ = QFileDialog.getOpenFileName(
                self, "选择Excel文件", "",
                "Excel文件 (*.xlsx *.xls)"
            )
            if not path:
                return
            import mimetypes
            boundary = '----WebKitFormBoundary7MA4YWxkTrZu0gW'
            with open(path, 'rb') as f:
                file_data = f.read()
            content_type = mimetypes.guess_type(path)[0] or 'application/octet-stream'
            body = (
                f'--{boundary}\r\n'
                f'Content-Disposition: form-data; name="mode"\r\n\r\n'
                f'incremental\r\n'
                f'--{boundary}\r\n'
                f'Content-Disposition: form-data; name="file"; filename="{os.path.basename(path)}"\r\n'
                f'Content-Type: {content_type}\r\n\r\n'
            ).encode('utf-8') + file_data + f'\r\n--{boundary}--\r\n'.encode('utf-8')
            try:
                from network.client import _request_raw
                result = _request_raw('POST', '/api/import/excel', body,
                                      f'multipart/form-data; boundary={boundary}')
                if result.get('imported') is not None:
                    msg = f"导入完成！\n成功：{result.get('imported', 0)}条\n更新：{result.get('updated', 0)}条\n跳过：{result.get('skipped', 0)}条"
                    QMessageBox.information(self, "导入结果", msg)
                else:
                    QMessageBox.critical(self, "导入失败", result.get('error', '未知错误'))
            except Exception as e:
                QMessageBox.critical(self, "导入失败", str(e))
        else:
            dialog = ImportDialog(self)
            if dialog.exec():
                self._refresh_status()

    def _recover_person(self):
        from dialogs.person.recover_dialog import RecoverDialog
        dialog = RecoverDialog(self)
        if dialog.exec():
            self._refresh_status()

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

    def _report_import_excel(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "选择Excel文件", "",
            "Excel文件 (*.xlsx *.xls *.et)"
        )
        if not path:
            return

        report_name = os.path.basename(path)
        name, ok = QInputDialog.getText(self, "报表名称", "请输入报表名称：", text=report_name)
        if not ok or not name.strip():
            return

        with open(path, 'rb') as f:
            file_data = f.read()

        import mimetypes
        content_type = mimetypes.guess_type(path)[0] or 'application/octet-stream'
        boundary = '----WebKitFormBoundary7MA4YWxkTrZu0gW'
        body = (
            f'--{boundary}\r\n'
            f'Content-Disposition: form-data; name="name"\r\n\r\n'
            f'{name.strip()}\r\n'
            f'--{boundary}\r\n'
            f'Content-Disposition: form-data; name="file"; filename="{report_name}"\r\n'
            f'Content-Type: {content_type}\r\n\r\n'
        ).encode('utf-8') + file_data + f'\r\n--{boundary}--\r\n'.encode('utf-8')

        try:
            from network.client import _request_raw
            result = _request_raw('POST', '/api/reports/upload', body,
                                  f'multipart/form-data; boundary={boundary}')
            if result.get('success'):
                QMessageBox.information(self, "成功", f"报表已上传：\n{name.strip()}")
            else:
                QMessageBox.critical(self, "失败", result.get('error', '上传失败'))
        except Exception as e:
            QMessageBox.critical(self, "上传失败", str(e))

    def _report_online_edit(self):

        if not get_server_url():
            QMessageBox.warning(self, "提示", "请先连接服务器后再使用在线编辑功能")
            return

        self.setCursor(Qt.CursorShape.WaitCursor)
        try:
            from network.client import _request
            reports = _request('GET', '/api/reports')
        except Exception as e:
            self.setCursor(Qt.CursorShape.ArrowCursor)
            QMessageBox.critical(self, "错误", f"获取报表列表失败：{e}")
            return
        finally:
            self.setCursor(Qt.CursorShape.ArrowCursor)

        dialog = QDialog(self)
        dialog.setWindowTitle("选择报表进行在线编辑")
        dialog.setFixedSize(700, 400)
        dialog.setWindowFlags(dialog.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint)
        layout = QVBoxLayout(dialog)

        if not reports:
            lbl = QLabel("没有已上传的报表，请先通过「导入Excel」上传报表")
            lbl.setStyleSheet("color: #999; font-size: 14px; padding: 20px;")
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(lbl)
            btn_close = QPushButton("关闭")
            btn_close.setStyleSheet(f"background-color: {BTN_CANCEL_COLOR}; padding: 8px 20px;")
            btn_close.clicked.connect(dialog.reject)
            layout.addWidget(btn_close, alignment=Qt.AlignmentFlag.AlignCenter)
            dialog.exec()
            return

        table = QTableWidget()
        table.setFont(QFont(FONT_NAME, FONT_SIZE))
        table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        headers = ["报表名称", "上传者", "上传时间"]
        table.setColumnCount(len(headers))
        table.setHorizontalHeaderLabels(headers)
        table.setRowCount(len(reports))
        for row_idx, r in enumerate(reports):
            name_item = QTableWidgetItem(r['original_name'])
            name_item.setData(Qt.ItemDataRole.UserRole, r['report_id'])
            name_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            table.setItem(row_idx, 0, name_item)
            table.setItem(row_idx, 1, QTableWidgetItem(r['username']))
            table.setItem(row_idx, 2, QTableWidgetItem(r['upload_time']))
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(table)

        btn_layout = QHBoxLayout()
        btn_open = QPushButton("打开编辑")
        btn_open.setStyleSheet(f"background-color: {BTN_ADD_COLOR}; color: white; font-weight: bold; padding: 8px 20px;")
        btn_close = QPushButton("关闭")
        btn_close.setStyleSheet(f"background-color: {BTN_CANCEL_COLOR}; padding: 8px 20px;")
        btn_layout.addStretch()
        btn_layout.addWidget(btn_open)
        btn_layout.addWidget(btn_close)
        layout.addLayout(btn_layout)

        def do_open():
            row = table.currentRow()
            if row < 0:
                QMessageBox.warning(dialog, "提示", "请选择一个报表")
                return
            report_id = table.item(row, 0).data(Qt.ItemDataRole.UserRole)
            from network.client import get_token
            server_url = get_server_url()
            token = get_token()
            edit_url = f"{server_url}/api/reports/{report_id}/edit?token={token}"
            import webbrowser
            webbrowser.open(edit_url)

        btn_open.clicked.connect(do_open)
        btn_close.clicked.connect(dialog.reject)
        table.doubleClicked.connect(do_open)
        dialog.exec()

    def _report_export_excel(self):

        try:
            from network.client import _request
            reports = _request('GET', '/api/reports')
        except Exception as e:
            QMessageBox.critical(self, "错误", f"获取报表列表失败：{e}")
            return

        if not reports:
            QMessageBox.warning(self, "提示", "没有已上传的报表")
            return

        dialog = QDialog(self)
        dialog.setWindowTitle("选择要导出的报表")
        dialog.setFixedSize(750, 450)
        layout = QVBoxLayout(dialog)

        table = QTableWidget()
        table.setFont(QFont(FONT_NAME, FONT_SIZE))
        table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        headers = ["报表名称", "上传者", "上传时间", "大小"]
        table.setColumnCount(len(headers))
        table.setHorizontalHeaderLabels(headers)
        table.setRowCount(len(reports))
        for row_idx, r in enumerate(reports):
            name_item = QTableWidgetItem(r['original_name'])
            name_item.setData(Qt.ItemDataRole.UserRole, r['report_id'])
            name_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            table.setItem(row_idx, 0, name_item)
            table.setItem(row_idx, 1, QTableWidgetItem(r['username']))
            table.setItem(row_idx, 2, QTableWidgetItem(r['upload_time']))
            size = r.get('file_size', 0)
            if size > 1024 * 1024:
                size_text = f"{size / 1024 / 1024:.1f} MB"
            elif size > 1024:
                size_text = f"{size / 1024:.1f} KB"
            else:
                size_text = f"{size} B"
            table.setItem(row_idx, 3, QTableWidgetItem(size_text))
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(table)

        btn_layout = QHBoxLayout()
        btn_download = QPushButton("下载")
        btn_download.setStyleSheet(f"background-color: {BTN_SAVE_COLOR}; color: white; font-weight: bold; padding: 8px 20px;")
        btn_logs = QPushButton("查看日志")
        btn_logs.setStyleSheet("background-color: #FF6600; color: white; padding: 8px 20px;")
        btn_close = QPushButton("关闭")
        btn_close.setStyleSheet(f"background-color: {BTN_CANCEL_COLOR}; padding: 8px 20px;")
        btn_layout.addStretch()
        btn_layout.addWidget(btn_download)
        btn_layout.addWidget(btn_logs)
        btn_layout.addWidget(btn_close)
        layout.addLayout(btn_layout)

        def do_download():
            row = table.currentRow()
            if row < 0:
                QMessageBox.warning(dialog, "提示", "请选择一个报表")
                return
            report_id = table.item(row, 0).data(Qt.ItemDataRole.UserRole)
            report_name = table.item(row, 0).text()
            save_path, _ = QFileDialog.getSaveFileName(
                dialog, "保存报表", report_name,
                "Excel文件 (*.xlsx *.xls *.et)"
            )
            if not save_path:
                return
            try:
                from network.client import _download_file
                _download_file(f'/api/reports/{report_id}/download', save_path)
                QMessageBox.information(dialog, "成功", f"已保存到：\n{save_path}")
            except Exception as e:
                QMessageBox.critical(dialog, "下载失败", str(e))

        def do_logs():
            row = table.currentRow()
            if row < 0:
                QMessageBox.warning(dialog, "提示", "请选择一个报表")
                return
            report_id = table.item(row, 0).data(Qt.ItemDataRole.UserRole)
            self._show_report_logs(report_id, dialog)

        btn_download.clicked.connect(do_download)
        btn_logs.clicked.connect(do_logs)
        btn_close.clicked.connect(dialog.close)
        dialog.exec()

    def _show_report_logs(self, report_id, parent):

        try:
            from network.client import _request
            data = _request('GET', f'/api/reports/{report_id}/logs')
        except Exception as e:
            QMessageBox.critical(parent, "错误", f"获取日志失败：{e}")
            return

        dialog = QDialog(parent)
        dialog.setWindowTitle("报表操作日志")
        dialog.setFixedSize(800, 450)
        layout = QVBoxLayout(dialog)

        table = QTableWidget()
        table.setFont(QFont(FONT_NAME, FONT_SIZE))
        table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        headers = ["时间", "用户", "操作", "详情", "IP"]
        table.setColumnCount(len(headers))
        table.setHorizontalHeaderLabels(headers)

        all_logs = data.get('file_logs', []) + data.get('db_logs', [])
        all_logs.sort(key=lambda x: x.get('time', ''), reverse=True)
        table.setRowCount(len(all_logs))
        for row_idx, l in enumerate(all_logs):
            for col_idx, key in enumerate(['time', 'user', 'action', 'detail', 'ip']):
                item = QTableWidgetItem(str(l.get(key, '')))
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                table.setItem(row_idx, col_idx, item)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(table)

        btn_close = QPushButton("关闭")
        btn_close.setStyleSheet(f"background-color: {BTN_CANCEL_COLOR}; padding: 8px 20px;")
        layout.addWidget(btn_close, alignment=Qt.AlignmentFlag.AlignCenter)
        btn_close.clicked.connect(dialog.close)
        dialog.exec()

    def _view_change_log(self):

        if not get_server_url():
            QMessageBox.warning(self, "提示", "请先连接服务器后查看日志")
            return

        self.setCursor(Qt.CursorShape.WaitCursor)
        try:
            from network.client import _request
            reports = _request('GET', '/api/reports')
        except Exception as e:
            self.setCursor(Qt.CursorShape.ArrowCursor)
            QMessageBox.critical(self, "错误", f"获取报表列表失败：{e}")
            return
        finally:
            self.setCursor(Qt.CursorShape.ArrowCursor)

        dialog = QDialog(self)
        dialog.setWindowTitle("选择报表查看操作日志")
        dialog.setFixedSize(750, 450)
        layout = QVBoxLayout(dialog)

        if not reports:
            lbl = QLabel("没有已上传的报表")
            lbl.setStyleSheet("color: #999; font-size: 14px; padding: 20px;")
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(lbl)
            btn_close = QPushButton("关闭")
            btn_close.setStyleSheet(f"background-color: {BTN_CANCEL_COLOR}; padding: 8px 20px;")
            btn_close.clicked.connect(dialog.reject)
            layout.addWidget(btn_close, alignment=Qt.AlignmentFlag.AlignCenter)
            dialog.exec()
            return

        table = QTableWidget()
        table.setFont(QFont(FONT_NAME, FONT_SIZE))
        table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        headers = ["报表名称", "上传者", "上传时间"]
        table.setColumnCount(len(headers))
        table.setHorizontalHeaderLabels(headers)
        table.setRowCount(len(reports))
        for row_idx, r in enumerate(reports):
            name_item = QTableWidgetItem(r['original_name'])
            name_item.setData(Qt.ItemDataRole.UserRole, r['report_id'])
            name_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            table.setItem(row_idx, 0, name_item)
            table.setItem(row_idx, 1, QTableWidgetItem(r['username']))
            table.setItem(row_idx, 2, QTableWidgetItem(r['upload_time']))
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(table)

        btn_layout = QHBoxLayout()
        btn_view = QPushButton("查看日志")
        btn_view.setStyleSheet(f"background-color: {BTN_SAVE_COLOR}; color: white; font-weight: bold; padding: 8px 20px;")
        btn_close = QPushButton("关闭")
        btn_close.setStyleSheet(f"background-color: {BTN_CANCEL_COLOR}; padding: 8px 20px;")
        btn_layout.addStretch()
        btn_layout.addWidget(btn_view)
        btn_layout.addWidget(btn_close)
        layout.addLayout(btn_layout)

        def do_view():
            row = table.currentRow()
            if row < 0:
                QMessageBox.warning(dialog, "提示", "请选择一个报表")
                return
            report_id = table.item(row, 0).data(Qt.ItemDataRole.UserRole)
            report_name = table.item(row, 0).text()
            self._show_report_logs_dialog(report_id, report_name, dialog)

        btn_view.clicked.connect(do_view)
        table.doubleClicked.connect(do_view)
        btn_close.clicked.connect(dialog.reject)
        dialog.exec()

    def _show_report_logs_dialog(self, report_id, report_name, parent):

        try:
            from network.client import _request
            data = _request('GET', f'/api/reports/{report_id}/logs')
        except Exception as e:
            QMessageBox.critical(parent, "错误", f"获取日志失败：{e}")
            return

        dialog = QDialog(parent)
        dialog.setWindowTitle(f"操作日志 - {report_name}")
        dialog.setFixedSize(850, 500)
        layout = QVBoxLayout(dialog)

        table = QTableWidget()
        table.setFont(QFont(FONT_NAME, FONT_SIZE))
        table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        headers = ["时间", "用户", "操作", "详情", "IP"]
        table.setColumnCount(len(headers))
        table.setHorizontalHeaderLabels(headers)

        all_logs = data.get('db_logs', []) + data.get('file_logs', [])
        all_logs.sort(key=lambda x: x.get('time', ''), reverse=True)
        table.setRowCount(len(all_logs))
        for row_idx, l in enumerate(all_logs):
            for col_idx, key in enumerate(['time', 'user', 'action', 'detail', 'ip']):
                item = QTableWidgetItem(str(l.get(key, '')))
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                table.setItem(row_idx, col_idx, item)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(table)

        btn_close = QPushButton("关闭")
        btn_close.setStyleSheet(f"background-color: {BTN_CANCEL_COLOR}; padding: 8px 20px;")
        layout.addWidget(btn_close, alignment=Qt.AlignmentFlag.AlignCenter)
        btn_close.clicked.connect(dialog.close)
        dialog.exec()

    def _batch_import_ids(self):

        if not get_server_url():
            QMessageBox.warning(self, "提示", "请先连接服务器后使用此功能")
            return

        self.setCursor(Qt.CursorShape.WaitCursor)
        try:
            from network.client import _request
            reports = _request('GET', '/api/reports')
        except Exception as e:
            self.setCursor(Qt.CursorShape.ArrowCursor)
            QMessageBox.critical(self, "错误", f"获取报表列表失败：{e}")
            return
        finally:
            self.setCursor(Qt.CursorShape.ArrowCursor)

        if not reports:
            QMessageBox.warning(self, "提示", "没有已上传的报表，请先导入报表")
            return

        sel_dialog = QDialog(self)
        sel_dialog.setWindowTitle("选择要导入证件号码的报表")
        sel_dialog.setFixedSize(700, 400)
        sel_layout = QVBoxLayout(sel_dialog)

        table = QTableWidget()
        table.setFont(QFont(FONT_NAME, FONT_SIZE))
        table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        headers = ["报表名称", "上传者", "上传时间"]
        table.setColumnCount(len(headers))
        table.setHorizontalHeaderLabels(headers)
        table.setRowCount(len(reports))
        for row_idx, r in enumerate(reports):
            name_item = QTableWidgetItem(r['original_name'])
            name_item.setData(Qt.ItemDataRole.UserRole, r['report_id'])
            name_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            table.setItem(row_idx, 0, name_item)
            table.setItem(row_idx, 1, QTableWidgetItem(r['username']))
            table.setItem(row_idx, 2, QTableWidgetItem(r['upload_time']))
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        sel_layout.addWidget(table)

        sel_btn_layout = QHBoxLayout()
        sel_ok = QPushButton("下一步")
        sel_ok.setStyleSheet(f"background-color: {BTN_SAVE_COLOR}; color: white; font-weight: bold; padding: 8px 20px;")
        sel_cancel = QPushButton("取消")
        sel_cancel.setStyleSheet(f"background-color: {BTN_CANCEL_COLOR}; padding: 8px 20px;")
        sel_btn_layout.addStretch()
        sel_btn_layout.addWidget(sel_ok)
        sel_btn_layout.addWidget(sel_cancel)
        sel_layout.addLayout(sel_btn_layout)

        selected_report = [None]
        def do_next():
            row = table.currentRow()
            if row < 0:
                QMessageBox.warning(sel_dialog, "提示", "请选择一个报表")
                return
            selected_report[0] = {
                'report_id': table.item(row, 0).data(Qt.ItemDataRole.UserRole),
                'report_name': table.item(row, 0).text(),
            }
            sel_dialog.accept()

        sel_ok.clicked.connect(do_next)
        sel_cancel.clicked.connect(sel_dialog.reject)

        if sel_dialog.exec() != QDialog.DialogCode.Accepted or not selected_report[0]:
            return

        report_id = selected_report[0]['report_id']
        report_name = selected_report[0]['report_name']

        path, _ = QFileDialog.getOpenFileName(
            self, "选择证件号码Excel文件", "",
            "Excel文件 (*.xlsx *.xls *.et)"
        )
        if not path:
            return

        try:
            ext = os.path.splitext(path)[1].lower()
            if ext == '.et':
                import xlrd
                wb = xlrd.open_workbook(path)
                ws = wb.sheet_by_index(0)
                id_list = []
                for i in range(1, ws.nrows):
                    id_card = str(ws.cell(i, 0).value).strip() if ws.cell(i, 0).value else ""
                    phone = str(ws.cell(i, 1).value).strip() if ws.ncols > 1 and ws.cell(i, 1).value else ""
                    social1 = str(ws.cell(i, 2).value).strip() if ws.ncols > 2 and ws.cell(i, 2).value else ""
                    social2 = str(ws.cell(i, 3).value).strip() if ws.ncols > 3 and ws.cell(i, 3).value else ""
                    social3 = str(ws.cell(i, 4).value).strip() if ws.ncols > 4 and ws.cell(i, 4).value else ""
                    if id_card:
                        id_list.append({"id_card": id_card, "phone": phone, "social1": social1, "social2": social2, "social3": social3})
            else:
                import openpyxl
                wb = openpyxl.load_workbook(path, read_only=True)
                ws = wb.active
                id_list = []
                for row in ws.iter_rows(min_row=2, values_only=True):
                    if not row or not row[0]:
                        continue
                    id_card = str(row[0]).strip() if row[0] else ""
                    phone = str(row[1]).strip() if len(row) > 1 and row[1] else ""
                    social1 = str(row[2]).strip() if len(row) > 2 and row[2] else ""
                    social2 = str(row[3]).strip() if len(row) > 3 and row[3] else ""
                    social3 = str(row[4]).strip() if len(row) > 4 and row[4] else ""
                    if id_card:
                        id_list.append({"id_card": id_card, "phone": phone, "social1": social1, "social2": social2, "social3": social3})
        except Exception as e:
            QMessageBox.critical(self, "读取失败", str(e))
            return

        if not id_list:
            QMessageBox.warning(self, "提示", "文件中没有有效数据")
            return

        reply = QMessageBox.question(
            self, "确认导入",
            f"将把 {len(id_list)} 条证件号码导入到报表「{report_name}」中，按身份证号匹配。\n\n确定继续？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        try:
            from network.client import _request
            result = _request('POST', f'/api/reports/{report_id}/import_ids', {'ids': id_list})
            if result.get('success'):
                QMessageBox.information(self, "导入完成",
                    f"更新：{result.get('updated', 0)} 条\n未匹配：{result.get('not_found', 0)} 条")
            else:
                QMessageBox.critical(self, "导入失败", result.get('error', '未知错误'))
        except Exception as e:
            QMessageBox.critical(self, "导入失败", str(e))

    def _manual_backup(self):
        if self.is_network_mode:
            reply = QMessageBox.question(
                self, "确认备份",
                "确定要备份服务器数据库吗？",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                try:
                    from network.client import _request
                    result = _request('POST', '/api/backup')
                    if result.get('success'):
                        QMessageBox.information(self, "成功", "服务器数据库备份成功！")
                    else:
                        QMessageBox.critical(self, "备份失败", result.get('error', '未知错误'))
                except Exception as e:
                    QMessageBox.critical(self, "备份失败", str(e))
        else:
            path = backup_database()
            if path:
                QMessageBox.information(self, "成功", f"备份已保存到：{path}")
            else:
                QMessageBox.warning(self, "提示", "数据库文件不存在，无法备份")

    def _auto_backup(self):
        timer = QTimer(self)
        timer.timeout.connect(self._do_backup)
        timer.start(24 * 60 * 60 * 1000)

    def _do_backup(self):
        backup_database()

    def _refresh_status(self):
        if self.is_network_mode:
            try:
                from network.client import api_stats
                stats = api_stats()
                self.lbl_status.setText(f"数据库记录数：{stats.get('total_persons', '?')}")
            except Exception:
                self.lbl_status.setText("数据库记录数：获取失败")
        else:
            self.lbl_status.setText(f"数据库记录数：{get_person_count()}")
        self._update_status_bar()

    def _update_status_bar(self):
        if self.is_network_mode:
            self.lbl_backup.setText("备份状态：服务器管理")
            self.lbl_backup.setStyleSheet("color: #666;")
        else:
            from data.excel_importer import get_backup_status
            backup_info = get_backup_status()
            if backup_info["last_backup"]:
                self.lbl_backup.setText(f"最近备份：{backup_info['last_backup']}")
                self.lbl_backup.setStyleSheet("color: green;")
            else:
                self.lbl_backup.setText("备份状态：无备份")
                self.lbl_backup.setStyleSheet("color: orange;")
        
        total, used, free = shutil.disk_usage("/")
        free_gb = free // (1024**3)
        if free_gb < 10:
            self.lbl_disk.setText(f"磁盘空间：{free_gb}GB ⚠️")
            self.lbl_disk.setStyleSheet("color: red; font-weight: bold;")
        else:
            self.lbl_disk.setText(f"磁盘空间：{free_gb}GB")
            self.lbl_disk.setStyleSheet("color: green;")

    def _change_profile(self):
        if not self.current_user:
            QMessageBox.warning(self, "提示", "未获取到用户信息！")
            return
        from dialogs.user_dialog import ChangeProfileDialog
        dialog = ChangeProfileDialog(self.current_user, self)
        if dialog.exec():
            pass

    def _show_about(self):
        from core.config import APP_VERSION
        QMessageBox.about(
            self, "关于",
            f"{APP_NAME}\n版本：{APP_VERSION}\n\n基于Python + PyQt6 + SQLite"
        )

    def _check_for_updates(self):
        self._update_dialog = None
        self._show_update_dialog(None)

    def _show_update_dialog(self, version_info):
                     

        if self._update_dialog:
            self._update_dialog.raise_()
            self._update_dialog.activateWindow()
            return

        self._update_dialog = QDialog(self)
        self._update_dialog.setWindowTitle("检查更新")
        self._update_dialog.setFixedSize(480, 320)
        self._update_dialog.setWindowFlags(self._update_dialog.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint)
        self._update_btn_now = None
        self._update_dialog.finished.connect(lambda: (setattr(self, '_update_dialog', None), setattr(self, '_update_btn_now', None)))
        layout = QVBoxLayout(self._update_dialog)
        layout.setSpacing(12)

        self._update_status = QLabel("正在检查更新...")
        self._update_status.setFont(QFont(FONT_NAME, 11))
        self._update_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self._update_status)

        self._update_progress = QProgressBar()
        self._update_progress.setRange(0, 0)
        layout.addWidget(self._update_progress)

        self._update_info = QTextEdit()
        self._update_info.setReadOnly(True)
        self._update_info.setMaximumHeight(120)
        self._update_info.setVisible(False)
        layout.addWidget(self._update_info)

        btn_layout = QHBoxLayout()
        self._update_btn_close = QPushButton("关闭")
        self._update_btn_close.clicked.connect(self._update_dialog.close)
        self._update_btn_close.setVisible(False)
        btn_layout.addStretch()
        btn_layout.addWidget(self._update_btn_close)
        layout.addLayout(btn_layout)

        self._update_dialog.show()

        if version_info:
            self._on_version_check_done(version_info, "")
        else:
            self._version_worker = VersionCheckWorker()
            self._version_worker.finished.connect(self._on_version_check_done)
            self._version_worker.start()

    def _on_version_check_done(self, version_info, error):
        self._update_progress.setRange(0, 1)
        self._update_progress.setValue(1)

        if error:
            self._update_status.setText("检查更新失败")
            self._update_status.setStyleSheet("color: red;")
            self._update_info.setVisible(True)
            self._update_info.setText(error)
            self._update_btn_close.setVisible(True)
            return

        if not version_info:
            self._update_status.setText("当前已是最新版本")
            self._update_status.setStyleSheet("color: green;")
            self._update_btn_close.setVisible(True)
            return

        latest_version = version_info.get("desktop_version", version_info.get("latest_version", ""))
        release_notes = version_info.get("desktop_release_notes", version_info.get("release_notes", "无"))
        file_size = version_info.get("desktop_file_size", version_info.get("file_size", 0))

        self._update_status.setText(f"发现新版本：{latest_version}")
        self._update_status.setStyleSheet("color: #0066CC; font-weight: bold;")

        size_text = ""
        if file_size > 1024 * 1024:
            size_text = f"文件大小：{file_size / 1024 / 1024:.1f} MB"
        elif file_size > 1024:
            size_text = f"文件大小：{file_size / 1024:.1f} KB"

        self._update_info.setVisible(True)
        self._update_info.setText(f"更新内容：\n{release_notes}\n\n{size_text}")
        self._update_info.setStyleSheet("background-color: #F5F5F5;")

        self._update_btn_close.setText("暂不更新")
        self._update_btn_close.setVisible(True)

        if hasattr(self, '_update_btn_now') and self._update_btn_now:
            return

        btn_update = QPushButton("立即更新")
        btn_update.setStyleSheet("background-color: #0078D4; color: white; font-weight: bold; padding: 8px 24px;")
        self._update_btn_now = btn_update
        btn_layout = self._update_dialog.findChild(QHBoxLayout)
        btn_layout.insertWidget(0, btn_update)

        def do_update():
            btn_update.setEnabled(False)
            btn_update.setText("下载中...")
            self._update_btn_close.setEnabled(False)
            self._update_progress.setRange(0, 100)
            self._update_progress.setValue(0)
            self._update_status.setText("正在下载更新...")
            self._update_status.setStyleSheet("color: #0066CC;")
            self._update_info.setVisible(False)

            self._dl_worker = DownloadWorker(version_info)

            def on_progress(downloaded, total):
                if total > 0:
                    percent = int(downloaded * 100 / total)
                    self._update_progress.setValue(percent)
                    mb_done = downloaded / 1024 / 1024
                    mb_total = total / 1024 / 1024
                    self._update_status.setText(f"正在下载更新... {mb_done:.1f}/{mb_total:.1f} MB ({percent}%)")
                else:
                    mb_done = downloaded / 1024 / 1024
                    self._update_status.setText(f"正在下载更新... {mb_done:.1f} MB")

            def on_finished(filepath, error):
                if error:
                    self._update_progress.setRange(0, 1)
                    self._update_progress.setValue(1)
                    self._update_status.setText("下载失败")
                    self._update_status.setStyleSheet("color: red;")
                    self._update_info.setVisible(True)
                    self._update_info.setText(error)
                    btn_update.setText("下载失败")
                    self._update_btn_close.setEnabled(True)
                    return

                self._update_status.setText("正在验证文件...")
                self._update_progress.setRange(0, 0)

                checksum = version_info.get("checksum", "")
                if not verify_file(filepath, checksum):
                    self._update_progress.setRange(0, 1)
                    self._update_progress.setValue(1)
                    self._update_status.setText("验证失败")
                    self._update_status.setStyleSheet("color: red;")
                    self._update_info.setVisible(True)
                    self._update_info.setText("下载文件验证失败，请重新下载。")
                    os.remove(filepath)
                    btn_update.setText("验证失败")
                    self._update_btn_close.setEnabled(True)
                    return

                self._update_status.setText("正在准备安装...")
                update_local_version(version_info)

                ok, err = apply_update(filepath)
                if ok:
                    self._update_status.setText("更新成功，程序即将重启...")
                    self._update_status.setStyleSheet("color: green; font-weight: bold;")
                    self._update_progress.setRange(0, 1)
                    self._update_progress.setValue(1)
                    btn_update.setVisible(False)
                    self._update_btn_close.setText("立即重启")
                    self._update_btn_close.setVisible(True)
                    self._update_btn_close.setEnabled(True)
                    self._update_btn_close.clicked.disconnect()
                    self._update_btn_close.clicked.connect(QApplication.quit)
                else:
                    self._update_progress.setRange(0, 1)
                    self._update_progress.setValue(1)
                    self._update_status.setText("下载完成")
                    self._update_status.setStyleSheet("color: green;")
                    self._update_info.setVisible(True)
                    self._update_info.setText(f"更新文件已下载到：\n{filepath}\n\n请手动安装更新。")
                    btn_update.setVisible(False)
                    self._update_btn_close.setEnabled(True)

            self._dl_worker.progress.connect(on_progress)
            self._dl_worker.finished.connect(on_finished)
            self._dl_worker.start()

        btn_update.clicked.connect(do_update)

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

    def _view_forest_info(self):
        from PyQt6.QtWidgets import QTableWidget, QTableWidgetItem, QHeaderView
        dialog = QDialog(self)
        dialog.setWindowTitle("林地信息查看")
        dialog.resize(900, 500)
        layout = QVBoxLayout(dialog)

        headers = ["户号", "姓名", "地方公益林(亩)", "国家公益林(亩)", "非国有天然商品林(亩)"]
        table = QTableWidget()
        table.setColumnCount(len(headers))
        table.setHorizontalHeaderLabels(headers)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(table)

        persons = []
        if self.is_network_mode:
            try:
                from network.client import _request
                resp = _request('GET', '/api/persons', params={'page': 1, 'per_page': 10000})
                persons = resp.get('persons', resp.get('data', resp.get('items', [])))
            except Exception as e:
                QMessageBox.warning(self, "错误", f"查询失败：{e}")
                return
        else:
            from core.database import get_session, Person
            session = get_session()
            persons = session.query(Person).all()
            session.close()

        rows = 0
        for p in persons:
            lw = getattr(p, 'local_welfare_forest_area', None) or ""
            nw = getattr(p, 'national_welfare_forest_area', None) or ""
            cf = getattr(p, 'commercial_forest_area', None) or ""
            if lw or nw or cf:
                table.insertRow(rows)
                table.setItem(rows, 0, QTableWidgetItem(str(getattr(p, 'hu_hao', '') or "")))
                table.setItem(rows, 1, QTableWidgetItem(str(getattr(p, 'name', '') or "")))
                table.setItem(rows, 2, QTableWidgetItem(str(lw)))
                table.setItem(rows, 3, QTableWidgetItem(str(nw)))
                table.setItem(rows, 4, QTableWidgetItem(str(cf)))
                rows += 1

        lbl_summary = QLabel(f"共 {rows} 人有林地信息")
        layout.addWidget(lbl_summary)
        dialog.exec()

    def _export_forest_data(self):
        self._export_excel()

    def _student_query(self):
        from dialogs.student.student_query_dialog import StudentQueryDialog
        dialog = StudentQueryDialog(self)
        dialog.exec()

    def _import_student_education(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "选择Excel文件", "",
            "Excel文件 (*.xlsx *.xls *.et)"
        )
        if not path:
            return
        if self.is_network_mode:
            import mimetypes
            boundary = '----WebKitFormBoundary7MA4YWxkTrZu0gW'
            with open(path, 'rb') as f:
                file_data = f.read()
            content_type = mimetypes.guess_type(path)[0] or 'application/octet-stream'
            body = (
                f'--{boundary}\r\n'
                f'Content-Disposition: form-data; name="file"; filename="{os.path.basename(path)}"\r\n'
                f'Content-Type: {content_type}\r\n\r\n'
            ).encode('utf-8') + file_data + f'\r\n--{boundary}--\r\n'.encode('utf-8')
            try:
                from network.client import _request_raw
                result = _request_raw('POST', '/api/students/import', body,
                                      f'multipart/form-data; boundary={boundary}')
                if result.get('imported') is not None:
                    msg = f"导入完成！\n成功：{result.get('imported', 0)}条\n更新：{result.get('updated', 0)}条\n跳过：{result.get('skipped', 0)}条"
                    if result.get("errors"):
                        msg += f"\n错误：{len(result['errors'])}条\n" + "\n".join(result["errors"][:5])
                    QMessageBox.information(self, "导入结果", msg)
                else:
                    QMessageBox.critical(self, "导入失败", result.get('error', '未知错误'))
            except Exception as e:
                QMessageBox.critical(self, "导入失败", str(e))
        else:
            from data.student_importer import import_student_education
            result = import_student_education(path)
            msg = f"导入完成！\n成功：{result['imported']}条\n更新：{result['updated']}条\n跳过：{result['skipped']}条"
            if result["errors"]:
                msg += f"\n错误：{len(result['errors'])}条\n" + "\n".join(result["errors"][:5])
            QMessageBox.information(self, "导入结果", msg)

    def _export_student_education(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "导出就读信息", f"学生就读信息_{datetime.now().strftime('%Y%m%d')}.xlsx",
            "Excel文件 (*.xlsx)"
        )
        if not path:
            return
        if self.is_network_mode:
            try:
                from network.client import _download_file
                _download_file('/api/students/export', path)
                QMessageBox.information(self, "成功", f"数据已导出到：{path}")
            except Exception as e:
                QMessageBox.critical(self, "导出失败", str(e))
        else:
            from data.student_importer import export_student_education
            if export_student_education(path):
                QMessageBox.information(self, "成功", f"数据已导出到：{path}")
            else:
                QMessageBox.warning(self, "提示", "没有数据可导出")

    def _generate_student_template(self):
        from data.student_importer import export_student_education_template
        path, _ = QFileDialog.getSaveFileName(
            self, "保存模板", "学生就读信息模板.xlsx",
            "Excel文件 (*.xlsx)"
        )
        if path:
            export_student_education_template(path)
            QMessageBox.information(self, "成功", f"模板已生成：{path}")

    def _generate_forest_template(self):
        from data.excel_forest_template import generate_forest_template
        path, _ = QFileDialog.getSaveFileName(
            self, "保存模板", "林地面积导入模板.xlsx",
            "Excel文件 (*.xlsx)"
        )
        if path:
            generate_forest_template(path)
            QMessageBox.information(self, "成功", f"模板已生成：{path}")

    def _generate_payment_template(self, func_name, default_filename):
        from data.excel_payment_templates import (
            generate_land_subsidy_template,
            generate_treatment_payment_template,
            generate_pension_insurance_template,
            generate_dibao_payment_template,
            generate_tekun_payment_template,
        )
        func_map = {
            'land_subsidy': generate_land_subsidy_template,
            'treatment_payment': generate_treatment_payment_template,
            'pension_insurance': generate_pension_insurance_template,
            'dibao_payment': generate_dibao_payment_template,
            'tekun_payment': generate_tekun_payment_template,
        }
        path, _ = QFileDialog.getSaveFileName(
            self, "保存模板", default_filename,
            "Excel文件 (*.xlsx)"
        )
        if path:
            func_map[func_name](path)
            QMessageBox.information(self, "成功", f"模板已生成：{path}")

    def _generate_land_subsidy_template(self):
        self._generate_payment_template('land_subsidy', '地力补贴导入模板.xlsx')

    def _generate_treatment_payment_template(self):
        self._generate_payment_template('treatment_payment', '待遇发放导入模板.xlsx')

    def _generate_pension_insurance_template(self):
        self._generate_payment_template('pension_insurance', '养老保险导入模板.xlsx')

    def _generate_dibao_payment_template(self):
        self._generate_payment_template('dibao_payment', '低保发放导入模板.xlsx')

    def _generate_tekun_payment_template(self):
        self._generate_payment_template('tekun_payment', '特困发放导入模板.xlsx')

    def _grade_promotion(self):
        from dialogs.student.grade_promotion_dialog import GradePromotionDialog
        dialog = GradePromotionDialog(self)
        if dialog.exec():
            pass

    def _import_land_subsidy(self):
        dialog = LandSubsidyImportDialog(self.is_network_mode, self)
        if dialog.exec():
            pass

    def _view_land_subsidy(self):
        is_admin = self.current_user.get('role') == 'admin'
        dialog = LandSubsidyViewDialog(self.is_network_mode, is_admin, self)
        dialog.exec()

    def _import_treatment_payment(self):
        dialog = TreatmentPaymentImportDialog(self.is_network_mode, self)
        if dialog.exec():
            pass

    def _view_treatment_payment(self):
        is_admin = self.current_user.get('role') == 'admin'
        dialog = TreatmentPaymentViewDialog(self.is_network_mode, is_admin, self)
        dialog.exec()

    def _import_pension_insurance(self):
        dialog = PensionInsuranceImportDialog(self.is_network_mode, self)
        if dialog.exec():
            pass

    def _view_pension_insurance(self):
        is_admin = self.current_user.get('role') == 'admin'
        dialog = PensionInsuranceViewDialog(self.is_network_mode, is_admin, self)
        dialog.exec()

    def _add_household(self):
        from core.database import generate_new_hu_hao, add_new_household

        dialog = QDialog(self)
        dialog.setWindowTitle("新增户")
        dialog.setFixedSize(400, 340)
        layout = QVBoxLayout(dialog)

        title = QLabel("新增户")
        title.setFont(QFont(FONT_NAME, 12, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        form = QFormLayout()
        txt_huhao = QLineEdit()
        if self.is_network_mode:
            try:
                from network.client import api_new_hu_hao
                result = api_new_hu_hao()
                txt_huhao.setText(result.get('hu_hao', ''))
            except Exception:
                txt_huhao.setText('')
        else:
            txt_huhao.setText(generate_new_hu_hao())
        form.addRow("户号：", txt_huhao)
        txt_name = QLineEdit()
        txt_name.setPlaceholderText("户主姓名")
        form.addRow("户主姓名：", txt_name)
        txt_idcard = QLineEdit()
        txt_idcard.setPlaceholderText("身份证号")
        form.addRow("身份证号：", txt_idcard)
        txt_address = QLineEdit()
        form.addRow("地址：", txt_address)
        txt_phone = QLineEdit()
        form.addRow("电话：", txt_phone)
        txt_land = QLineEdit()
        txt_land.setPlaceholderText("亩")
        form.addRow("土地面积：", txt_land)
        txt_local_welfare_forest = QLineEdit()
        txt_local_welfare_forest.setPlaceholderText("亩")
        form.addRow("地方公益林：", txt_local_welfare_forest)
        txt_national_welfare_forest = QLineEdit()
        txt_national_welfare_forest.setPlaceholderText("亩")
        form.addRow("国家公益林：", txt_national_welfare_forest)
        txt_commercial_forest = QLineEdit()
        txt_commercial_forest.setPlaceholderText("亩")
        form.addRow("非国有天然商品林：", txt_commercial_forest)
        layout.addLayout(form)

        def do_add():
            if not txt_name.text().strip():
                QMessageBox.warning(dialog, "提示", "请输入户主姓名！")
                return
            if not txt_idcard.text().strip():
                QMessageBox.warning(dialog, "提示", "请输入身份证号！")
                return
            try:
                if self.is_network_mode:
                    from network.client import api_add_household
                    result = api_add_household({
                        'hu_hao': txt_huhao.text().strip(),
                        'name': txt_name.text().strip(),
                        'id_card': txt_idcard.text().strip(),
                        'address': txt_address.text().strip(),
                        'phone': txt_phone.text().strip(),
                        'land_area': txt_land.text().strip(),
                        'local_welfare_forest_area': txt_local_welfare_forest.text().strip(),
                        'national_welfare_forest_area': txt_national_welfare_forest.text().strip(),
                        'commercial_forest_area': txt_commercial_forest.text().strip()
                    })
                    if result.get('success'):
                        QMessageBox.information(dialog, "成功", f"新户 {txt_huhao.text()} 创建成功！")
                        dialog.accept()
                        self._do_search()
                    else:
                        QMessageBox.critical(dialog, "错误", result.get('error', '创建失败'))
                else:
                    add_new_household(
                        hu_hao=txt_huhao.text().strip(),
                        name=txt_name.text().strip(),
                        id_card=txt_idcard.text().strip(),
                        address=txt_address.text().strip(),
                        phone=txt_phone.text().strip(),
                        land_area=txt_land.text().strip(),
                        local_welfare_forest_area=txt_local_welfare_forest.text().strip(),
                        national_welfare_forest_area=txt_national_welfare_forest.text().strip(),
                        commercial_forest_area=txt_commercial_forest.text().strip()
                    )
                    QMessageBox.information(dialog, "成功", f"新户 {txt_huhao.text()} 创建成功！")
                    dialog.accept()
                    self._do_search()
            except Exception as e:
                QMessageBox.critical(dialog, "错误", str(e))

        btn_layout = QHBoxLayout()
        btn_ok = QPushButton("创建")
        btn_ok.setStyleSheet(f"background-color: {BTN_SAVE_COLOR}; color: white; font-weight: bold; padding: 8px;")
        btn_ok.clicked.connect(do_add)
        btn_cancel = QPushButton("取消")
        btn_cancel.setStyleSheet(f"background-color: {BTN_CANCEL_COLOR}; padding: 8px;")
        btn_cancel.clicked.connect(dialog.reject)
        btn_layout.addWidget(btn_ok)
        btn_layout.addWidget(btn_cancel)
        layout.addLayout(btn_layout)

        dialog.exec()

    def _split_household(self):
        if not self.current_family:
            QMessageBox.warning(self, "提示", "请先查询并选择一个家庭！")
            return


        dialog = QDialog(self)
        dialog.setWindowTitle("分户")
        dialog.setFixedSize(450, 400)
        layout = QVBoxLayout(dialog)

        title = QLabel(f"选择要分出去的人员（当前户号：{self.current_hu_hao}）")
        title.setFont(QFont(FONT_NAME, 11, QFont.Weight.Bold))
        layout.addWidget(title)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        container = QWidget()
        cb_layout = QVBoxLayout(container)

        checkboxes = []
        for p in self.current_family:
            cb = QCheckBox(f"{p.name} ({p.id_card}) - {p.relation}")
            cb.person_id = p.id
            checkboxes.append(cb)
            cb_layout.addWidget(cb)

        scroll.setWidget(container)
        layout.addWidget(scroll)

        def do_split():
            selected = [cb.person_id for cb in checkboxes if cb.isChecked()]
            if not selected:
                QMessageBox.warning(dialog, "提示", "请选择要分户的人员！")
                return
            reply = QMessageBox.question(
                dialog, "确认分户",
                f"确定将 {len(selected)} 人分出为新户？",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                try:
                    if self.is_network_mode:
                        from network.client import _request
                        result = _request('POST', '/api/household/split', {
                            'person_ids': selected
                        })
                        if result.get('success'):
                            QMessageBox.information(dialog, "成功", f"分户成功！新户号：{result['new_hu_hao']}")
                            dialog.accept()
                            self._do_search()
                        else:
                            QMessageBox.critical(dialog, "错误", result.get('error', '分户失败'))
                    else:
                        from core.database import split_household
                        new_hu_hao = split_household(selected)
                        QMessageBox.information(dialog, "成功", f"分户成功！新户号：{new_hu_hao}")
                        dialog.accept()
                        self._do_search()
                except Exception as e:
                    QMessageBox.critical(dialog, "错误", str(e))

        btn_layout = QHBoxLayout()
        btn_ok = QPushButton("确认分户")
        btn_ok.setStyleSheet(f"background-color: {BTN_SAVE_COLOR}; color: white; font-weight: bold; padding: 8px;")
        btn_ok.clicked.connect(do_split)
        btn_cancel = QPushButton("取消")
        btn_cancel.setStyleSheet(f"background-color: {BTN_CANCEL_COLOR}; padding: 8px;")
        btn_cancel.clicked.connect(dialog.reject)
        btn_layout.addWidget(btn_ok)
        btn_layout.addWidget(btn_cancel)
        layout.addLayout(btn_layout)

        dialog.exec()

    def _merge_household(self):
        if not self.current_family:
            QMessageBox.warning(self, "提示", "请先查询并选择一个家庭！")
            return


        dialog = QDialog(self)
        dialog.setWindowTitle("合户")
        dialog.setFixedSize(450, 450)
        layout = QVBoxLayout(dialog)

        title = QLabel(f"合户操作（当前户号：{self.current_hu_hao}）")
        title.setFont(QFont(FONT_NAME, 11, QFont.Weight.Bold))
        layout.addWidget(title)

        form = QFormLayout()
        txt_target = QLineEdit()
        txt_target.setPlaceholderText("目标户号（合并到此户）")
        txt_target.setText(self.current_hu_hao or "")
        form.addRow("目标户号：", txt_target)
        layout.addLayout(form)

        info = QLabel("选择要合并的人员：")
        layout.addWidget(info)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        container = QWidget()
        cb_layout = QVBoxLayout(container)

        checkboxes = []
        for p in self.current_family:
            cb = QCheckBox(f"{p.name} ({p.id_card}) - {p.relation}")
            cb.person_id = p.id
            checkboxes.append(cb)
            cb_layout.addWidget(cb)

        scroll.setWidget(container)
        layout.addWidget(scroll)

        def do_merge():
            target = txt_target.text().strip()
            if not target:
                QMessageBox.warning(dialog, "提示", "请输入目标户号！")
                return
            selected = [cb.person_id for cb in checkboxes if cb.isChecked()]
            if not selected:
                QMessageBox.warning(dialog, "提示", "请选择要合并的人员！")
                return
            reply = QMessageBox.question(
                dialog, "确认合户",
                f"确定将 {len(selected)} 人合并到户号 {target}？",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                try:
                    if self.is_network_mode:
                        from network.client import _request
                        result = _request('POST', '/api/household/merge', {
                            'target_hu_hao': target,
                            'person_ids': selected
                        })
                        if result.get('success'):
                            QMessageBox.information(dialog, "成功", "合户成功！")
                            dialog.accept()
                            self._do_search()
                        else:
                            QMessageBox.critical(dialog, "错误", result.get('error', '合户失败'))
                    else:
                        from core.database import merge_household
                        merge_household(target, selected)
                        QMessageBox.information(dialog, "成功", "合户成功！")
                        dialog.accept()
                        self._do_search()
                except Exception as e:
                    QMessageBox.critical(dialog, "错误", str(e))

        btn_layout = QHBoxLayout()
        btn_ok = QPushButton("确认合户")
        btn_ok.setStyleSheet(f"background-color: {BTN_SAVE_COLOR}; color: white; font-weight: bold; padding: 8px;")
        btn_ok.clicked.connect(do_merge)
        btn_cancel = QPushButton("取消")
        btn_cancel.setStyleSheet(f"background-color: {BTN_CANCEL_COLOR}; padding: 8px;")
        btn_cancel.clicked.connect(dialog.reject)
        btn_layout.addWidget(btn_ok)
        btn_layout.addWidget(btn_cancel)
        layout.addLayout(btn_layout)

        dialog.exec()


def main():
    ensure_dirs()
    from core.database import init_db
    init_db()
    app = QApplication(sys.argv)
    app.setFont(QFont(FONT_NAME, FONT_SIZE))
    app.setQuitOnLastWindowClosed(False)

    _pending_update = [None]
    _bg_worker_ref = [None]

    def _on_bg_version_check(result, error):
        if result and not error:
            _pending_update[0] = result

    _bg_worker_ref[0] = VersionCheckWorker()
    _bg_worker_ref[0].finished.connect(_on_bg_version_check)
    _bg_worker_ref[0].start()

    from dialogs.connect_dialog import ConnectDialog
    connect_dialog = ConnectDialog()
    if not connect_dialog.exec():
        sys.exit(0)

    server_url = connect_dialog.get_server_url()

    current_user = {}

    if server_url:
        from network.client import set_server_url, test_connection, set_token
        set_server_url(server_url)
        if not test_connection():
            QMessageBox.critical(None, "连接失败", f"无法连接到服务器：\n{server_url}\n\n请检查服务器是否启动，或检查网络连接。")
            sys.exit(1)
        from dialogs.user_dialog import LoginDialog
        login_dialog = LoginDialog()
        if login_dialog.exec():
            token = login_dialog.get_token()
            if token:
                set_token(token)
            current_user = login_dialog.get_user() or {}
        else:
            sys.exit(1)
    else:
        from core.database import get_session, set_db_password, reset_engine, is_database_encrypted, decrypt_database, encrypt_database, init_db, get_all_users
        from core.config import DB_PATH

        password = None
        from dialogs.password_dialog import PasswordDialog
        from dialogs.user_dialog import LoginDialog

        if is_database_encrypted():
            dialog = PasswordDialog(is_new=False)
            if dialog.exec():
                password = dialog.get_password()
                if not decrypt_database(password):
                    reply = QMessageBox.question(
                        None, "解密失败",
                        "密码错误或数据库损坏！\n\n"
                        "⚠️ 重要提示：\n"
                        "如果忘记密码，数据将永久丢失，无法恢复！\n\n"
                        "是否删除加密文件重新开始？\n"
                        "（将丢失所有原有数据）",
                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                    )
                    if reply == QMessageBox.StandardButton.Yes:
                        os.remove(DB_PATH + '.enc')
                        if os.path.exists(DB_PATH + '.key'):
                            os.remove(DB_PATH + '.key')
                        password = None
                    else:
                        sys.exit(0)
                else:
                    reset_engine()
            else:
                sys.exit(0)
        
        if not password:
            dialog = PasswordDialog(is_new=True)
            if dialog.exec():
                password = dialog.get_password()
            else:
                sys.exit(0)
        
        if password:
            set_db_password(password)
        
        def cleanup():
            if password:
                try:
                    reset_engine()
                    encrypt_database(password)
                except Exception:
                    pass
        
        app.aboutToQuit.connect(cleanup)
        
        users = get_all_users()
        if not users:
            QMessageBox.warning(None, "系统未初始化", "系统未初始化！\n\n请先在Web服务端创建用户账户后再登录。\n\n启动Web服务端命令：python3 web_app.py")
            sys.exit(0)
        
        login_dialog = LoginDialog()
        if login_dialog.exec():
            current_user = login_dialog.get_user()
        else:
            sys.exit(0)

        session = get_session()
        try:
            session.query(Person).count()
        except Exception:
            if password:
                QMessageBox.critical(None, "错误", "数据库访问失败！")
                sys.exit(1)
            raise
        finally:
            session.close()

    window = MainWindow(current_user)
    window.show()

    if _pending_update[0]:
        QTimer.singleShot(500, lambda: window._show_update_dialog(_pending_update[0]))
    else:
        def _check_after_bg(result, error):
            if result and not error:
                QTimer.singleShot(500, lambda: window._show_update_dialog(result))
        _bg_worker_ref[0].finished.disconnect(_on_bg_version_check)
        _bg_worker_ref[0].finished.connect(_check_after_bg)

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
