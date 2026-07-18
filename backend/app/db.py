"""SQLAlchemy engine, session factory, and database helpers."""

from collections.abc import Generator

from sqlalchemy import create_engine, text
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import get_settings

settings = get_settings()
database_url = settings.resolved_database_url

connect_args = {"check_same_thread": False} if database_url.startswith("sqlite") else {}
engine_kwargs: dict = {"connect_args": connect_args}

if database_url.startswith("postgresql"):
    engine_kwargs.update(
        {
            "pool_pre_ping": True,
            "pool_size": 5,
            "max_overflow": 10,
        }
    )

engine = create_engine(database_url, **engine_kwargs)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    """Declarative base for all ORM models."""

    pass


def get_db() -> Generator[Session, None, None]:
    """Yield a database session for FastAPI dependency injection."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def check_db_connection() -> bool:
    """Return True if the configured database accepts a connection."""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception:
        return False


def init_db() -> None:
    """Create SQLite test/dev tables; Postgres is managed by Supabase migrations."""
    from app import models  # noqa: F401

    if database_url.startswith("sqlite"):
        Base.metadata.create_all(bind=engine)
    elif not check_db_connection():
        raise RuntimeError("Could not connect to configured Postgres database")
