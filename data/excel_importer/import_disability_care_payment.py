import os
import secrets
from datetime import datetime

from core.database import get_session, Person, DisabilityCarePayment
from core.utils import safe_str
from ._read_excel_robust import _read_excel_robust
from ._backfill_social_card import _backfill_social_card


def import_disability_care_payment(file_path: str, progress_callback=None) -> dict:
    """导入残疾人护理补贴数据（本地模式），只导入身份证号在数据库中存在的人员"""

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

    existing_id_cards = set()
    person_map = {}
    try:
        persons = session.query(Person).all()
        existing_id_cards = {p.id_card for p in persons if p.id_card}
        person_map = {p.id_card: p for p in persons if p.id_card}
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

                if id_card and id_card not in existing_id_cards:
                    not_found.append(f"{name}({id_card})")
                    skipped += 1
                    continue

                amount = safe_str(row.get("金额", "")) if "金额" in columns else ""

                period = safe_str(row.get("费款所属期", ""))
                if id_card and period:
                    card = safe_str(row.get("卡号", "")).strip()
                    person = person_map.get(id_card)
                    if person and card:
                        _backfill_social_card(person, "残疾人护理补贴" + period, card)

                record = DisabilityCarePayment(
                    id=f"dcp_{secrets.token_hex(8)}",
                    name=name,
                    id_card=id_card,
                    town=safe_str(row.get("所属乡镇", "")),
                    village=safe_str(row.get("所属村", "")),
                    period=safe_str(row.get("费款所属期", "")),
                    payment_status=safe_str(row.get("支付标志", "")),
                    personal_code=safe_str(row.get("个人编号", "")),
                    bank_account=safe_str(row.get("银行账号", "")),
                    amount=amount,
                    relation=safe_str(row.get("和申请人关系", "")),
                    fail_reason=safe_str(row.get("失败原因", "")),
                    import_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    import_source=file_name,
                )
                session.add(record)
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
