"""本地 SQLite 数据访问层（拆分后的同名包，行为与原 core/database.py 一致）。"""

from ._base import (
    SERVICE_NAME,
    Base,
    _db_password,
    _engine,
    _SessionFactory,
    set_db_password,
    get_db_password,
    _derive_key,
    encrypt_database,
    decrypt_database,
    is_database_encrypted,
    get_engine,
    reset_engine,
    get_session,
    init_db,
    _migrate_db,
)

# 先导入全部模型，Base.metadata 才完整
from .models.person import Person
from .models.student_education import StudentEducation
from .models.land_subsidy import LandSubsidy
from .models.pension_insurance import PensionInsurance
from .models.dibao_payment import DibaoPayment
from .models.tekun_payment import TekunPayment
from .models.disability_care_payment import DisabilityCarePayment
from .models.elderly_allowance import ElderlyAllowance
from .models.education_history import EducationHistory
from .models.user import User
from .models.operation_log import OperationLog
from .models.deleted_person import DeletedPerson

from .functions.validate_password import validate_password
from .functions.create_user import create_user
from .functions.authenticate_user import authenticate_user
from .functions.add_operation_log import add_operation_log
from .functions.get_operation_logs import get_operation_logs
from .functions.get_all_users import get_all_users
from .functions.delete_user import delete_user
from .functions.update_user import update_user
from .functions.change_user_password import change_user_password
from .functions.search_by_name import search_by_name
from .functions.get_family_members import get_family_members
from .functions.add_person import add_person
from .functions.update_person import update_person
from .functions.get_person_count import get_person_count
from .functions.generate_new_hu_hao import generate_new_hu_hao
from .functions.split_household import split_household
from .functions.merge_household import merge_household
from .functions.add_new_household import add_new_household
from .functions.migrate_person import migrate_person
from .functions.delete_person import delete_person
from .functions.recover_person import recover_person
from .functions.get_deleted_persons import get_deleted_persons
from .functions.get_student_education import get_student_education
from .functions.save_student_education import save_student_education
from .functions.delete_student_education import delete_student_education
from .functions.get_education_history import get_education_history
from .functions.get_all_students import get_all_students
from .functions.search_students import search_students
from .functions.batch_update_school import batch_update_school
from .functions.batch_set_left_behind import batch_set_left_behind
from .functions.promote_all_grades import promote_all_grades

__all__ = [
    "SERVICE_NAME",
    "Base",
    "_db_password",
    "_engine",
    "_SessionFactory",
    "set_db_password",
    "get_db_password",
    "_derive_key",
    "encrypt_database",
    "decrypt_database",
    "is_database_encrypted",
    "get_engine",
    "reset_engine",
    "get_session",
    "init_db",
    "_migrate_db",
    "Person",
    "StudentEducation",
    "LandSubsidy",
    "PensionInsurance",
    "DibaoPayment",
    "TekunPayment",
    "DisabilityCarePayment",
    "ElderlyAllowance",
    "EducationHistory",
    "User",
    "OperationLog",
    "DeletedPerson",
    "validate_password",
    "create_user",
    "authenticate_user",
    "add_operation_log",
    "get_operation_logs",
    "get_all_users",
    "delete_user",
    "update_user",
    "change_user_password",
    "search_by_name",
    "get_family_members",
    "add_person",
    "update_person",
    "get_person_count",
    "generate_new_hu_hao",
    "split_household",
    "merge_household",
    "add_new_household",
    "migrate_person",
    "delete_person",
    "recover_person",
    "get_deleted_persons",
    "get_student_education",
    "save_student_education",
    "delete_student_education",
    "get_education_history",
    "get_all_students",
    "search_students",
    "batch_update_school",
    "batch_set_left_behind",
    "promote_all_grades",
]
