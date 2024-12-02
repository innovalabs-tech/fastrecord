from fastapi import Request
from typing import Optional
from sqlmodel import Session
from starlette.middleware.base import BaseHTTPMiddleware
from contextvars import ContextVar
from ..utils.connection import get_engine

session_context: ContextVar[Optional[Session]] = ContextVar('session', default=None)


class DatabaseMiddleware(BaseHTTPMiddleware):
    """
    Middleware that handles database sessions and transactions
    Similar to Rails' ActiveRecord::ConnectionHandling
    """

    async def dispatch(self, request: Request, call_next):
        # Create new session for each request
        session = Session(get_engine())
        token = session_context.set(session)

        try:
            # Start transaction
            response = await call_next(request)

            # Commit on successful response
            if response.status_code < 400:
                session.commit()
            else:
                session.rollback()

            return response

        except Exception as e:
            # Rollback on exception
            session.rollback()
            raise

        finally:
            # Clean up session
            session.close()
            session_context.reset(token)
