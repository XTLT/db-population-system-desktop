"""存量数据库的列迁移（逐列 ALTER，已存在则跳过）。"""


def migrate_db(engine):
    from sqlalchemy import text
    with engine.connect() as conn:
        try:
            conn.execute(text("ALTER TABLE persons ADD COLUMN updated_at VARCHAR DEFAULT ''"))
            conn.commit()
        except Exception:
            pass
        try:
            conn.execute(text("ALTER TABLE users ADD COLUMN is_default VARCHAR DEFAULT '否'"))
            conn.commit()
        except Exception:
            pass
        try:
            conn.execute(text("ALTER TABLE persons ADD COLUMN land_area VARCHAR DEFAULT ''"))
            conn.commit()
        except Exception:
            pass
        try:
            conn.execute(text("ALTER TABLE persons ADD COLUMN land_area_change_reason VARCHAR DEFAULT ''"))
            conn.commit()
        except Exception:
            pass
        try:
            conn.execute(text("ALTER TABLE persons ADD COLUMN land_area_change_time VARCHAR DEFAULT ''"))
            conn.commit()
        except Exception:
            pass
        try:
            conn.execute(text("ALTER TABLE persons ADD COLUMN local_welfare_forest_area VARCHAR DEFAULT ''"))
            conn.commit()
        except Exception:
            pass
        try:
            conn.execute(text("ALTER TABLE persons ADD COLUMN local_welfare_forest_change_reason VARCHAR DEFAULT ''"))
            conn.commit()
        except Exception:
            pass
        try:
            conn.execute(text("ALTER TABLE persons ADD COLUMN local_welfare_forest_change_time VARCHAR DEFAULT ''"))
            conn.commit()
        except Exception:
            pass
        try:
            conn.execute(text("ALTER TABLE persons ADD COLUMN national_welfare_forest_area VARCHAR DEFAULT ''"))
            conn.commit()
        except Exception:
            pass
        try:
            conn.execute(text("ALTER TABLE persons ADD COLUMN national_welfare_forest_change_reason VARCHAR DEFAULT ''"))
            conn.commit()
        except Exception:
            pass
        try:
            conn.execute(text("ALTER TABLE persons ADD COLUMN national_welfare_forest_change_time VARCHAR DEFAULT ''"))
            conn.commit()
        except Exception:
            pass
        try:
            conn.execute(text("ALTER TABLE persons ADD COLUMN commercial_forest_area VARCHAR DEFAULT ''"))
            conn.commit()
        except Exception:
            pass
        try:
            conn.execute(text("ALTER TABLE persons ADD COLUMN commercial_forest_change_reason VARCHAR DEFAULT ''"))
            conn.commit()
        except Exception:
            pass
        try:
            conn.execute(text("ALTER TABLE persons ADD COLUMN commercial_forest_change_time VARCHAR DEFAULT ''"))
            conn.commit()
        except Exception:
            pass
        try:
            conn.execute(text("ALTER TABLE persons ADD COLUMN tekun VARCHAR DEFAULT ''"))
            conn.commit()
        except Exception:
            pass
        try:
            conn.execute(text("ALTER TABLE persons ADD COLUMN tekun_type VARCHAR DEFAULT ''"))
            conn.commit()
        except Exception:
            pass
        try:
            conn.execute(text("ALTER TABLE persons ADD COLUMN disability_type VARCHAR DEFAULT ''"))
            conn.commit()
        except Exception:
            pass
        try:
            conn.execute(text("ALTER TABLE student_education ADD COLUMN graduation_date VARCHAR DEFAULT ''"))
            conn.commit()
        except Exception:
            pass
        try:
            conn.execute(text("ALTER TABLE persons ADD COLUMN social_card2_source VARCHAR DEFAULT ''"))
            conn.commit()
        except Exception:
            pass
        try:
            conn.execute(text("ALTER TABLE persons ADD COLUMN social_card3_source VARCHAR DEFAULT ''"))
            conn.commit()
        except Exception:
            pass
        try:
            conn.execute(text("ALTER TABLE deleted_persons ADD COLUMN social_card2_source VARCHAR DEFAULT ''"))
            conn.commit()
        except Exception:
            pass
        try:
            conn.execute(text("ALTER TABLE deleted_persons ADD COLUMN social_card3_source VARCHAR DEFAULT ''"))
            conn.commit()
        except Exception:
            pass
        try:
            conn.execute(text("ALTER TABLE dibao_payment ADD COLUMN gender VARCHAR DEFAULT ''"))
            conn.commit()
        except Exception:
            pass
        try:
            conn.execute(text("ALTER TABLE dibao_payment ADD COLUMN family_members VARCHAR DEFAULT ''"))
            conn.commit()
        except Exception:
            pass
        try:
            conn.execute(text("ALTER TABLE dibao_payment ADD COLUMN family_count VARCHAR DEFAULT ''"))
            conn.commit()
        except Exception:
            pass
        try:
            conn.execute(text("ALTER TABLE dibao_payment ADD COLUMN base_amount VARCHAR DEFAULT ''"))
            conn.commit()
        except Exception:
            pass
        try:
            conn.execute(text("ALTER TABLE dibao_payment ADD COLUMN special_amount VARCHAR DEFAULT ''"))
            conn.commit()
        except Exception:
            pass
        try:
            conn.execute(text("ALTER TABLE dibao_payment ADD COLUMN adjust_amount VARCHAR DEFAULT ''"))
            conn.commit()
        except Exception:
            pass
        try:
            conn.execute(text("ALTER TABLE dibao_payment ADD COLUMN special_situation VARCHAR DEFAULT ''"))
            conn.commit()
        except Exception:
            pass
        try:
            conn.execute(text("ALTER TABLE dibao_payment ADD COLUMN special_subsidy VARCHAR DEFAULT ''"))
            conn.commit()
        except Exception:
            pass
        try:
            conn.execute(text("ALTER TABLE dibao_payment ADD COLUMN start_time VARCHAR DEFAULT ''"))
            conn.commit()
        except Exception:
            pass
        try:
            conn.execute(text("ALTER TABLE dibao_payment ADD COLUMN issue_month VARCHAR DEFAULT ''"))
            conn.commit()
        except Exception:
            pass
        # land_subsidy 表迁移：电话号码/金融机构/上账时间
        try:
            conn.execute(text("ALTER TABLE land_subsidy ADD COLUMN phone VARCHAR DEFAULT ''"))
            conn.commit()
        except Exception:
            pass
        try:
            conn.execute(text("ALTER TABLE land_subsidy ADD COLUMN bank_name VARCHAR DEFAULT ''"))
            conn.commit()
        except Exception:
            pass
        try:
            conn.execute(text("ALTER TABLE land_subsidy ADD COLUMN land_time VARCHAR DEFAULT ''"))
            conn.commit()
        except Exception:
            pass
        try:
            conn.execute(text("ALTER TABLE land_subsidy ADD COLUMN bank_account VARCHAR DEFAULT ''"))
            conn.commit()
        except Exception:
            pass
        try:
            conn.execute(text("ALTER TABLE land_subsidy ADD COLUMN rape_standard VARCHAR DEFAULT ''"))
            conn.commit()
        except Exception:
            pass
        # 残疾人护理补贴表新增列：手机号/折号/开户行/区划地址/代持代管/户主姓名/户主身份证号/备注
        for col in ("phone", "fold_no", "bank_name", "area_address", "agent_manage",
                    "householder_name", "householder_id_card", "remark"):
            try:
                conn.execute(text(f"ALTER TABLE disability_care_payment ADD COLUMN {col} VARCHAR DEFAULT ''"))
                conn.commit()
            except Exception:
                pass
        # 高龄补贴表新增列（同上8列）
        for col in ("phone", "fold_no", "bank_name", "area_address", "agent_manage",
                    "householder_name", "householder_id_card", "remark"):
            try:
                conn.execute(text(f"ALTER TABLE elderly_allowance ADD COLUMN {col} VARCHAR DEFAULT ''"))
                conn.commit()
            except Exception:
                pass
        # 特困表新增列（与低保相同的10列）
        for col in ("gender", "family_members", "family_count", "base_amount", "special_amount",
                    "adjust_amount", "special_situation", "special_subsidy", "start_time", "issue_month"):
            try:
                conn.execute(text(f"ALTER TABLE tekun_payment ADD COLUMN {col} VARCHAR DEFAULT ''"))
                conn.commit()
            except Exception:
                pass
        # 死亡时间（2026-11-19：改为死亡时必填，存量已死亡人员不回填）
        for _tbl in ("persons", "deleted_persons"):
            try:
                conn.execute(text(f"ALTER TABLE {_tbl} ADD COLUMN death_date VARCHAR DEFAULT ''"))
                conn.commit()
            except Exception:
                pass
