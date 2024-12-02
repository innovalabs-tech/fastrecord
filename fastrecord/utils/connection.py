from typing import Optional
from sqlmodel import create_engine, SQLModel, Session
from sqlalchemy.engine import Engine

_engine: Optional[Engine] = None


def get_engine() -> Engine:
    """Get the SQLAlchemy engine instance"""
    global _engine
    if _engine is None:
        raise RuntimeError("Database not configured. Call setup_database first.")
    return _engine


def setup_database(url: str, **kwargs):
    """Configure the database connection"""
    global _engine
    _engine = create_engine(url, **kwargs)

    # Create all tables
    SQLModel.metadata.create_all(_engine)
