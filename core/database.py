from sqlalchemy import create_engine, Column, String, Index, event
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from core.config import DB_PATH
import os
import hashlib

import secrets

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


class Person(Base):
    __tablename__ = "persons"

    id = Column(String, primary_key=True)
    hu_hao = Column(String, nullable=False, index=True)
    id_card = Column(String, nullable=False, index=True)
    name = Column(String, nullable=False, index=True)
    age = Column(String, default="")
    address = Column(String, default="")
    relation = Column(String, default="")
    is_dead = Column(String, default="否")
    phone = Column(String, default="")
    remark = Column(String, default="")
    poor_type = Column(String, default="")
    disability = Column(String, default="")
    disability_type = Column(String, default="")
    dis_level = Column(String, default="")
    dibao = Column(String, default="")
    jisheng = Column(String, default="")
    social_card1 = Column(String, default="")
    social_card2 = Column(String, default="")
    social_card3 = Column(String, default="")
    is_migrated = Column(String, default="否")
    migration_date = Column(String, default="")
    migration_place = Column(String, default="")
    migration_reason = Column(String, default="")
    updated_at = Column(String, default="")
    land_area = Column(String, default="")
    land_area_change_reason = Column(String, default="")
    land_area_change_time = Column(String, default="")
    tekun = Column(String, default="")
    tekun_type = Column(String, default="")

    __table_args__ = (
        Index("idx_name_hu_hao", "name", "hu_hao"),
    )


class StudentEducation(Base):
    __tablename__ = "student_education"

    id = Column(String, primary_key=True)
    person_id = Column(String, nullable=False, index=True)
    id_card = Column(String, nullable=False, index=True)
    school_name = Column(String, default="")
    grade = Column(String, default="")
    class_name = Column(String, default="")
    guardian = Column(String, default="")
    guardian_phone = Column(String, default="")
    is_left_behind = Column(String, default="否")
    student_status = Column(String, default="")
    enrollment_date = Column(String, default="")
    graduation_date = Column(String, default="")


class LandSubsidy(Base):
    __tablename__ = "land_subsidy"

    id = Column(String, primary_key=True)
    person_id = Column(String, default="")
    id_card = Column(String, nullable=False, index=True)
    name = Column(String, nullable=False, index=True)
    subsidy_year = Column(String, default="")
    certified_area = Column(String, default="")
    subsidy_area = Column(String, default="")
    base_standard = Column(String, default="")
    rape_area = Column(String, default="")
    rape_amount = Column(String, default="")
    total_amount = Column(String, default="")
    import_time = Column(String, default="")


class TreatmentPayment(Base):
    __tablename__ = "treatment_payment"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False, index=True)
    id_card = Column(String, default="", index=True)
    town = Column(String, default="")  # 所属乡镇
    village = Column(String, default="")  # 所属村
    period = Column(String, default="", index=True)  # 费款所属期/年月
    payment_status = Column(String, default="")  # 支付标志
    personal_code = Column(String, default="")  # 个人编号
    bank_account = Column(String, default="")
    amount = Column(String, default="")
    subsidy_type = Column(String, default="")  # 救助类型(低保/特困等)
    relation = Column(String, default="")  # 和申请人关系
    fail_reason = Column(String, default="")  # 失败原因
    import_time = Column(String, default="")
    import_source = Column(String, default="")  # 导入来源文件名


class PensionInsurance(Base):
    __tablename__ = "pension_insurance"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False, index=True)
    id_card = Column(String, default="", index=True)
    town = Column(String, default="")  # 所属乡镇
    village = Column(String, default="")  # 所属村
    period = Column(String, default="", index=True)  # 费款所属期/年月
    payment_status = Column(String, default="")  # 支付标志
    personal_code = Column(String, default="")  # 个人编号
    person_id = Column(String, default="")  # 享受定期待遇人员ID
    bank_account = Column(String, default="")
    amount = Column(String, default="")
    fail_reason = Column(String, default="")  # 失败原因
    import_time = Column(String, default="")
    import_source = Column(String, default="")  # 导入来源文件名


class EducationHistory(Base):
    __tablename__ = "education_history"

    id = Column(String, primary_key=True)
    person_id = Column(String, nullable=False, index=True)
    id_card = Column(String, nullable=False)
    school_name = Column(String, default="")
    grade = Column(String, default="")
    class_name = Column(String, default="")
    student_status = Column(String, default="")
    change_date = Column(String, default="")
    change_reason = Column(String, default="")


