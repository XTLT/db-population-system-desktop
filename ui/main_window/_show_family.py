from datetime import datetime
from PyQt6.QtWidgets import QMessageBox, QTableWidgetItem, QHeaderView, QPushButton
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor
from core.config import GRADE_DISPLAY, FONT_NAME, PHOTOS_DIR, FONT_SIZE
from core.database import Person, get_family_members, get_student_education
from core.utils import has_any_photo


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
