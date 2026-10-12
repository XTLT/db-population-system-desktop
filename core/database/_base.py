import hashlib
import os
import secrets

from sqlalchemy import create_engine, event
from sqlalchemy.orm import declarative_base, sessionmaker, Session

from core.config import DB_PATH

SERVICE_NAME = "population-query-system"

Base = declarative_base()

_db_password = None


def set_db_password(password: str):
    global _db_password
    _db_password = password
    try:
        import keyring
        keyring.set_password(SERVICE_NAME, "db_password", password)
    except Exception:
        pass


def get_db_password() -> str:
    global _db_password
    if _db_password:
        return _db_password
    try:
        import keyring
        pw = keyring.get_password(SERVICE_NAME, "db_password")
        if pw:
            _db_password = pw
            return pw
    except Exception:
        pass
    return ""


def _derive_key(password: str, salt: bytes) -> bytes:
    return hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 310000)


def encrypt_database(password: str):
    if not os.path.exists(DB_PATH):
        return
    import sqlite3
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.execute("PRAGMA wal_checkpoint(TRUNCATE)")
        conn.close()
    except Exception:
        pass
    salt = secrets.token_bytes(32)
    key = _derive_key(password, salt)
    with open(DB_PATH, 'rb') as f:
        data = f.read()

    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    nonce = secrets.token_bytes(12)
    aesgcm = AESGCM(key)
    encrypted = aesgcm.encrypt(nonce, data, None)

    with open(DB_PATH + '.enc', 'wb') as f:
        f.write(salt + nonce + encrypted)

    os.remove(DB_PATH)
    for ext in ['-wal', '-shm']:
        p = DB_PATH + ext
        if os.path.exists(p):
            os.remove(p)

    key_path = DB_PATH + '.key'
    if os.path.exists(key_path):
        os.remove(key_path)


def decrypt_database(password: str) -> bool:
    enc_path = DB_PATH + '.enc'
    if not os.path.exists(enc_path):
        return True
    try:
        with open(enc_path, 'rb') as f:
            content = f.read()

        if len(content) < 44:
            return False

        salt = content[:32]
        nonce = content[32:44]
        encrypted = content[44:]

        key = _derive_key(password, salt)

        from cryptography.hazmat.primitives.ciphers.aead import AESGCM
        aesgcm = AESGCM(key)
        data = aesgcm.decrypt(nonce, encrypted, None)

        with open(DB_PATH, 'wb') as f:
            f.write(data)
        return True
    except Exception:
        return False


def is_database_encrypted() -> bool:
    return os.path.exists(DB_PATH + '.enc')


_engine = None
_SessionFactory = None


def get_engine():
    global _engine
    if _engine is None:
        _engine = create_engine(f"sqlite:///{DB_PATH}", echo=False)

        @event.listens_for(_engine, "connect")
        def set_sqlite_pragma(dbapi_connection, _connection_record):
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA journal_mode=WAL")
            cursor.execute("PRAGMA synchronous=NORMAL")
            cursor.close()
    return _engine


def reset_engine():
    global _engine, _SessionFactory
    if _engine is not None:
        _engine.dispose()
    _engine = None
    _SessionFactory = None


def get_session() -> Session:
    global _SessionFactory
    if _SessionFactory is None:
        _SessionFactory = sessionmaker(bind=get_engine())
    return _SessionFactory()


def init_db():
    engine = get_engine()
    Base.metadata.create_all(engine)
    _migrate_db(engine)


def _migrate_db(engine):
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