class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True)
    username = Column(String, nullable=False, unique=True, index=True)
    password_hash = Column(String, nullable=False)
    real_name = Column(String, default="")
    role = Column(String, default="user")
    is_active = Column(String, default="是")
    is_default = Column(String, default="否")
    created_at = Column(String, default="")
    last_login = Column(String, default="")
    login_attempts = Column(String, default="0")
    locked_until = Column(String, default="")


class OperationLog(Base):
    __tablename__ = "operation_logs"

    id = Column(String, primary_key=True)
    user_id = Column(String, nullable=False, index=True)
    username = Column(String, nullable=False)
    operation_type = Column(String, nullable=False)
    operation_target = Column(String, default="")
    ip_address = Column(String, default="")
    client_type = Column(String, default="")
    created_at = Column(String, nullable=False)
    is_high_risk = Column(String, default="否")


class DeletedPerson(Base):
    __tablename__ = "deleted_persons"

    id = Column(String, primary_key=True)
    original_id = Column(String, nullable=False)
    hu_hao = Column(String, nullable=False)
    id_card = Column(String, nullable=False)
    name = Column(String, nullable=False)
    age = Column(String, default="")
    address = Column(String, default="")
    relation = Column(String, default="")
    is_dead = Column(String, default="否")
    phone = Column(String, default="")
    remark = Column(String, default="")
    poor_type = Column(String, default="")
    disability = Column(String, default="")
    disability_type = Column(String, default="")
    dis_level = Column(String, default="")
    dibao = Column(String, default="")
    jisheng = Column(String, default="")
    social_card1 = Column(String, default="")
    social_card2 = Column(String, default="")
    social_card3 = Column(String, default="")
    tekun = Column(String, default="")
    tekun_type = Column(String, default="")
    is_migrated = Column(String, default="否")
    migration_date = Column(String, default="")
    migration_place = Column(String, default="")
    migration_reason = Column(String, default="")
    deleted_at = Column(String, nullable=False)


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
        # treatment_payment 表新增字段
        try:
            conn.execute(text("ALTER TABLE treatment_payment ADD COLUMN id_card VARCHAR DEFAULT ''"))
            conn.commit()
        except Exception:
            pass
        try:
            conn.execute(text("ALTER TABLE treatment_payment ADD COLUMN town VARCHAR DEFAULT ''"))
            conn.commit()
        except Exception:
            pass
        try:
            conn.execute(text("ALTER TABLE treatment_payment ADD COLUMN village VARCHAR DEFAULT ''"))
            conn.commit()
        except Exception:
            pass
        try:
            conn.execute(text("ALTER TABLE treatment_payment ADD COLUMN period VARCHAR DEFAULT ''"))
            conn.commit()
        except Exception:
            pass
        try:
            conn.execute(text("ALTER TABLE treatment_payment ADD COLUMN payment_status VARCHAR DEFAULT ''"))
            conn.commit()
        except Exception:
            pass
        try:
            conn.execute(text("ALTER TABLE treatment_payment ADD COLUMN personal_code VARCHAR DEFAULT ''"))
            conn.commit()
        except Exception:
            pass
        try:
            conn.execute(text("ALTER TABLE treatment_payment ADD COLUMN subsidy_type VARCHAR DEFAULT ''"))
            conn.commit()
        except Exception:
            pass
        try:
            conn.execute(text("ALTER TABLE treatment_payment ADD COLUMN relation VARCHAR DEFAULT ''"))
            conn.commit()
        except Exception:
            pass
        try:
            conn.execute(text("ALTER TABLE treatment_payment ADD COLUMN fail_reason VARCHAR DEFAULT ''"))
            conn.commit()
        except Exception:
            pass
        try:
            conn.execute(text("ALTER TABLE treatment_payment ADD COLUMN import_source VARCHAR DEFAULT ''"))
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


def validate_password(password: str) -> tuple[bool, str]:
    if len(password) < 8:
        return False, "密码长度至少8位"
    if not any(c.isalpha() for c in password):
        return False, "密码必须包含字母"
    if not any(c.isdigit() for c in password):
        return False, "密码必须包含数字"
    return True, ""


