from .utils import setup_database

from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field, field_validator
from typing import Literal
from functools import lru_cache

class FastRecordSettings(BaseSettings):
    # Database settings
    DATABASE_URL: str = Field(
        default="sqlite:///./test.db",
        description="Database connection URL"
    )
    DATABASE_ECHO: bool = Field(
        default=False,
        description="Enable SQL query logging"
    )
    DATABASE_POOL_SIZE: int = Field(
        default=5,
        ge=1,
        le=100,
        description="Database connection pool size"
    )
    DATABASE_MAX_OVERFLOW: int = Field(
        default=10,
        ge=0,
        le=100,
        description="Maximum overflow connections"
    )
    DATABASE_POOL_TIMEOUT: int = Field(
        default=30,
        ge=1,
        le=300,
        description="Connection pool timeout in seconds"
    )

    # Cache settings
    CACHE_ENABLED: bool = Field(
        default=False,
        description="Enable caching"
    )
    CACHE_TYPE: Literal["memory", "redis"] = Field(
        default="memory",
        description="Cache backend type"
    )
    CACHE_REDIS_URL: str = Field(
        default="redis://localhost:6379/0",
        description="Redis connection URL"
    )
    CACHE_DEFAULT_TTL: int = Field(
        default=1800,
        ge=0,
        le=86400,
        description="Default TTL in seconds"
    )
    CACHE_PREFIX: str = Field(
        default="fastrecord",
        min_length=1,
        description="Cache key prefix"
    )
    CACHE_VERSION: str = Field(
        default="1.0",
        pattern=r"^\d+\.\d+$",
        description="Cache version"
    )

    # Query settings
    MAX_EAGER_LOAD_RELATIONS: int = Field(
        default=10,
        ge=1,
        le=50,
        description="Maximum number of eager loaded relations"
    )

    # Model settings
    DEFAULT_PER_PAGE: int = Field(
        default=25,
        ge=1,
        le=100,
        description="Default pagination size"
    )
    PARANOID_MODE: bool = Field(
        default=True,
        description="Enable soft deletes"
    )

    # Validation settings
    RAISE_ON_VALIDATION_ERROR: bool = Field(
        default=False,
        description="Raise exception on validation errors"
    )

    @field_validator("DATABASE_URL")
    def validate_database_url(cls, v):
        valid_prefixes = ("sqlite:///", "postgresql://", "mysql://")
        if not any(v.startswith(prefix) for prefix in valid_prefixes):
            raise ValueError("Invalid database URL scheme")
        return v

    @field_validator("CACHE_REDIS_URL")
    def validate_redis_url(cls, v, values):
        if values.get("CACHE_TYPE") == "redis":
            if not v.startswith("redis://"):
                raise ValueError("Invalid Redis URL scheme")
        return v

    class Config:
        env_prefix = "FR_"
        case_sensitive = True
        env_file = ".env"


@lru_cache()
def get_settings() -> FastRecordSettings:
    """Get the application settings"""
    return FastRecordSettings()


def configure(**kwargs):
    """Configure FastRecord with custom settings"""
    settings = get_settings()

    for key, value in kwargs.items():
        if hasattr(settings, key):
            setattr(settings, key, value)

    # Set up database connection
    setup_database(
        settings.DATABASE_URL,
        echo=settings.DATABASE_ECHO,
        pool_size=settings.DATABASE_POOL_SIZE,
        max_overflow=settings.DATABASE_MAX_OVERFLOW,
        pool_timeout=settings.DATABASE_POOL_TIMEOUT
    )
