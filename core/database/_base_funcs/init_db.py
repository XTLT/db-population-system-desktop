"""建表并执行列迁移。"""

from .get_engine import get_engine
from .migrate_db import migrate_db


def init_db():
    from .._base import Base

    engine = get_engine()
    Base.metadata.create_all(engine)
    migrate_db(engine)