def create_user(username: str, password: str, real_name: str = "", role: str = "user") -> User:
    from datetime import datetime
    valid, msg = validate_password(password)
    if not valid:
        raise ValueError(msg)
    session = get_session()
    try:
        existing = session.query(User).filter(User.username == username).first()
        if existing:
            raise ValueError("用户名已存在")
        salt = secrets.token_hex(16)
        password_hash = hashlib.sha256((salt + password).encode()).hexdigest()
        user = User(
            id=f"user_{secrets.token_hex(8)}",
            username=username,
            password_hash=f"{salt}:{password_hash}",
            real_name=real_name,
            role=role,
            created_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
        session.add(user)
        session.commit()
        return user
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def authenticate_user(username: str, password: str, ip_address: str = "", client_type: str = "") -> User | None:
    from datetime import datetime, timedelta
    session = get_session()
    try:
        user = session.query(User).filter(User.username == username, User.is_active == "是").first()
        if not user:
            return None
        if user.locked_until:
            try:
                lock_time = datetime.strptime(user.locked_until, "%Y-%m-%d %H:%M:%S")
                if datetime.now() < lock_time:
                    return None
                user.locked_until = ""
                user.login_attempts = "0"
            except Exception:
                user.locked_until = ""
                user.login_attempts = "0"
        salt, stored_hash = user.password_hash.split(":")
        password_hash = hashlib.sha256((salt + password).encode()).hexdigest()
        if password_hash != stored_hash:
            attempts = int(user.login_attempts or "0") + 1
            user.login_attempts = str(attempts)
            if attempts >= 5:
                user.locked_until = (datetime.now() + timedelta(minutes=15)).strftime("%Y-%m-%d %H:%M:%S")
            session.commit()
            return None
        user.login_attempts = "0"
        user.locked_until = ""
        user.last_login = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        session.commit()
        result = type('UserResult', (), {
            'id': user.id, 'username': user.username, 'real_name': user.real_name,
            'role': user.role, 'is_active': user.is_active
        })()
        return result
    finally:
        session.close()


def add_operation_log(user_id: str, username: str, operation_type: str, operation_target: str = "", ip_address: str = "", client_type: str = "", is_high_risk: str = "否"):
    from datetime import datetime
    session = get_session()
    try:
        log = OperationLog(
            id=f"log_{secrets.token_hex(8)}",
            user_id=user_id,
            username=username,
            operation_type=operation_type,
            operation_target=operation_target,
            ip_address=ip_address,
            client_type=client_type,
            created_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            is_high_risk=is_high_risk
        )
        session.add(log)
        session.commit()
    except Exception:
        session.rollback()
    finally:
        session.close()


def get_operation_logs(limit: int = 100) -> list:
    session = get_session()
    try:
        return session.query(OperationLog).order_by(OperationLog.created_at.desc()).limit(limit).all()
    finally:
        session.close()


def get_all_users() -> list:
    session = get_session()
    try:
        return session.query(User).all()
    finally:
        session.close()


def delete_user(user_id: str):
    session = get_session()
    try:
        user = session.query(User).filter(User.id == user_id).first()
        if user:
            session.delete(user)
            session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def update_user(user_id: str, **kwargs):
    session = get_session()
    try:
        user = session.query(User).filter(User.id == user_id).first()
        if user:
            for key, value in kwargs.items():
                if hasattr(user, key):
                    setattr(user, key, value)
            session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def change_user_password(user_id: str, old_password: str, new_password: str) -> tuple[bool, str]:
    valid, msg = validate_password(new_password)
    if not valid:
        return False, msg
    session = get_session()
    try:
        user = session.query(User).filter(User.id == user_id).first()
        if not user:
            return False, "用户不存在"
        salt, stored_hash = user.password_hash.split(":")
        if hashlib.sha256((salt + old_password).encode()).hexdigest() != stored_hash:
            return False, "原密码错误"
        new_salt = secrets.token_hex(16)
        new_hash = hashlib.sha256((new_salt + new_password).encode()).hexdigest()
        user.password_hash = f"{new_salt}:{new_hash}"
        session.commit()
        return True, ""
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def search_by_name(name: str) -> list[Person]:
    session = get_session()
    try:
        return session.query(Person).filter(Person.name.like(f"%{name}%")).all()
    finally:
        session.close()


def get_family_members(hu_hao: str) -> list[Person]:
    session = get_session()
    try:
        return session.query(Person).filter(Person.hu_hao == hu_hao).all()
    finally:
        session.close()


def add_person(person: Person):
    session = get_session()
    try:
        session.add(person)
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def update_person(person: Person):
    from datetime import datetime
    session = get_session()
    try:
        person.updated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        session.merge(person)
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def get_person_count() -> int:
    session = get_session()
    try:
        return session.query(Person).count()
    finally:
        session.close()


def generate_new_hu_hao() -> str:
    session = get_session()
    try:
        persons = session.query(Person).all()
        max_num = 0
        for p in persons:
            try:
                num = int(p.hu_hao)
                if num > max_num:
                    max_num = num
            except (ValueError, TypeError):
                pass
        return str(max_num + 1)
    finally:
        session.close()


def split_household(person_ids: list, new_hu_hao: str = None) -> str:
    if not person_ids:
        raise ValueError("请选择要分户的人员")
    if not new_hu_hao:
        new_hu_hao = generate_new_hu_hao()
    session = get_session()
    try:
        for pid in person_ids:
            p = session.query(Person).filter(Person.id == pid).first()
            if p:
                p.hu_hao = new_hu_hao
                p.relation = "户主"
                from datetime import datetime
                p.updated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        session.commit()
        return new_hu_hao
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def merge_household(target_hu_hao: str, person_ids: list):
    if not person_ids:
        raise ValueError("请选择要合户的人员")
    session = get_session()
    try:
        for pid in person_ids:
            p = session.query(Person).filter(Person.id == pid).first()
            if p:
                p.hu_hao = target_hu_hao
                from datetime import datetime
                p.updated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def add_new_household(hu_hao: str, name: str, id_card: str, relation: str = "户主", **kwargs) -> Person:
    session = get_session()
    try:
        existing = session.query(Person).filter(Person.hu_hao == hu_hao).first()
        if existing:
            raise ValueError(f"户号 {hu_hao} 已存在")
        from core.utils import calculate_age
        person = Person(
            id=f"p_{hu_hao}_{id_card}",
            hu_hao=hu_hao,
            id_card=id_card,
            name=name,
            age=calculate_age(id_card),
            relation=relation,
            address=kwargs.get("address", ""),
            phone=kwargs.get("phone", ""),
            land_area=kwargs.get("land_area", ""),
        )
        session.add(person)
        session.commit()
        return person
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def migrate_person(person_id: str, migration_date: str, migration_place: str, migration_reason: str):
    session = get_session()
    try:
        person = session.query(Person).filter(Person.id == person_id).first()
        if person:
            person.is_migrated = "是"
            person.migration_date = migration_date
            person.migration_place = migration_place
            person.migration_reason = migration_reason
            session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def delete_person(person_id: str):
    from datetime import datetime
    import uuid
    session = get_session()
    try:
        person = session.query(Person).filter(Person.id == person_id).first()
        if person:
            deleted = DeletedPerson(
                id=f"del_{uuid.uuid4().hex[:8]}",
                original_id=person.id,
                hu_hao=person.hu_hao,
                id_card=person.id_card,
                name=person.name,
                age=person.age,
                address=person.address,
                relation=person.relation,
                is_dead=person.is_dead,
                phone=person.phone,
                remark=person.remark,
                poor_type=person.poor_type,
                disability=person.disability,
                dis_level=person.dis_level,
                dibao=person.dibao,
                jisheng=person.jisheng,
                social_card1=person.social_card1,
                social_card2=person.social_card2,
                social_card3=person.social_card3,
                tekun=person.tekun,
                tekun_type=person.tekun_type,
                is_migrated=person.is_migrated,
                migration_date=person.migration_date,
                migration_place=person.migration_place,
                migration_reason=person.migration_reason,
                deleted_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            )
            session.add(deleted)
            session.delete(person)
            session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def recover_person(deleted_id: str):
    session = get_session()
    try:
        deleted = session.query(DeletedPerson).filter(DeletedPerson.id == deleted_id).first()
        if deleted:
            person = Person(
                id=deleted.original_id,
                hu_hao=deleted.hu_hao,
                id_card=deleted.id_card,
                name=deleted.name,
                age=deleted.age,
                address=deleted.address,
                relation=deleted.relation,
                is_dead=deleted.is_dead,
                phone=deleted.phone,
                remark=deleted.remark,
                poor_type=deleted.poor_type,
                disability=deleted.disability,
                dis_level=deleted.dis_level,
                dibao=deleted.dibao,
                jisheng=deleted.jisheng,
                social_card1=deleted.social_card1,
                social_card2=deleted.social_card2,
                social_card3=deleted.social_card3,
                tekun=deleted.tekun,
                tekun_type=deleted.tekun_type,
                is_migrated=deleted.is_migrated,
                migration_date=deleted.migration_date,
                migration_place=deleted.migration_place,
                migration_reason=deleted.migration_reason
            )
            session.add(person)
            session.delete(deleted)
            session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def get_deleted_persons() -> list:
    session = get_session()
    try:
        return session.query(DeletedPerson).all()
    finally:
        session.close()


def get_student_education(person_id: str) -> 'StudentEducation | None':
    session = get_session()
    try:
        return session.query(StudentEducation).filter(StudentEducation.person_id == person_id).first()
    finally:
        session.close()


def save_student_education(education: StudentEducation):
    session = get_session()
    try:
        existing = session.query(StudentEducation).filter(
            StudentEducation.person_id == education.person_id
        ).first()
        if existing:
            changed = (
                existing.school_name != education.school_name or
                existing.grade != education.grade or
                existing.class_name != education.class_name or
                existing.student_status != education.student_status
            )
            if changed:
                from datetime import datetime
                import uuid
                history = EducationHistory(
                    id=str(uuid.uuid4()),
                    person_id=education.person_id,
                    id_card=existing.id_card,
                    school_name=existing.school_name,
                    grade=existing.grade,
                    class_name=existing.class_name,
                    student_status=existing.student_status,
                    change_date=datetime.now().strftime("%Y-%m-%d"),
                    change_reason="编辑更新"
                )
                session.add(history)
            existing.school_name = education.school_name
            existing.grade = education.grade
            existing.class_name = education.class_name
            existing.guardian = education.guardian
            existing.guardian_phone = education.guardian_phone
            existing.is_left_behind = education.is_left_behind
            existing.student_status = education.student_status
            existing.enrollment_date = education.enrollment_date
        else:
            session.add(education)
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def delete_student_education(person_id: str):
    session = get_session()
    try:
        edu = session.query(StudentEducation).filter(StudentEducation.person_id == person_id).first()
        if edu:
            session.delete(edu)
            session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def get_education_history(person_id: str) -> list:
    session = get_session()
    try:
        return session.query(EducationHistory).filter(
            EducationHistory.person_id == person_id
        ).order_by(EducationHistory.change_date.desc()).all()
    finally:
        session.close()


def get_all_students() -> list:
    session = get_session()
    try:
        return session.query(StudentEducation).filter(
            StudentEducation.student_status.in_(["在读", "留级", "跳级"])
        ).all()
    finally:
        session.close()


def search_students(school: str = None, grade: str = None, class_name: str = None, is_left_behind: str = None) -> list:
    session = get_session()
    try:
        q = session.query(StudentEducation)
        if school:
            q = q.filter(StudentEducation.school_name == school)
        if grade:
            q = q.filter(StudentEducation.grade == grade)
        if class_name:
            q = q.filter(StudentEducation.class_name == class_name)
        if is_left_behind:
            q = q.filter(StudentEducation.is_left_behind == is_left_behind)
        return q.all()
    finally:
        session.close()


def batch_update_school(person_ids: list, school_name: str):
    session = get_session()
    try:
        for pid in person_ids:
            edu = session.query(StudentEducation).filter(StudentEducation.person_id == pid).first()
            if edu:
                edu.school_name = school_name
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def batch_set_left_behind(person_ids: list, is_left_behind: str):
    session = get_session()
    try:
        for pid in person_ids:
            edu = session.query(StudentEducation).filter(StudentEducation.person_id == pid).first()
            if edu:
                edu.is_left_behind = is_left_behind
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def promote_all_grades():
    from core.config import GRADE_PROMOTION_MAP, GRADUATION_GRADES, BLOCKED_PROMOTION_STATUSES
    from datetime import datetime
    session = get_session()
    try:
        students = session.query(StudentEducation).filter(
            StudentEducation.student_status.in_(["在读", "跳级"])
        ).all()
        count = 0
        for s in students:
            if s.student_status in BLOCKED_PROMOTION_STATUSES:
                continue
            new_grade = GRADE_PROMOTION_MAP.get(s.grade)
            if new_grade:
                history = EducationHistory(
                    id=f"hist_{datetime.now().strftime('%Y%m%d%H%M%S')}_{s.person_id}",
                    person_id=s.person_id,
                    id_card=s.id_card,
                    school_name=s.school_name,
                    grade=s.grade,
                    class_name=s.class_name,
                    student_status=s.student_status,
                    change_date=datetime.now().strftime("%Y-%m-%d"),
                    change_reason="自动升年级"
                )
                session.add(history)
                s.grade = new_grade
                if new_grade == "GRADUATED" or new_grade in GRADUATION_GRADES:
                    s.student_status = "毕业"
                count += 1
        session.commit()
        return count
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
