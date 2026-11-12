import os
from pathlib import Path

from sqlalchemy import Engine, event
from sqlmodel import Session, create_engine

# The one place the database location is set. The app and Alembic both read it.
# Defaults to api/dnd.db, whichever folder you run commands from;
# set the DATABASE_URL environment variable to use another database.
API_DIR = Path(__file__).resolve().parent.parent
DATABASE_URL = os.environ.get("DATABASE_URL", f"sqlite:///{(API_DIR / 'dnd.db').as_posix()}")


def create_db_engine(url: str, **kwargs) -> Engine:
    """Create an engine. For SQLite, foreign keys are switched on for every connection.

    SQLite ignores FOREIGN KEY constraints unless each connection runs
    `PRAGMA foreign_keys = ON`, so a "connect" event does that whenever the
    engine opens a new connection. The app, the seed script and the tests all
    build their engine here, so they all get it.
    """
    if url.startswith("sqlite"):
        kwargs.setdefault("connect_args", {"check_same_thread": False})
    db_engine = create_engine(url, **kwargs)

    if db_engine.dialect.name == "sqlite":
        @event.listens_for(db_engine, "connect")
        def _enable_sqlite_foreign_keys(dbapi_connection, connection_record):
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys = ON")
            cursor.close()

    return db_engine


engine = create_db_engine(DATABASE_URL)


def get_session():
    with Session(engine) as session:
        yield session
