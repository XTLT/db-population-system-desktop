"""创建（或复用）SQLite engine，并设置 WAL / synchronous 参数。"""

from sqlalchemy import create_engine, event


def get_engine():
    from .. import _base

    if _base._engine is None:
        engine = create_engine(f"sqlite:///{_base.DB_PATH}", echo=False)

        @event.listens_for(engine, "connect")
        def set_sqlite_pragma(dbapi_connection, _connection_record):
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA journal_mode=WAL")
            cursor.execute("PRAGMA synchronous=NORMAL")
            cursor.close()

        _base._engine = engine
    return _base._engine
