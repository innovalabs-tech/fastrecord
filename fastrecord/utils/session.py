from sqlmodel import Session

from ..middleware.database import session_context


def get_session() -> Session:
    session = session_context.get()
    if session is None:
        raise RuntimeError("Database session not available")
    return session
