import os
import pandas as pd
from datetime import datetime
import shutil
import tarfile
import hashlib
import secrets
import json

from core.config import DB_PATH, BACKUP_DIR, PHOTOS_DIR, EXCEL_TEMPLATE_COLUMNS
from core.database import get_session, Person, get_db_password, _derive_key, LandSubsidy, TreatmentPayment, PensionInsurance
from core.utils import safe_str, calculate_age


def backup_database(manual: bool = False) -> dict:
    if not os.path.exists(DB_PATH):
        return {"success": False, "error": "数据库文件不存在"}
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = os.path.join(BACKUP_DIR, f"backup_{timestamp}")
    os.makedirs(backup_dir, exist_ok=True)
    
    try:
        db_backup = os.path.join(backup_dir, "population.db")
        shutil.copy2(DB_PATH, db_backup)
        
        photos_backup = os.path.join(backup_dir, "photos.tar.gz")
        if os.path.exists(PHOTOS_DIR) and os.listdir(PHOTOS_DIR):
            with tarfile.open(photos_backup, "w:gz") as tar:
                tar.add(PHOTOS_DIR, arcname="Photos")
        
        password = get_db_password()
        if password:
            _encrypt_backup(backup_dir, password)
        
        db_hash = _calculate_file_hash(db_backup)
        manifest = {
            "timestamp": timestamp,
            "manual": manual,
            "db_hash": db_hash,
            "encrypted": bool(password),
            "complete": True
        }
        with open(os.path.join(backup_dir, "backup_complete.txt"), "w") as f:
            json.dump(manifest, f)
        
        _cleanup_old_backups()
        
        return {"success": True, "path": backup_dir, "timestamp": timestamp}
    except Exception as e:
        return {"success": False, "error": str(e)}


def _encrypt_backup(backup_dir: str, password: str):
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    
    salt = secrets.token_bytes(32)
    key = _derive_key(password, salt)
    
    for filename in os.listdir(backup_dir):
        filepath = os.path.join(backup_dir, filename)
        if os.path.isfile(filepath) and filename != "backup_complete.txt":
            with open(filepath, "rb") as f:
                data = f.read()
            nonce = secrets.token_bytes(12)
            aesgcm = AESGCM(key)
            encrypted = aesgcm.encrypt(nonce, data, None)
            with open(filepath + ".enc", "wb") as f:
                f.write(salt + nonce + encrypted)
            os.remove(filepath)


