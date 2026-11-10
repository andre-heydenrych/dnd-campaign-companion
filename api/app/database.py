import os
from pathlib import Path

from sqlmodel import Session, create_engine

# The one place the database location is set. The app and Alembic both read it.
# Defaults to api/dnd.db, whichever folder you run commands from;
# set the DATABASE_URL environment variable to use another database.
API_DIR = Path(__file__).resolve().parent.parent
DATABASE_URL = os.environ.get("DATABASE_URL", f"sqlite:///{(API_DIR / 'dnd.db').as_posix()}")

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args)

def get_session():
    with Session(engine) as session:
        yield session