"""FastRecord - A Rails-like ORM for FastAPI using SQLModel."""

from .base import FastRecord
from sqlmodel import Field, SQLModel

__version__ = "0.1.0"
__all__ = ["FastRecord", "Field", "SQLModel"]