def _calculate_file_hash(filepath: str) -> str:
    sha256_hash = hashlib.sha256()
    with open(filepath, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


def _cleanup_old_backups():
    if not os.path.exists(BACKUP_DIR):
        return
    
    cutoff_date = datetime.now().timestamp() - (60 * 24 * 60 * 60)
    
    for item in os.listdir(BACKUP_DIR):
        item_path = os.path.join(BACKUP_DIR, item)
        if os.path.isdir(item_path) and item.startswith("backup_"):
            try:
                dir_time = os.path.getmtime(item_path)
                if dir_time < cutoff_date:
                    complete_file = os.path.join(item_path, "backup_complete.txt")
                    if os.path.exists(complete_file):
                        shutil.rmtree(item_path)
            except Exception:
                pass


def get_backup_status() -> dict:
    if not os.path.exists(BACKUP_DIR):
        return {"last_backup": None, "status": "无备份"}
    
    backups = []
    for item in os.listdir(BACKUP_DIR):
        if item.startswith("backup_"):
            item_path = os.path.join(BACKUP_DIR, item)
            complete_file = os.path.join(item_path, "backup_complete.txt")
            if os.path.exists(complete_file):
                backups.append({
                    "path": item_path,
                    "time": os.path.getmtime(item_path)
                })
    
    if not backups:
        return {"last_backup": None, "status": "无备份"}
    
    latest = max(backups, key=lambda x: x["time"])
    return {
        "last_backup": datetime.fromtimestamp(latest["time"]).strftime("%Y-%m-%d %H:%M:%S"),
        "status": "正常"
    }


def import_excel_full(file_path: str, progress_callback=None) -> dict:
    backup_database()
    df = _read_excel_robust(file_path)
    df = df.fillna("")
    total = len(df)
    imported = 0
    skipped = 0
    errors = []
    session = get_session()
    try:
        session.query(Person).delete()
        session.commit()
        for idx, row in df.iterrows():
            try:
                person = _row_to_person(row, idx)
                session.add(person)
                imported += 1
                if progress_callback:
                    progress_callback(int((idx + 1) / total * 100))
            except Exception as e:
                skipped += 1
                errors.append(f"行{idx + 2}: {str(e)}")
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
    return {"imported": imported, "skipped": skipped, "errors": errors, "total": total}


def import_excel_incremental(file_path: str, progress_callback=None) -> dict:
    backup_database()
    df = _read_excel_robust(file_path)
    df = df.fillna("")
    total = len(df)
    imported = 0
    updated = 0
    skipped = 0
    errors = []
    session = get_session()
    try:
        for idx, row in df.iterrows():
            try:
                id_card = safe_str(row.get("身份证号", ""))
                if not id_card:
                    skipped += 1
                    continue
                existing = session.query(Person).filter(Person.id_card == id_card).first()
                if existing:
                    _update_person_from_row(existing, row)
                    updated += 1
                else:
                    person = _row_to_person(row, idx)
                    session.add(person)
                    imported += 1
                if progress_callback:
                    progress_callback(int((idx + 1) / total * 100))
            except Exception as e:
                skipped += 1
                errors.append(f"行{idx + 2}: {str(e)}")
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
    return {"imported": imported, "updated": updated, "skipped": skipped, "errors": errors, "total": total}


def query_persons_with_filters(filters: dict) -> list:
    session = get_session()
    try:
        query = session.query(Person)

        if filters.get("name"):
            query = query.filter(Person.name.contains(filters["name"]))
        if filters.get("address"):
            query = query.filter(Person.address.contains(filters["address"]))
        if filters.get("is_dead") and filters["is_dead"] != "全部":
            query = query.filter(Person.is_dead == filters["is_dead"])
        relation = filters.get("relation", [])
        if relation:
            query = query.filter(Person.relation.in_(relation))
        disability = filters.get("disability", [])
        if disability:
            query = query.filter(Person.disability.in_(disability))
        if filters.get("dis_level"):
            dis_level = filters["dis_level"]
            if isinstance(dis_level, list) and dis_level:
                query = query.filter(Person.dis_level.in_(dis_level))
            elif isinstance(dis_level, str) and dis_level != "全部":
                query = query.filter(Person.dis_level == dis_level)
        poor_type = filters.get("poor_type", [])
        if poor_type:
            query = query.filter(Person.poor_type.in_(poor_type))
        if filters.get("dibao") and filters["dibao"] != "全部":
            query = query.filter(Person.dibao == filters["dibao"])
        if filters.get("jisheng") and filters["jisheng"] != "全部":
            query = query.filter(Person.jisheng == filters["jisheng"])
        if filters.get("tekun") and filters["tekun"] != "全部":
            query = query.filter(Person.tekun == filters["tekun"])
        if filters.get("tekun_type"):
            tekun_type = filters["tekun_type"]
            if isinstance(tekun_type, list) and tekun_type:
                query = query.filter(Person.tekun_type.in_(tekun_type))
            elif isinstance(tekun_type, str) and tekun_type != "全部":
                query = query.filter(Person.tekun_type == tekun_type)
        land = filters.get("land_area", "全部")
        if land == "不为0":
            query = query.filter(Person.land_area != "", Person.land_area.isnot(None))
        elif land == "空白":
            query = query.filter(
                (Person.land_area == "") | (Person.land_area.is_(None))
            )

        persons = query.all()

        if filters.get("age_min") or filters.get("age_max"):
            age_min = int(filters["age_min"]) if filters.get("age_min") else 0
            age_max = int(filters["age_max"]) if filters.get("age_max") else 999
            filtered = []
            for p in persons:
                age = -1
                if p.age:
                    try:
                        age = int(p.age)
                    except (ValueError, TypeError):
                        pass
                if age < 0 and p.id_card:
                    age_str = calculate_age(p.id_card)
                    if age_str:
                        try:
                            age = int(age_str)
                        except (ValueError, TypeError):
                            pass
                if age >= 0 and age_min <= age <= age_max:
                    filtered.append(p)
            persons = filtered

        return persons
    finally:
        session.close()


def export_excel(file_path: str, progress_callback=None, filters: dict = None) -> bool:
    if filters:
        persons = query_persons_with_filters(filters)
    else:
        session = get_session()
        try:
            persons = session.query(Person).all()
        finally:
            session.close()

    if not persons:
        return False

    data = []
    for i, p in enumerate(persons):
        data.append({
            "户号": p.hu_hao,
            "身份证号": p.id_card,
            "姓名": p.name,
            "地址": p.address,
            "与户主关系": p.relation,
            "是否死亡": p.is_dead,
            "电话": p.phone,
            "备注": p.remark,
            "脱贫户或监测户": p.poor_type,
            "残疾": p.disability,
            "残疾等级": p.dis_level,
            "低保": p.dibao,
            "是否计生家庭": p.jisheng,
            "特困供养": getattr(p, 'tekun', '') or "",
            "供养类型": getattr(p, 'tekun_type', '') or "",
            "社保卡号1": p.social_card1,
            "社保卡号2": p.social_card2,
            "社保卡号3": p.social_card3,
            "土地面积": p.land_area or "",
        })
        if progress_callback and (i + 1) % 100 == 0:
            progress_callback(int((i + 1) / len(persons) * 100))
    df = pd.DataFrame(data, columns=EXCEL_TEMPLATE_COLUMNS)
    df.to_excel(file_path, index=False, engine="openpyxl")
    return True


def generate_template(file_path: str):
    df = pd.DataFrame(columns=EXCEL_TEMPLATE_COLUMNS)
    df.to_excel(file_path, index=False, engine="openpyxl")


def _row_to_person(row, idx) -> Person:
    id_card = safe_str(row.get("身份证号", ""))
    return Person(
        id=f"p_{idx}_{id_card}",
        hu_hao=safe_str(row.get("户号", "")),
        id_card=id_card,
        name=safe_str(row.get("姓名", "")),
        age=calculate_age(id_card),
        address=safe_str(row.get("地址", "")),
        relation=safe_str(row.get("与户主关系", "")),
        is_dead=safe_str(row.get("是否死亡", "否")),
        phone=safe_str(row.get("电话", "")),
        remark=safe_str(row.get("备注", "")),
        poor_type=safe_str(row.get("脱贫户或监测户", "")),
        disability=safe_str(row.get("残疾", "")),
        dis_level=safe_str(row.get("残疾等级", "")),
        dibao=safe_str(row.get("低保", "")),
        jisheng=safe_str(row.get("是否计生家庭", "")),
        tekun=safe_str(row.get("特困供养", "")),
        tekun_type=safe_str(row.get("供养类型", "")),
        social_card1=safe_str(row.get("社保卡号1", "")),
        social_card2=safe_str(row.get("社保卡号2", "")),
        social_card3=safe_str(row.get("社保卡号3", "")),
        land_area=safe_str(row.get("土地面积", "")),
    )


def _update_person_from_row(person: Person, row):
    person.hu_hao = safe_str(row.get("户号", person.hu_hao))
    person.name = safe_str(row.get("姓名", person.name))
    person.age = calculate_age(person.id_card)
    person.address = safe_str(row.get("地址", person.address))
    person.relation = safe_str(row.get("与户主关系", person.relation))
    person.is_dead = safe_str(row.get("是否死亡", person.is_dead))
    person.phone = safe_str(row.get("电话", person.phone))
    person.remark = safe_str(row.get("备注", person.remark))
    person.poor_type = safe_str(row.get("脱贫户或监测户", person.poor_type))
    person.disability = safe_str(row.get("残疾", person.disability))
    person.dis_level = safe_str(row.get("残疾等级", person.dis_level))
    person.dibao = safe_str(row.get("低保", person.dibao))
    person.jisheng = safe_str(row.get("是否计生家庭", person.jisheng))
    person.tekun = safe_str(row.get("特困供养", getattr(person, 'tekun', '')))
    person.tekun_type = safe_str(row.get("供养类型", getattr(person, 'tekun_type', '')))
    person.social_card1 = safe_str(row.get("社保卡号1", person.social_card1))
    person.social_card2 = safe_str(row.get("社保卡号2", person.social_card2))
    person.social_card3 = safe_str(row.get("社保卡号3", person.social_card3))
    person.land_area = safe_str(row.get("土地面积", person.land_area))


def _read_excel_robust(file_path: str, header=None):
    """读取 Excel 文件，自动检测格式和引擎"""
    ext = os.path.splitext(file_path)[1].lower()
    engines = (['openpyxl', 'xlrd'] if ext == '.xlsx'
               else ['xlrd', 'openpyxl'] if ext == '.xls'
               else ['openpyxl', 'xlrd'])
    for engine in engines:
        try:
            return pd.read_excel(file_path, dtype=str, header=header, engine=engine)
        except Exception:
            continue
    try:
        return pd.read_csv(file_path, dtype=str, header=header, encoding='utf-8')
    except Exception:
        return pd.read_csv(file_path, dtype=str, header=header, encoding='gbk')


def import_land_subsidy(file_path: str, subsidy_year: str = "", progress_callback=None) -> dict:
    """导入地力补贴数据
    
    只导入身份证号在数据库中存在的人员
    """

    df = _read_excel_robust(file_path)
    df = df.fillna("")

    header_row = -1
    for idx, row in df.iterrows():
        values = [str(v).strip() for v in row.values]
        if "姓名" in values and "身份证号" in values:
            header_row = idx
            break

    if header_row == -1:
        return {"imported": 0, "skipped": 0, "errors": ["未找到表头（姓名、身份证号）"], "total": 0, "not_found": []}

    main_headers = [str(v).strip() for v in df.iloc[header_row].values]

    if header_row + 1 < len(df):
        sub_headers = [str(v).strip() for v in df.iloc[header_row + 1].values]
    else:
        sub_headers = [""] * len(main_headers)

    col_map = {}
    for i, (main, sub) in enumerate(zip(main_headers, sub_headers)):
        if main:
            if sub:
                col_map[i] = f"{main}_{sub}"
            else:
                col_map[i] = main
        elif sub:
            col_map[i] = sub
        else:
            col_map[i] = f"col_{i}"

    data_df = df.iloc[header_row + 2:].reset_index(drop=True)
    data_df.columns = [col_map.get(i, f"col_{i}") for i in range(len(col_map))]

    total = len(data_df)
    imported = 0
    skipped = 0
    errors = []
    not_found = []
    session = get_session()

    # 获取数据库中所有身份证号
    existing_id_cards = set()
    try:
        persons = session.query(Person.id_card).all()
        existing_id_cards = {p.id_card for p in persons if p.id_card}
    except Exception:
        pass

    try:
        for idx, row in data_df.iterrows():
            try:
                name = safe_str(row.get("姓名", ""))
                id_card = safe_str(row.get("身份证号", ""))

                if not name and not id_card:
                    skipped += 1
                    continue

                # 检查身份证号是否在数据库中存在
                if id_card and id_card not in existing_id_cards:
                    not_found.append(f"{name}({id_card})")
                    skipped += 1
                    continue

                certified_area = ""
                for key in row.index:
                    if "确权颁证面积" in key or "确权颁发面积" in key:
                        certified_area = safe_str(row.get(key, ""))
                        break

                subsidy_area = ""
                for key in row.index:
                    if "补贴面积" in key:
                        val = safe_str(row.get(key, ""))
                        subsidy_area = val.replace("（亩）", "").replace("(亩)", "").strip()
                        break

                base_standard = ""
                for key in row.index:
                    if "基础补贴标准" in key:
                        val = safe_str(row.get(key, ""))
                        base_standard = val.replace("（元/亩）", "").replace("(元/亩)", "").strip()
                        break

                rape_area = ""
                for key in row.index:
                    if "其中种植油菜" in key and "面积" in key:
                        rape_area = safe_str(row.get(key, "")).strip()
                        break

                rape_amount = ""
                for key in row.index:
                    if "其中种植油菜" in key and "金额" in key:
                        rape_amount = safe_str(row.get(key, "")).strip()
                        break

                total_amount = ""
                for key in row.index:
                    if "补贴总金额" in key:
                        val = safe_str(row.get(key, ""))
                        total_amount = val.replace("（元）", "").replace("(元)", "").strip()
                        break

                subsidy = LandSubsidy(
                    id=f"ls_{secrets.token_hex(8)}",
                    id_card=id_card,
                    name=name,
                    subsidy_year=subsidy_year,
                    certified_area=certified_area,
                    subsidy_area=subsidy_area,
                    base_standard=base_standard,
                    rape_area=rape_area,
                    rape_amount=rape_amount,
                    total_amount=total_amount,
                    import_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                )
                session.add(subsidy)
                imported += 1

                if progress_callback:
                    progress_callback(int((idx + 1) / total * 100))
            except Exception as e:
                skipped += 1
                errors.append(f"行{idx + header_row + 3}: {str(e)}")

        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

    return {"imported": imported, "skipped": skipped, "errors": errors, "total": total, "not_found": not_found}


def get_all_land_subsidies(subsidy_year: str = None) -> list:

    session = get_session()
    try:
        query = session.query(LandSubsidy)
        if subsidy_year:
            query = query.filter(LandSubsidy.subsidy_year == subsidy_year)
        return query.order_by(LandSubsidy.name).all()
    finally:
        session.close()


def delete_land_subsidy(subsidy_id: str):

    session = get_session()
    try:
        subsidy = session.query(LandSubsidy).filter(LandSubsidy.id == subsidy_id).first()
        if subsidy:
            session.delete(subsidy)
            session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def get_person_subsidy_total(id_card: str, subsidy_year: str = None) -> str:

    session = get_session()
    try:
        query = session.query(LandSubsidy).filter(LandSubsidy.id_card == id_card)
        if subsidy_year:
            query = query.filter(LandSubsidy.subsidy_year.startswith(subsidy_year))
        subsidies = query.all()
        if not subsidies:
            return ""
        total = 0.0
        for s in subsidies:
            try:
                total += float(s.total_amount)
            except (ValueError, TypeError):
                pass
        return f"{total:.2f}" if total > 0 else ""
    finally:
        session.close()


def get_year_subsidy_totals() -> dict:

    session = get_session()
    try:
        subsidies = session.query(LandSubsidy).all()
        totals = {}
        for s in subsidies:
            year = s.subsidy_year or "未知"
            if year not in totals:
                totals[year] = 0.0
            try:
                totals[year] += float(s.total_amount)
            except (ValueError, TypeError):
                pass
        return totals
    finally:
        session.close()


def import_treatment_payment(file_path: str, progress_callback=None) -> dict:
    """导入待遇发放数据，支持三种表格格式
    
    只导入身份证号在数据库中存在的人员
    """

    df = _read_excel_robust(file_path, header=0)
    df = df.fillna("")

    # 检测表格类型
    columns = list(df.columns)
    file_name = os.path.basename(file_path)

    # 确定姓名和身份证列名
    name_col = None
    id_card_col = None
    amount_col = None

    if "救助类型" in columns and "人员身份证号" in columns:
        name_col = "人员姓名"
        id_card_col = "人员身份证号"
        amount_col = "家庭保障总金额"
    elif "姓名" in columns:
        name_col = "姓名"
        if "公民身份证号码" in columns:
            id_card_col = "公民身份证号码"
        elif "身份证号" in columns:
            id_card_col = "身份证号"
        amount_col = "金额" if "金额" in columns else None

    if not name_col:
        return {"imported": 0, "skipped": 0, "errors": ["未找到姓名列"], "total": 0, "not_found": []}

    total = len(df)
    imported = 0
    skipped = 0
    errors = []
    not_found = []
    session = get_session()

    # 获取数据库中所有身份证号
    existing_id_cards = set()
    try:
        persons = session.query(Person.id_card).all()
        existing_id_cards = {p.id_card for p in persons if p.id_card}
    except Exception:
        pass

    try:
        for idx, row in df.iterrows():
            try:
                name = safe_str(row.get(name_col, ""))
                if not name:
                    skipped += 1
                    continue

                id_card = safe_str(row.get(id_card_col, "")) if id_card_col else ""
                
                # 检查身份证号是否在数据库中存在
                if id_card and id_card not in existing_id_cards:
                    not_found.append(f"{name}({id_card})")
                    skipped += 1
                    continue
                
                amount = safe_str(row.get(amount_col, "")) if amount_col else ""

                # 根据表格类型提取其他字段
                town = safe_str(row.get("所属乡镇", ""))
                village = safe_str(row.get("所属村", ""))
                period = safe_str(row.get("费款所属期", ""))
                payment_status = safe_str(row.get("支付标志", ""))
                personal_code = safe_str(row.get("个人编号", ""))
                bank_account = safe_str(row.get("银行账号", ""))
                fail_reason = safe_str(row.get("失败原因", ""))
                subsidy_type = safe_str(row.get("救助类型", ""))
                relation = safe_str(row.get("和申请人关系", ""))

                payment = TreatmentPayment(
                    id=f"tp_{secrets.token_hex(8)}",
                    name=name,
                    id_card=id_card,
                    town=town,
                    village=village,
                    period=period,
                    payment_status=payment_status,
                    personal_code=personal_code,
                    bank_account=bank_account,
                    amount=amount,
                    subsidy_type=subsidy_type,
                    relation=relation,
                    fail_reason=fail_reason,
                    import_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    import_source=file_name,
                )
                session.add(payment)
                imported += 1

                if progress_callback:
                    progress_callback(int((idx + 1) / total * 100))
            except Exception as e:
                skipped += 1
                errors.append(f"行{idx + 2}: {str(e)}")

        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

    return {"imported": imported, "skipped": skipped, "errors": errors, "total": total, "not_found": not_found}


def get_all_treatment_payments(period: str = None, id_card: str = None, subsidy_type: str = None) -> list:

    session = get_session()
    try:
        query = session.query(TreatmentPayment)
        if period:
            query = query.filter(TreatmentPayment.period == period)
        if id_card:
            query = query.filter(TreatmentPayment.id_card.like(f'%{id_card}%'))
        if subsidy_type:
            query = query.filter(TreatmentPayment.subsidy_type == subsidy_type)
        return query.order_by(TreatmentPayment.period.desc(), TreatmentPayment.name).all()
    finally:
        session.close()


def delete_treatment_payment(payment_id: str):

    session = get_session()
    try:
        payment = session.query(TreatmentPayment).filter(TreatmentPayment.id == payment_id).first()
        if payment:
            session.delete(payment)
            session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def import_pension_insurance(file_path: str, progress_callback=None) -> dict:
    """导入养老保险数据
    
    只导入身份证号在数据库中存在的人员
    """

    df = _read_excel_robust(file_path, header=0)
    df = df.fillna("")

    columns = list(df.columns)
    file_name = os.path.basename(file_path)

    if "姓名" not in columns:
        return {"imported": 0, "skipped": 0, "errors": ["未找到姓名列"], "total": 0, "not_found": []}

    id_card_col = None
    if "公民身份证号码" in columns:
        id_card_col = "公民身份证号码"
    elif "身份证号" in columns:
        id_card_col = "身份证号"
    elif "身份证号码" in columns:
        id_card_col = "身份证号码"

    total = len(df)
    imported = 0
    skipped = 0
    errors = []
    not_found = []
    session = get_session()

    # 获取数据库中所有身份证号
    existing_id_cards = set()
    try:
        persons = session.query(Person.id_card).all()
        existing_id_cards = {p.id_card for p in persons if p.id_card}
    except Exception:
        pass

    try:
        for idx, row in df.iterrows():
            try:
                name = safe_str(row.get("姓名", ""))
                if not name:
                    skipped += 1
                    continue

                id_card = safe_str(row.get(id_card_col, "")) if id_card_col else ""
                
                # 检查身份证号是否在数据库中存在
                if id_card and id_card not in existing_id_cards:
                    not_found.append(f"{name}({id_card})")
                    skipped += 1
                    continue

                pension = PensionInsurance(
                    id=f"pi_{secrets.token_hex(8)}",
                    name=name,
                    id_card=id_card,
                    town=safe_str(row.get("所属乡镇", "")),
                    village=safe_str(row.get("所属村", "")),
                    period=safe_str(row.get("费款所属期", "")),
                    payment_status=safe_str(row.get("支付标志", "")),
                    personal_code=safe_str(row.get("个人编号", "")),
                    person_id=safe_str(row.get("享受定期待遇人员ID", "")),
                    bank_account=safe_str(row.get("银行账号", "")),
                    amount=safe_str(row.get("金额", "")),
                    fail_reason=safe_str(row.get("失败原因", "")),
                    import_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    import_source=file_name,
                )
                session.add(pension)
                imported += 1

                if progress_callback:
                    progress_callback(int((idx + 1) / total * 100))
            except Exception as e:
                skipped += 1
                errors.append(f"行{idx + 2}: {str(e)}")

        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

    return {"imported": imported, "skipped": skipped, "errors": errors, "total": total, "not_found": not_found}


def get_all_pension_insurance(period: str = None, id_card: str = None) -> list:

    session = get_session()
    try:
        query = session.query(PensionInsurance)
        if period:
            query = query.filter(PensionInsurance.period == period)
        if id_card:
            query = query.filter(PensionInsurance.id_card.like(f'%{id_card}%'))
        return query.order_by(PensionInsurance.period.desc(), PensionInsurance.name).all()
    finally:
        session.close()


def delete_pension_insurance(record_id: str):

    session = get_session()
    try:
        record = session.query(PensionInsurance).filter(PensionInsurance.id == record_id).first()
        if record:
            session.delete(record)
            session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
